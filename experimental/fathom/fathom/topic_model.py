import logging
import numpy as np
import os
import time

from datetime import datetime
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

from db import TmplDB
from settings import MODELS_DIR
from utils import loadObject
from utils import makeDir
from utils import saveObject
from utils import stringToFile

# TODO: If user chooses tfidf and LDA, use tfidf to filter words first,
# TODO: then use LDA. As of now, LDA does not support the output format
# of tfidf.


class TopicModel(object):
    """
    Class to train Tmpl topic models using NMF or LDA.

    Usage:
        This class is meant to make running Tmpl topic models easier for
        you, the user. It uses two of Scikit-learn's
        matrix decomposition classes (which are fairly specific to
        topic modeling problems), NMF (Non-negative Matrix Factorization) and
        LDA (Latent Dirichlet Allocation) for the actual topic model training.

        Instantiating a TopicModel object:

        The only required positional argument for a TopicModel object
        is a Reader object that gives your TopicModel object an interface
        to read the corpus in. A general workflow is to first instantiate
        a reader (see reader.py for examples on how to do this) and then
        pass in a reader to your TopicModel.

        The rest of the TopicModel constructor arguments are various
        configurations and hyperparameters.

        Example:
            reader = Reader(directory='/path/to/pre-parsed/corpus')
            model = TopicModel(reader)

        OR if you want to parse the corpus dynamically
        (see reader.py for more information on this):
            parser = Parser(directory='path/to/raw-xml/proceedings')
            reader = Reader(parser=parser)
            model = TopicModel(reader)

        Training your TopicModel:

        To train your TopicModel (which really just calls Scikit-learn's
        internal models), call the TopicModel.train() method:

            # considering we have already instantiated a TopicModel as in
            # the example above
            model.train()

        Saving your TopicModel:

        Great, now we've got a trained TopicModel object that stored in
        memory; but wait, this will only be available and present while
        our program is running! We want to be able to persist our
        TopicModels. To save your TopicModel -- which as of the current
        design, means pickling your entire TopicModel instance (to save it's
        state in a straightforward way) to a file, instantiating and
        writing metadata and training output to a sqlite3 database (which
        is really just a local file), and generating a human-readable
        high-level summary file describing the results of your model, run
        the following:

            model.save()

        TmplDB storage:

        The metadata and output from the trained model will be stored
        dynamically (as they are read in / computed) in a TmplDB instance
        that is instantiated (one per TopicModel instance) when you
        instantiate a TopicModel object.

        See main.py for a complete example of how to use a TopicModel class.

    Args:
        reader: Reader object that gives the TopicModel instance an interface
            to read in your corpus. We have a pre-built Reader class in
            reader.py but in reality, you could provide your own Reader class.
            The only requirement is that is has a method, 'read()' that
            yields fulltexts paired with their respective metadata objects in
            a tuple like such (fulltext, meta). There are some other more
            specific implicit requirements (for instance, we expect a 'meta'
            to have a 'title' field but you can easily look through the code
            to figure out those requirements)
        vectorizerType: a string denoting the type of Scikit-learn vectorizer
            to use. See TopicModel.VALID_VECTORIZER_TYPES for the set of
            valid vectorizer type strings to use.
        modelType: a string denoting the type of Scikit-learn model to use. See
            TopicModel.VALID_MODEL_TYPES for the set of valid model types. As
            of now, only LDA and NMF are available.
        noTopics: the number of topics to infer in your model. This corresponds
            to the 'n_components' parameter in the Scikit-learn models.
        noFeatures: the upperbound on the number of features (number of words)
            to use when training your model. This corresponds to the
            'max_features' parameter in the Scikit-learn vectorizers.
        maxIter: the maximum number of iterations to use in training. This
            corresponds to the maximum iterations that Scikit-learn will use
            to fit a model. As of now, it seems like the default value, 10,
            works pretty well for training a topic model over papers from the
            Big 4 PL conferences (POPL, PLDI, OOPSLA, ICFP) ~4000 documents.
            However, you may need to play around with this to get optimal
            convergence.
        name: a unique name to give your TopicModel instance. If not specified,
            a unique name will be generated by the TopicModel._uniqueName()
            method.
    """
    # Default constructor arguments
    DEFAULT_OUTPUT_DIR = '.'

    # Valid vectorizer types.
    TFIDF_VECTORIZER = 'tfidf'
    COUNT_VECTORIZER = 'count'
    VALID_VECTORIZER_TYPES = {TFIDF_VECTORIZER, COUNT_VECTORIZER}

    # Valid model types.
    NMF = 'nmf'
    LDA = 'lda'
    VALID_MODEL_TYPES = {NMF, LDA}

    # Scikit-learn verbosity level (0-10: higher values = more verbose logging).
    SCIKIT_LEARN_VERBOSITY = 0

    # Filenames to save models to
    MODEL_FILENAME = 'model.pkl'
    SUMMARY_FILENAME = 'summary.txt'
    DATABASE_FILENAME = 'db.sqlite3'

    def __init__(self, reader, vectorizerType=TFIDF_VECTORIZER, modelType=NMF,
                 noTopics=20, noFeatures=1000, maxIter=None, name=None,
                 parentLogger=None):

        # Save timestamp of when model was instantiated to help uniquely
        # identify this model (not perfect but works).
        self._timestamp = datetime.now().isoformat()

        if parentLogger:
            self.logger = parentLogger.getChild('TopicModel')
        else:
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger('TopicModel')

        # Check that user passed in valid vectorizer types, model types values.
        if vectorizerType not in self.VALID_VECTORIZER_TYPES:
            raise ValueError(
                (
                    'Invalid "vectorizerType". '
                    'Valid vectorizers are {valid_vectorizers}.'
                ).format(
                    valid_vectorizers=self.VALID_VECTORIZER_TYPES
                )
            )
        if modelType not in self.VALID_MODEL_TYPES:
            raise ValueError(
                'Invalid "modelType". Valid models are {valid_models}.'.format(
                valid_models=self.VALID_MODEL_TYPES
                )
            )

        # Set default maxIter (it differs depending on the model).
        if maxIter is None:
            if modelType == self.NMF:
                maxIter = 200
            elif modelType == self.LDA:
                maxIter = 10

        # Initialize instance variables.
        self.reader = reader
        self.vectorizerType = vectorizerType
        self.modelType = modelType
        self.noTopics = noTopics
        self.noFeatures = noFeatures
        self.maxIter = maxIter

        # Set some 'private' instance variables that will be set later on.
        self._documents, self._metas = None, None
        self._trained = False
        self._vectorizer = None
        self._model = None
        self._feature_names = None
        self._DTMatrix = None
        self._W = None
        self._H = None
        self._savedModelPath = None
        self._summaryFilePath = None

        # Generate unique name if user doesn't pass in name
        self.name = name or self._uniqueName()

        # Output dir to save model to.
        self.outputDir = os.path.join(MODELS_DIR, self.name)

        # Make necessary directories if they don't already exist.
        makeDir(MODELS_DIR)
        makeDir(self.outputDir)
        self.logger.info(
            (
                'Created directory at {outputDir} '
                'to save model output files to.'
            ).format(outputDir=self.outputDir)
        )

        # Instantiate database and pass along to reader, too.
        self.db = TmplDB(os.path.join(self.outputDir, self.DATABASE_FILENAME))
        self.reader.setDB(self.db)

        # Init some other variables that will be set after training the model.
        self.trainedModel = None  # Trained Scikit-learned model.
        self.vectorizingTime = None  # Time to vectorize (in seconds)
        self.trainingTime = None  # Training time (in seconds).

    @property
    def vectorizer(self):
        """
        Scikit-learn vectorizer object for vectorizing corpus (converting
        corpus into a bag-of-words matrix).

        Returns:
            Scikit-learn.feature_extractino.text vectorizer object.
        """
        if self._vectorizer is None:
            if self.vectorizerType == self.TFIDF_VECTORIZER:
                self._vectorizer = TfidfVectorizer(
                    max_df=0.95,  # Removes words appearing in > 95% of docs.
                    # min_df=2,  # Only keep words appearing in at least 2 docs.
                    max_features=self.noFeatures,
                    stop_words='english',
                    ngram_range=(1, 2),
                    decode_error='ignore'  # Just ignore weird chars in corpus.
                )
            elif self.vectorizerType == self.COUNT_VECTORIZER:
                self._vectorizer = CountVectorizer(
                    max_df=0.95,  # Removes words appearing in > 95% of docs.
                    # min_df=2,  # Only keep words appearing in at least 2 docs.
                    max_features=self.noFeatures,
                    stop_words='english',
                    ngram_range=(1, 2),
                    decode_error='ignore'  # Just ignore weird chars in corpus.
                )
            else:
                raise ValueError("Invalid vectorizer type.")
        return self._vectorizer

    @property
    def model(self):
        """
        Scikit-learn model responsible for internal training of topic models.

        Returns:
            Scikit-learn.decompositions model object.
        """
        if self._model is None:
            if self.modelType == self.NMF:
                self._model = NMF(
                    n_components=self.noTopics,
                    max_iter=self.maxIter,
                    random_state=1,
                    alpha=.1,
                    l1_ratio=.5,
                    init='nndsvd',
                    verbose=self.SCIKIT_LEARN_VERBOSITY
                )
            elif self.modelType == self.LDA:
                self._model = LatentDirichletAllocation(
                    n_components=self.noTopics,
                    max_iter=self.maxIter,
                    learning_method='online',
                    learning_offset=50.,
                    random_state=0,
                    verbose=self.SCIKIT_LEARN_VERBOSITY
                )
            else:  # Not a legal model type.
                raise ValueError("Invalid model type.")
        return self._model

    @property
    def documents(self):
        """
        List of documents in corpus.

        Returns:
            List of document fulltexts. Co-indexed with metas.
                eg. fulltexts[i] corresponds to metas[i]
        """
        if self._documents is None:
            (self._documents, self._metas) = zip(*list(self.reader.read()))
        return self._documents

    @property
    def metas(self):
        """
        List of metadatas corresponding to fulltexts in corpus.

        Returns:
            List of document metas. Co-indexed with fulltexts.
                eg. metas[i] corresponds to fulltexts[i]
        """
        if self._metas is None:
            (self._documents, self._metas) = zip*(list(self.reader.read()))
        return self._metas

    @property
    def savedModelPath(self):
        """
        Path to pickled TopicModel instance.

        Returns:
            List of document metas. Co-indexed with fulltexts.
                eg. metas[i] corresponds to fulltexts[i]
        """
        if self._savedModelPath is None:
            self._savedModelPath = os.path.join(self.outputDir,
                                                self.MODEL_FILENAME)
        return self._savedModelPath

    @property
    def summaryFilePath(self):
        """
        Path to human-readable trained model summary.

        Returns:
            Filepath to summary file.
        """
        if self._summaryFilePath is None:
            self._summaryFilePath = os.path.join(self.outputDir,
                                                 self.SUMMARY_FILENAME)
        return self._summaryFilePath

    def _uniqueName(self):
        """Creates a unique name to identify the model."""
        return (
            (
                '{modelType}_{vectorizerType}v_{noTopics}'
                'n_{noFeatures}f_{maxIter}i_{timestamp}'
            ).format(
                modelType=self.modelType,
                vectorizerType=self.vectorizerType,
                noTopics=self.noTopics,
                noFeatures=self.noFeatures,
                maxIter=self.maxIter,
                timestamp=self._timestamp,
            )
        )

    def train(self):
        """
        Trains the desired model. Saves trained model in the
        'model' instance variable.
        """

        # fit_transform learns a vocabulary for the corpus and
        # returns the transformed term-document matrix.
        # TODO: Sklearn doesn't have verbose logging for its vectorizers
        # so let user know whats going on.
        documents = self.documents

        self.logger.info('Vectorizing corpus...')
        start = time.clock()
        vectorized = self.vectorizer.fit_transform(documents)
        end = time.clock()

        # Save document-term matrix for later use.
        self._DTMatrix = vectorized

        self.vectorizingTime = end - start

        # Save dictionary mapping ids to words.
        self._feature_names = self.vectorizer.get_feature_names()

        self.logger.info(
            (
                'Training {modelType} model with {noDocuments} documents '
                'with {vectorizerType} vectorizer, '
                '{noTopics} topics, {noFeatures} features, '
                'and {maxIter} max iterations.'
            ).format(
                modelType=self.modelType,
                noDocuments=len(self.documents),
                vectorizerType=self.vectorizerType,
                noTopics=self.noTopics,
                noFeatures=self.noFeatures,
                maxIter=self.maxIter,
            )
        )

        # Train and set model to newly trained model.
        start = time.clock()
        self.trainedModel = self.model.fit(vectorized)
        end = time.clock()
        self.trainingTime = end - start

        # Save the topic-to-documents matrix. Essentially, we are
        # using the model we just trained to convert our document-term matrix
        # corpus into a document-topic matrix based on the term frequencies
        # for each document in the matrix.
        self._W = self.model.transform(vectorized)

        # Save the word-to-topic matrix. This is what the model
        # learns using the corpus.
        self._H = self.model.components_

        self._trained = True

        logging.info(
            (
                'Done training. Vectorizing time: {vectorizingTime}s. '
                'Training time: {trainingTime}s'
            ).format(
                vectorizingTime=self.vectorizingTime,
                trainingTime=self.trainingTime,
            )
        )

        # Insert paper topic scores into db.
        self.insertPaperScores()
        self.insertModel()
        return

    def topWords(self, n):
        """
        Finds and returns the top n words per topic for the trained model.

        Args:
            n: Number of top words to find for each topic.

        Returns:
            A list of lists of the top n words for each topic
            (where the topic number corresponds to the index of the outer list).
        """
        if not self._trained:
            raise ValueError(
                'Cannot fetch top words for untrained model. '
                'Call model.train() first.'
            )

        result = []
        for topic in self._H:
            topWordsIx = topic.argsort()[:-n - 1:-1]
            result.append([self._feature_names[i] for i in topWordsIx])
        return result

    def topPapers(self, n):
        """
        Finds and returns the top n papers per topic for the trained model.

        Args:
            n: Number of top papers to find for each topic.

        Returns:
            A list of lists of the top n papers' titles for each topic
            (where the topic number corresponds to the index of the outer list).
        """
        if not self._trained:
            raise ValueError(
                'Cannot fetch top words for untrained model. '
                'Call model.train() first.'
            )

        result = []
        for topic_id, _ in enumerate(self._H):
            topDocIx = np.argsort(self._W[:, topic_id])[::-1][0:n]
            result.append([self._metas[i]['title'] for i in topDocIx])
        return result

    def insertPaperScores(self):
        """Inserts paper topic vectors into TmplDB instance."""
        if not self._trained or self._W is None:
            raise ValueError(
                'Cannot call insertPapers() with an untrained model. '
                'Call model.train() first.'
            )
        for i, paper in enumerate(self._W):
            meta = self.metas[i]
            papers = []
            for topic_id, score in enumerate(paper):
                papers.append((meta['article_id'], topic_id, self.name, score))
            self.db.insertScores(*papers)

    def insertModel(self):
        """Inserts model data into TmplDB instance."""
        if not self._trained:
            raise ValueError(
                'Cannot call insertModel() with an '
                'untrained model. Call model.train() first.'
            )

        modelData = (
            self.name,
            self.savedModelPath,
            self._timestamp,
            self.noTopics,
            self.noFeatures,
            self.maxIter,
            self.vectorizerType,
            self.modelType,
        )
        self.db.insertModels(modelData)

    def save(self):
        """
        Saves the trained TopicModel object to the output path.
        Called automatically in the train() method
        if instance variable 'save' is set to True.
        Can also call manually with desired path.
        """
        if not self._trained:
            self.logger.warning(
                ('You are saving an untrained model. '
                 'Call model.train() to train.')
            )

        self.logger.info('Saving pickled trained model and summary.')
        saveObject(self, self.savedModelPath)
        stringToFile(self.summary(), self.summaryFilePath)
        self.logger.info(
            (
                'Successfully saved trained model and summary {outputDir}'
            ).format(
                outputDir=self.outputDir
            )
        )

    @staticmethod
    def load(path):
        """
        Loads a TopicModel object from disk and returns it.

        Args:
            path: path to persisted model to be loaded.

        Returns: the desired TopicModel object; the trained sklearn model is
            stored in the trainedModel attribute.
        """
        return loadObject(path)

    # TODO: LDA model toString spits out the same papers for all topics for
    # tfidf.
    # Only works when using the count vectorizer.
    def summary(self, noWords=10, noPapers=10):
        if not self._trained:
            output = (
                '<TopicModel: '
                'Untrained {modelType} model with {noTopics} topics, '
                '{noFeatures} features, and {maxIter} maximum iterations '
                'using a {vectorizerType} vectorizer>').format(
                    modelType=self.modelType,
                    noTopics=self.noTopics,
                    noFeatures=self.noFeatures,
                    maxIter=self.maxIter,
                    vectorizerType=self.vectorizerType,
            )
        else:
            output = ''
            header = (
                'Trained {modelType} model over {noDocuments} documents '
                'with {vectorizerType} vectorizer, '
                '{noTopics} topics, {noFeatures} features, '
                'and {maxIter} maximum iterations. '
                'Vectorizing time: {vectorizingTime}s. '
                'Training time: {trainingTime}s.').format(
                    modelType=self.modelType,
                    noDocuments=len(self.documents),
                    vectorizerType=self.vectorizerType,
                    noTopics=self.noTopics,
                    noFeatures=self.noFeatures,
                    maxIter=self.maxIter,
                    vectorizingTime=self.vectorizingTime,
                    trainingTime=self.trainingTime,
                )
            output += header
            output += '\n'
            for topic_id, topic in enumerate(self._H):
                output += '---------- Topic {topic_id} ----------'.format(
                    topic_id=topic_id
                    )
                output += '\n'
                output += '*** Top words ***'
                output += '\n'
                topWordsIx = topic.argsort()[:-noWords - 1:-1]
                output += '\n'.join(
                    [self._feature_names[i] for i in topWordsIx]
                )
                output += '\n\n'
                output += '*** Top papers ***'
                output += '\n'
                topDocIx = np.argsort(self._W[:, topic_id])[::-1][0:noPapers]
                output += '\n'.join(
                    [self._metas[i]['title'] for i in topDocIx]
                )
                output += '\n\n'
        return output
