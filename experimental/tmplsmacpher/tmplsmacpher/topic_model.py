import numpy as np

from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

from reader import JsonFileReader


class TopicModel(object):

    TFIDF_VECTORIZER = 'tfidf'
    TF_VECTORIZER = 'count'

    def __init__(self, corpus, vectorizerType=TFIDF_VECTORIZER):
        self.corpus = corpus
        self.vectorizerType = vectorizerType

        self._vectorizer = None

    @property
    def vectorizer(self):
        if self._vectorizer is None:
            if vectorizerType = self.TFIDF_VECTORIZER:
                self._vectorizer = TfidfVectorizer(max_df=0.95, 
                                                   min_df=2,
                                                   max_features=no_features, 
                                                   stop_words='english')
            elif vectorizerType = self.TF_VECTORIZER:
                self._vectorizer = CountVectorizer(max_df=0.95, 
                                                   min_df=2, 
                                                   max_features=no_features, 
                                                   stop_words='english')
            else: # Not a legal vectorizer type.
                raise ValueError("Invalid vectorizer type.")
        return self._vectorizer

    def vectorize(self):
        pass

    def loadCorpus(self):
        pass

    def train(self):
        pass

    def displayTopics(self):
        pass

