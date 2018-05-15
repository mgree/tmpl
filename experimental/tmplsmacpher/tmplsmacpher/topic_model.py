import logging
import numpy as np
import os
import time

from datetime import datetime
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.decomposition import NMF
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

from db import TmplDB
from settings import MODELS_DIR
from utils import loadObject
from utils import makeDir
from utils import saveObject
from utils import stringToFile

# TODO: If user chooses tfidf and LDA, use tfidf to filter words first,
# TODO: then use LDA. As of now, LDA does not support the output format of tfidf.


class TopicModel(object):
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

    # Scikit-learn verbosity level (0 - 10: higher values = more verbose logging).
    SCIKIT_LEARN_VERBOSITY = 1

    # Filenames to save models to
    MODEL_FILENAME = 'model.pkl'
    SUMMARY_FILENAME = 'summary.txt'
    DATABASE_FILENAME = 'db.sqlite3'

    def __init__(self, reader, vectorizerType=TFIDF_VECTORIZER, modelType=NMF, noTopics=20, noFeatures=1000,
                 maxIter=None, name=None):

        # Initialize logger
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('TopicModel')

        # Check that user passed in valid vectorizer types, model types values.
        if vectorizerType not in self.VALID_VECTORIZER_TYPES:
            raise ValueError('Invalid "vectorizerType". Valid vectorizers are {valid_vectorizers}.'.format(
                valid_vectorizers=self.VALID_VECTORIZER_TYPES
                )
            )
        if modelType not in self.VALID_MODEL_TYPES:
            raise ValueError('Invalid "modelType". Valid models are {valid_models}.'.format(
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
        self._timestamp = None

        # Generate unique name if user doesn't pass in name
        self.name = name or self.uniqueName()

        # Output dir to save model to.
        self.outputDir = os.path.join(MODELS_DIR, self.name)

        # Make necessary directories if they don't already exist.
        makeDir(MODELS_DIR)
        makeDir(self.outputDir)
        self.logger.info('Created directory at {outputDir} to save model output files to.'.format(outputDir=self.outputDir))

        # Instantiate database and pass along to reader, too.
        self.db = TmplDB(os.path.join(self.outputDir, self.DATABASE_FILENAME))
        self.reader.setDB(self.db)

        # Initialize some other variables that will be set after training the model.
        self.trainedModel = None  # Trained model is stored here.
        self.vectorizingTime = None  # Store the time it took to vectorize corpus here.
        self.trainingTime = None  # Store the time it took to train model here.

    @property
    def vectorizer(self):
        if self._vectorizer is None:
            if self.vectorizerType == self.TFIDF_VECTORIZER:
                self._vectorizer = TfidfVectorizer(max_df=0.95,  # Removes words appearing in > 95% of documents.
                                                   # min_df=2,  # Removes words only appearing in 1 document.
                                                   max_features=self.noFeatures,
                                                   stop_words='english',
                                                   ngram_range=(1, 2),  # Collect single words and bi-grams (two words).
                                                   decode_error='ignore')  # Ignore weird chars in corpus.
            elif self.vectorizerType == self.COUNT_VECTORIZER:
                self._vectorizer = CountVectorizer(max_df=0.95,  # Removes words appearing in > 95% of documents.
                                                   # min_df=2,  # Removes words only appearing in 1 document.
                                                   max_features=self.noFeatures,
                                                   stop_words='english',
                                                   ngram_range=(1, 2),  # Collect single words and bi-grams (two words).
                                                   decode_error='ignore')  # Ignore weird chars in corpus.
            else:
                raise ValueError("Invalid vectorizer type.")
        return self._vectorizer

    @property
    def model(self):
        if self._model is None:
            if self.modelType == self.NMF:
                self._model = NMF(n_components=self.noTopics,
                                  max_iter=self.maxIter,
                                  random_state=1,
                                  alpha=.1,
                                  l1_ratio=.5,
                                  init='nndsvd',
                                  verbose=self.SCIKIT_LEARN_VERBOSITY)
            elif self.modelType == self.LDA:
                self._model = LatentDirichletAllocation(n_components=self.noTopics, 
                                                        max_iter=self.maxIter, 
                                                        learning_method='online', 
                                                        learning_offset=50.,
                                                        random_state=0,
                                                        verbose=self.SCIKIT_LEARN_VERBOSITY)
            else:  # Not a legal model type.
                raise ValueError("Invalid model type.")
        return self._model

    @property
    def documents(self):
        if self._documents is None:
            (self._documents, self._metas) = zip(*list(self.reader.read()))
        return self._documents

    @property
    def metas(self):
        if self._metas is None:
            (self._documents, self._metas) = zip*(list(self.reader.read()))
        return self._metas

    @property
    def savedModelPath(self):
        if self._savedModelPath is None:
            self._savedModelPath = os.path.join(self.outputDir, self.MODEL_FILENAME)
        return self._savedModelPath

    @property
    def summaryFilePath(self):
        if self._summaryFilePath is None:
            self._summaryFilePath = os.path.join(self.outputDir, self.SUMMARY_FILENAME)
        return self._summaryFilePath

    @property
    def timestamp(self):
        if self._timestamp is None:
            self._timestamp = datetime.now().isoformat()
        return self._timestamp

    def uniqueName(self):
        """Creates a unique name representing the model if uniqueName is None."""
        return ('{modelType}_{vectorizerType}v_{noTopics}n_{noFeatures}f_{maxIter}i_{timestamp}'.format(
            modelType=self.modelType,
            vectorizerType=self.vectorizerType,
            noTopics=self.noTopics,
            noFeatures=self.noFeatures,
            maxIter=self.maxIter,
            timestamp=self.timestamp,
        ))

    def train(self):
        """Trains the desired model. Saves trained model in the
        'model' instance variable.
        """
        # Unpack corpus.
        (documents, metas) = (self.documents, self.metas)

        # fit_transform learns a vocabulary for the corpus and 
        # returns the transformed term-document matrix.
        # Sklearn doesn't have verbose logging for its vectorizers so let user know whats going on.
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
                'with {vectorizerType} vectorizer, {noTopics} topics, {noFeatures} features, '
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
        # Train and set model to newly trained model. Also save the training time for metric purposes.
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

        logging.info('Done training. Vectorizing time: {vectorizingTime}s. Training time: {trainingTime}s'.format(
            vectorizingTime=self.vectorizingTime,
            trainingTime=self.trainingTime,
            )
        )

        # Insert paper topic scores into db.
        self.insertPaperScores()
        self.insertModel()
        return

    def topWords(self, n):
        """Finds and returns the top n words per topic for the trained model.

        Args:
            n: Number of top words to find for each topic.

        Returns:
            A list of lists of the top n words for each topic (where the topic number
            corresponds to the index of the outer list).
        """
        if not self._trained:
            raise ValueError('Cannot fetch top words for untrained model. Call model.train() first.')

        result = []
        for topic in self._H:
            topWordsIx = topic.argsort()[:-n - 1:-1]
            result.append([self._feature_names[i] for i in topWordsIx])
        return result

    def topPapers(self, n):
        """Finds and returns the top n papers per topic for the trained model.

        Args:
            n: Number of top papers to find for each topic.

        Returns:
            A list of lists of the top n papers' titles for each topic (where the topic number
            corresponds to the index of the outer list).
        """
        if not self._trained:
            raise ValueError('Cannot fetch top words for untrained model. Call model.train() first.')

        result = []
        for topic_id, _ in enumerate(self._H):
            topDocIx = np.argsort(self._W[:, topic_id])[::-1][0:n]
            result.append([self._metas[i]['title'] for i in topDocIx])
        return result

    def save(self):
        """Saves the trained TopicModel object to the output path. Called automatically in the train() method
        if instance variable 'save' is set to True. Can also call manually with desired path.
        """
        if not self._trained:
            self.logger.warning('You are saving an untrained model. Call model.train() to train.')

        self.logger.info('Saving pickled trained model and summary.')
        self.db.connection.close()
        joblib.dump(self, self.savedModelPath)
        stringToFile(self.summary(), self.summaryFilePath)
        self.logger.info('Successfully saved trained model and summary {outputDir}'.format(
            outputDir=self.outputDir
            )
        )

    def insertPaperScores(self):
        """Inserts paper topic vectors into TmplDB instance."""
        if not self._trained or self._W is None:
            raise ValueError('Cannot call insertPapers() with an untrained model. Call model.train() first.')
        for i, paper in enumerate(self._W):
            meta = self.metas[i]
            papers = []
            for topic_id, score in enumerate(paper):
                papers.append((meta['article_id'], topic_id, self.name, score))
            self.db.insertScores(*papers)

    def insertModel(self):
        """Inserts model data into TmplDB instance."""
        if not self._trained:
            raise ValueError('Cannot call insertModel() with an untrained model. Call model.train() first.')

        modelData = (
            self.name,
            self.savedModelPath,
            self.timestamp,
            self.noTopics,
            self.noFeatures,
            self.maxIter,
            self.vectorizerType,
            self.modelType,
        )
        self.db.insertModels(modelData)

    @staticmethod
    def load(path):
        """Loads a TopicModel object from disk and returns it.

        Args:
            path: path to persisted model to be loaded.

        Returns: the desired TopicModel object; the trained sklearn model is stored
            in the trainedModel attribute.
        """
        return loadObject(path)

    # TODO: LDA model toString spits out the same papers for all topics for tfidf.
    # Only works when using the count vectorizer.
    def summary(self, noWords=10, noPapers=10):
        if not self._trained:
            output = ('<TopicModel: '
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
                'with {vectorizerType} vectorizer, {noTopics} topics, {noFeatures} features, '
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
