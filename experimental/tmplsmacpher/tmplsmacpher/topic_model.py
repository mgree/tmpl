import logging
import numpy as np
import os
import time

from argparse import ArgumentParser
from datetime import datetime
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

from db import TmplDB
from reader import JsonFileReader
from settings import MODELS_DIR
from utils import makeDir
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
    SCIKIT_LEARN_VERBOSITY = 10

    # Filenames to save models to
    MODEL_FILENAME = 'model.pkl'
    SUMMARY_FILENAME = 'summary.txt'
    DATABASE_FILENAME = 'db.sqlite3'

    def __init__(self, reader, vectorizerType=TFIDF_VECTORIZER, modelType=NMF, noTopics=20, noFeatures=1000,
                 maxIter=None, name=None, save=False):

        # Initialize logger
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
        # Generate unique name if user doesn't pass in name
        self.name = name or self.uniqueName()
        self.save = save

        # Output dir to save model to if save is set to True.
        self.outputDir = os.path.join(MODELS_DIR, self.name)

        # Make necessary directories if they don't already exist.
        makeDir(MODELS_DIR) if self.save else None
        makeDir(self.outputDir) if self.save else None

        # Instantiate database and pass along to reader, too.
        self.db = TmplDB(os.path.join(self.outputDir, self.DATABASE_FILENAME))
        self.reader.setDB(self.db)

        # Set some 'private' instance variables for internal use / later use.
        self._documents, self._metas = None, None
        self._trained = False
        self._vectorizer = None
        self._model = None
        self._feature_names = None
        self._DTMatrix = None
        self._W = None
        self._H = None

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
            (self._documents, self._metas) = reader.readAll()
        return self._documents

    @property
    def metas(self):
        if self._metas is None:
            (self._documents, self._metas) = reader.readAll()
        return self._metas

    def uniqueName(self):
        """Creates a unique name representing the model if uniqueName is None."""
        return ('{modelType}_{vectorizerType}v_{noTopics}n_{noFeatures}f_{maxIter}i_{timestamp}'.format(
            modelType=self.modelType,
            vectorizerType=self.vectorizerType,
            noTopics=self.noTopics,
            noFeatures=self.noFeatures,
            maxIter=self.maxIter,
            timestamp=datetime.now().isoformat(),
        ))

    def train(self):
        """Trains the desired model. Saves trained model in the
        'model' instance variable.
        """
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

        # Save to disk both the pickled TopicModel instance and its summary.
        if self.save:
            self.saveModel(os.path.join(self.outputDir, self.MODEL_FILENAME))
            stringToFile(self.summary(), os.path.join(self.outputDir, self.SUMMARY_FILENAME))
            self.insertPapers()

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

    def saveModel(self, path):
        """Saves the trained TopicModel object to the output path. Called automatically in the train() method
        if instance variable 'save' is set to True. Can also call manually with desired path.
        """
        if not self._trained:
            raise ValueError('Cannot save an untrained model. Call model.train() first.')
        joblib.dump(self, path)

    def insertPapers(self):
        """Inserts paper topic vectors into TmplDB instance."""
        for i, paper in enumerate(self._W):
            meta = self.metas[i]
            papers = []
            for topic_id, score in enumerate(paper):
                papers.append((meta['article_id'], topic_id, self.name, score))
            self.db.insertScores(*papers)

    @staticmethod
    def loadModel(path):
        """Loads a model and instantiates a TopicModel object.

        Args:
            path: path to persisted model to be loaded.

        Returns: the desired TopicModel object; the trained sklearn model is stored
            in the trainedModel attribute.
        """
        return joblib.load(path)

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
            header = ('Trained {modelType} model over {noDocuments} documents'
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


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    parser = ArgumentParser(description='Used to run LDA or NMF topic models over a corpus.',
                            epilog='Happy topic modeling!')
    parser.add_argument('corpus', type=str,
                        help='The path to the directory containing the corpus.')
    parser.add_argument('--model', '-m', dest='model',
                        choices={'lda', 'nmf'}, default='nmf', type=str,
                        help='The type of model to train (lda or nmf). Defaults to nmf.')
    parser.add_argument('--num_topics', '-n', dest='num_topics',
                        default=20, type=int,
                        help='The number of topics you want the model to find.')
    parser.add_argument('--num_features', '-f', dest='num_features',
                        default=1000, type=int,
                        help='The number of features (unique word tokens) you want the model to use.')
    parser.add_argument('--vectorizer', '-v', dest='vectorizer',
                        choices={'count', 'tfidf'}, default='count', type=str,
                        help='''The type of word vectorizer to use (count or tfidf). \
                        As of now, LDA only supports using the count vectorizer.''')
    parser.add_argument('--max_iter', '-i', dest='max_iter',
                        default=None, type=int,
                        help='The maximum number of training iterations to run.')
    parser.add_argument('--name', '-u', dest='name',
                        default=None, type=str,
                        help='Optional name to keep track of your model with.')
    args = parser.parse_args()

    pathToCorpus = args.corpus
    modelType = args.model
    vectorizerType = args.vectorizer
    noTopics = args.num_topics
    noFeatures = args.num_features
    maxIter = args.max_iter
    name = args.name

    # Set logging level.
    logging.basicConfig(level=logging.INFO)

    # Instantiate reader to pass to TopicModel to read the corpus.
    reader = JsonFileReader(pathToCorpus)

    # Instantiate TopicModel object with desired parameters.
    model = TopicModel(reader,
                       modelType=modelType,
                       vectorizerType=vectorizerType,
                       noTopics=noTopics,
                       noFeatures=noFeatures,
                       maxIter=maxIter,
                       name=name,
                       save=True)


    # Train the model; training time is saved in model.trainingTime attribute.
    model.train()

    logging.info('Done training. Vectorizing time: {vectorizingTime}s. Training time: {trainingTime}s'.format(
        vectorizingTime=model.vectorizingTime,
        trainingTime=model.trainingTime,
        )
    )
    logging.info('Saving trained model, summary, and database to {outputDir}'.format(outputDir=model.outputDir))
