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

from settings import MODELS_DIR
from reader import JsonFileReader
from utils import makeDir
from utils import stringToFile

# TODO: If user chooses tfidf and LDA, use tfidf to filter words first, then use LDA.


class TopicModel(object):

    # Valid vectorizer types.
    TFIDF_VECTORIZER = 'tfidf'
    COUNT_VECTORIZER = 'count'
    VALID_VECTORIZER_TYPES = {TFIDF_VECTORIZER, COUNT_VECTORIZER}

    # Valid model types.
    NMF = 'nmf'
    LDA = 'lda'
    VALID_MODEL_TYPES = {NMF, LDA}

    # Scikit-learn verbosity level (higher values = more verbose logging).
    SCIKIT_LEARN_VERBOSITY = 5

    def __init__(self, corpus, vectorizerType=TFIDF_VECTORIZER, modelType=NMF, noTopics=20, noFeatures=1000,
                 maxIter=None):

        # Check arguments.
        if vectorizerType not in self.VALID_VECTORIZER_TYPES:
            raise ValueError('Invalid vectorizer type. Valid vectorizers are {valid_vectorizers}.'.format(
                valid_vectorizers=self.VALID_VECTORIZER_TYPES
                )
            )

        if modelType not in self.VALID_MODEL_TYPES:
            raise ValueError('Invalid model type. Valid models are {valid_models}.'.format(
                valid_models=self.VALID_MODEL_TYPES
                )
            )

        # Set default maxIter (it differs depending on the model).
        if maxIter is None:
            if modelType == self.NMF:
                maxIter = 200
            elif modelType == self.LDA:
                maxIter = 10

        self.corpus = corpus
        self.vectorizerType = vectorizerType
        self.modelType = modelType
        self.noTopics = noTopics
        self.noFeatures = noFeatures
        self.maxIter = maxIter

        # Set some 'private' instance variables for internal use.
        (self._documents, self._metas) = self.corpus
        self._dirName = None
        self._trained = False
        self._vectorizer = None
        self._model = None
        self._feature_names = None
        self._W = None
        self._H = None

        self.trainedModel = None  # Trained model is stored here.
        self.trainingTime = None  # Store the time it took to train model here.

    @property
    def vectorizer(self):
        if self._vectorizer is None:
            if self.vectorizerType == self.TFIDF_VECTORIZER:
                self._vectorizer = TfidfVectorizer(max_df=0.95,  # Removes words appearing in > 95% of documents.
                                                   min_df=2,  # Removes words only appearing in 1 document.
                                                   max_features=self.noFeatures, 
                                                   stop_words='english',
                                                   ngram_range=(1, 2),  # Collect single words and bi-grams (two words).
                                                   decode_error='ignore')  # Ignore encoding errors.
            elif self.vectorizerType == self.COUNT_VECTORIZER:
                self._vectorizer = CountVectorizer(max_df=0.95,  # Removes words appearing in > 95% of documents.
                                                   min_df=2,  # Removes words only appearing in 1 document.
                                                   max_features=self.noFeatures, 
                                                   stop_words='english',
                                                   ngram_range=(1, 2),  # Collect single words and bi-grams (two words).
                                                   decode_error='ignore')  # Ignore encoding errors.
            else: # Not a legal vectorizer type.
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
    def dirName(self):
        """Builds a directory name representing the model."""
        if self._dirName is None:
            self._dirName = ('{modelType}_{vectorizerType}v_{noTopics}n_{noFeatures}f_{maxIter}i'.format(
                modelType=self.modelType,
                vectorizerType=self.vectorizerType,
                noTopics=self.noTopics,
                noFeatures=self.noFeatures,
                maxIter=self.maxIter if self.modelType == 'lda' else 'default',
            ))
        return self._dirName

    def train(self):
        """Trains the desired model. Saves trained model in the
        'model' instance variable.
        """
        # Unpack corpus.
        (documents, metas) = (self._documents, self._metas)

        # fit_transform learns a vocabulary for the corpus and 
        # returns the transformed term-document matrix.
        vectorized = self.vectorizer.fit_transform(documents)

        print vectorized

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
        return

    def persist(self, path):
        """Saves the trained TopicModel object to the output path.
        """
        if not self._trained:
            raise ValueError('Cannot persist an untrained model. Call model.train() first.')
        joblib.dump(self, path)

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
    def toString(self, noWords=10, noPapers=10):
        if not self._trained:
            output = ('<TopicModel: '
                      'Untrained {modelType} model with {noTopics} topics, '
                      '{noFeatures} features, and {maxIter} maximum iterations '
                      'using a {vectorizerType} vectorizer>').format(
                            modelType=self.modelType,
                            noTopics=self.noTopics,
                            noFeatures=self.noFeatures,
                            maxIter=self.maxIter if self.modelType == 'lda' else 'default',
                            vectorizerType=self.vectorizerType,
                        )
        else:
            output = ''
            header = ('Trained {modelType} model '
                      'with {vectorizerType} vectorizer, {noTopics} topics, {noFeatures} features, \n'
                      'and {maxIter} max iterations (lda only). \nTraining time: {trainingTime}s').format(
                          modelType=self.modelType,
                          vectorizerType=self.vectorizerType,
                          noTopics=self.noTopics,
                          noFeatures=self.noFeatures,
                          maxIter=self.maxIter if self.modelType == 'lda' else 'default',
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
    parser.add_argument('-t', '--type', dest='type',
                        choices={'lda', 'nmf'}, default='nmf', type=str,
                        help='The type of model to train (lda or nmf). Defaults to nmf.')
    parser.add_argument('-n', '--num_topics', dest='num_topics',
                        default=20, type=int,
                        help='The number of topics you want the model to find.')
    parser.add_argument('-f', '--num_features', dest='num_features',
                        default=1000, type=int,
                        help='The number of features (unique word tokens) you want the model to use.')
    parser.add_argument('-v', '--v', dest='vectorizer_type',
                        choices={'count', 'tfidf'}, default='count', type=str,
                        help='''The type of word vectorizer to use (count or tfidf). \
                        As of now, LDA only supports using the count vectorizer.''')
    parser.add_argument('-i', '--max_iter', dest='max_iter',
                        default=None, type=int,
                        help='The maximum number of training iterations to run.')

    args = parser.parse_args()

    pathToCorpus = args.corpus
    modelType = args.type
    vectorizerType = args.vectorizer_type
    noTopics = args.num_topics
    noFeatures = args.num_features
    maxIter = args.max_iter

    if 'abs' in pathToCorpus:
        corpus = JsonFileReader.loadAllAbstracts(pathToCorpus)
    elif 'fulltext' in pathToCorpus:
        corpus = JsonFileReader.loadAllFullTexts(pathToCorpus)
    else:
        raise ValueError('Invalid corpus path.')

    # Instantiate TopicModel object with desired parameters.
    model = TopicModel(corpus,
                       modelType=modelType,
                       vectorizerType=vectorizerType,
                       noTopics=noTopics,
                       noFeatures=noFeatures,
                       maxIter=maxIter)

    # Make current model's dir to persist it to.
    modelDir = os.path.join(MODELS_DIR, model.dirName + '_' + datetime.now().isoformat())
    modelFilePath = os.path.join(modelDir, 'model.pkl')
    summaryFilePath = os.path.join(modelDir, 'summary.txt')
    makeDir(MODELS_DIR)  # Make the shared archive models dir if needed.
    makeDir(modelDir)  # Make the current model's dir.

    logging.info(
        (
            'Training {modelType} model over {pathToCorpus} corpus ' 
            'with {vectorizerType} vectorizer, {noTopics} topics, {noFeatures} features, '
            'and {maxIter} max iterations (lda only).'
        ).format(
            modelType=modelType,
            pathToCorpus=pathToCorpus,
            vectorizerType=vectorizerType,
            noTopics=noTopics,
            noFeatures=noFeatures,
            maxIter=maxIter or 'default',
        )
    )

    # Train the model; training time is saved in model.trainingTime attribute.
    model.train()
    logging.info('Done training. Took {trainingTime}s'.format(trainingTime=model.trainingTime))
    logging.info('Saving trained model and summary to {outputDir}'.format(outputDir=model.dirName))
    model.persist(modelFilePath)
    stringToFile(model.toString(), summaryFilePath)
