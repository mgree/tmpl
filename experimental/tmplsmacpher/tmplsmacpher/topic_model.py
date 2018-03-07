import numpy as np

from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

from reader import JsonFileReader


class TopicModel(object):

    TFIDF_VECTORIZER = 'tfidf'
    TF_VECTORIZER = 'count'

    NMF = 'nmf'
    LDA = 'lda'

    def __init__(self, 
                 corpus, 
                 vectorizerType=TFIDF_VECTORIZER,
                 modelType=NMF,
                 no_topics=20,
                 no_features=1000):
        self.corpus = corpus
        self.vectorizerType = vectorizerType
        self.modelType = modelType
        self.no_topics = no_topics
        self.no_features = no_features

        self._vectorizer = None
        self._model = None
        self._W = None
        self._H = None


    @property
    def vectorizer(self):
        if self._vectorizer is None:
            if self.vectorizerType == self.TFIDF_VECTORIZER:
                self._vectorizer = TfidfVectorizer(max_df=0.95, # Removes words appearing in more than 95% of documents.
                                                   min_df=2, # Removes words only appearing in 1 document.
                                                   max_features=self.no_features, 
                                                   stop_words='english')
            elif self.vectorizerType == self.TF_VECTORIZER:
                self._vectorizer = CountVectorizer(max_df=0.95, # Removes words appearing in more than 95% of documents.
                                                   min_df=2, # Removes words only appearing in 1 document.
                                                   max_features=self.no_features, 
                                                   stop_words='english')
            else: # Not a legal vectorizer type.
                raise ValueError("Invalid vectorizer type.")
        return self._vectorizer

    @property
    def model(self):
        if self._model is None:
            if self.modelType == self.NMF:
                self._model = NMF(n_components=self.no_topics, 
                                  random_state=1,
                                  alpha=.1,
                                  l1_ratio=.5,
                                  init='nndsvd',
                                  verbose=5)
            elif self.modelType == self.LDA:
                self._model = LatentDirichletAllocation(n_components=self.no_topics, 
                                                        max_iter=5, 
                                                        learning_method='online', 
                                                        learning_offset=50.,
                                                        random_state=0,
                                                        verbose=5)
            else: # Not a legal model type.
                raise ValueError("Invalid model type.")
        return self._model

    def train(self):
        # Unpack corpus.
        (documents, metas) = self.corpus

        # fit_transform learns a vocabulary for the corpus and 
        # returns the transformed term-document matrix.
        vectorized = self._vectorizer.fit_transform(documents)

        # Set model to newly trained model.
        self.model = self.model.fit(vectorized)


        self._W = self.model.transform(vectorized)
        self._H = self.model.components_

    def displayTopics(self):
        pass

