"""All of the corpus objects used in tmpl live here.
"""
import os

from abc import ABCMeta
from preprocess import tokenizeDocuments, _tokenizeDocument
from preprocess import lemmatizeTokenLists, _lemmatizeTokenList
from preprocess import stemTokenLists, stemTokenList
from preprocess import applyRules
from reader import JsonFileReader
from utils import DiskCache

from gensim.corpora import MmCorpus

class BaseCorpus(object):
    """Represents a bare-bones corpus object.
    """

    __metaclass__ = ABCMeta

    CORPUS_DIR = os.path.join(os.path.dirname(__file__), '.saved_corpora')

    def __init__(self, corpusDir, filename, forceRerun=False):
        self.corpusDir
        self.forceRerun = forceRerun
        self.filename = filename
        self.reader = JsonFileReader()

    @abstractmethod
    def saveCorpusMM(self):
        """Saves corpus to disk in Matrix Market format.
        """
        pass


class AbstractCorpus(BaseCorpus):
    """A gensim-compatible corpus of abstracts
    """

    FILENAME = 'abstract_corpus.mm'
    PATH_TO_ABS = '/Users/smacpher/clones/tmpl_venv/tmpl-data/abs/top4/'

    def __init__(self, *args, **kwargs):
        super(AbstractCorpus, self).__init__(*args, **kwargs)

    def saveCorpusMM(self):
        rawCorpus = self.reader.loadAllAbstracts()
        MmCorpus.serialize(
            os.path.join(super.CORPUS_DIR, AbstractCorpus.FILENAME),
            corpus
        )


class FulltextCorpus(BaseCorpus):
    """A gensim-compatible streaming corpus of fulltexts.
    """
    def __iter__(self):


