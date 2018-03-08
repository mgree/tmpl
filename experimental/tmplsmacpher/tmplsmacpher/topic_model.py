import numpy as np

from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

from reader import JsonFileReader


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

    def __init__(self, 
                 corpus, 
                 vectorizerType=TFIDF_VECTORIZER,
                 modelType=NMF,
                 noTopics=20,
                 noFeatures=1000,
                 maxIter=10):

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

        self.corpus = corpus
        self.vectorizerType = vectorizerType
        self.modelType = modelType
        self.noTopics = noTopics
        self.noFeatures = noFeatures
        self.maxIter = maxIter # Only for LDA.

        # Set some 'private' instance variables for internal use.
        (self._documents, self._metas) = self.corpus
        self._trained = False
        self._vectorizer = None
        self._model = None
        self._feature_names = None
        self._W = None
        self._H = None

    @property
    def vectorizer(self):
        if self._vectorizer is None:
            if self.vectorizerType == self.TFIDF_VECTORIZER:
                self._vectorizer = TfidfVectorizer(max_df=0.95, # Removes words appearing in more than 95% of documents.
                                                   min_df=2, # Removes words only appearing in 1 document.
                                                   max_features=self.noFeatures, 
                                                   stop_words='english',
                                                   ngram_range=(1, 2)) # Collect both individual words and bigrams (two words).
            elif self.vectorizerType == self.COUNT_VECTORIZER:
                self._vectorizer = CountVectorizer(max_df=0.95, # Removes words appearing in more than 95% of documents.
                                                   min_df=2, # Removes words only appearing in 1 document.
                                                   max_features=self.noFeatures, 
                                                   stop_words='english',
                                                   ngram_range=(1, 2)) # Collect both individual words and bigrams (two words).
            else: # Not a legal vectorizer type.
                raise ValueError("Invalid vectorizer type.")
        return self._vectorizer

    @property
    def model(self):
        if self._model is None:
            if self.modelType == self.NMF:
                self._model = NMF(n_components=self.noTopics, 
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
            else: # Not a legal model type.
                raise ValueError("Invalid model type.")
        return self._model

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

        # Train and set model to newly trained model.
        model = self.model.fit(vectorized)

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

    # TODO: LDA model toString spits out the same papers for all topics.
    # Only works when using the count vectorizer.
    def toString(self, noWords=10, noPapers=10):
        if not self._trained:
            output = ('<TopicModel: '
                      'Untrained {modelType} model with {noTopics} topics and '
                      '{noFeatures} features '
                      'using a {vectorizerType} vectorizer>').format(
                            modelType=self.modelType,
                            noTopics=self.noTopics,
                            noFeatures=self.noFeatures,
                            vectorizerType=self.vectorizerType,
                        )
        else:
            output = ''
            for topic_id, topic in enumerate(self._H):
                output += '---------- Topic {topic_id} ----------'.format(
                    topic_id=topic_id
                    )
                output += '\n'
                output += '*** Top words ***'
                output +='\n'
                topWordsIndices = topic.argsort()[:-noWords -1:-1]
                output += '\n'.join([self._feature_names[i] for i in topWordsIndices])
                output += '\n\n'
                output += '*** Top papers ***'
                output +='\n'
                topDocIndices = np.argsort(self._W[:,topic_id] )[::-1][0:noPapers]
                output += '\n'.join([self._metas[i]['title'] for i in topDocIndices])
                output += '\n\n'
        return output


if __name__ == '__main__':
    pathToAbs = '/Users/smacpher/clones/tmpl_venv/tmpl-data/abs/top4/'
    corpus = JsonFileReader.loadAllAbstracts(pathToAbs, recursive=True)
    model = TopicModel(corpus, modelType=TopicModel.NMF, vectorizerType=TopicModel.TFIDF_VECTORIZER, noTopics=20, noFeatures=1000)
    model.train()
    print model.toString()

