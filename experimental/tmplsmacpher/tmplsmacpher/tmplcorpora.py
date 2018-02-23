"""All of the corpus objects used in tmpl live here.
"""
import os

from abc import ABCMeta
from abc import abstractmethod

from preprocess import preprocessAll
from reader import JsonFileReader
from utils import DiskCache
from utils import makeDir

from gensim.corpora import Dictionary
from gensim.corpora import MmCorpus


class BaseCorpus(object):
    """Represents a bare-bones corpus object.
    """

    __metaclass__ = ABCMeta

    CORPUS_DIR = os.path.join(os.path.dirname(__file__), '.saved_corpora')

    def __init__(self):
        # Instantiate reader for subclasses to use.
        self.reader = JsonFileReader()

        # Make directory to save corpora to.
        makeDir(BaseCorpus.CORPUS_DIR)

    @abstractmethod
    def saveMmCorpus(self):
        """Saves corpus to disk in Matrix Market format.
        """
        pass


class AbstractCorpus(BaseCorpus):
    """A gensim-compatible corpus of abstracts
    """

    CORPUS_FILENAME = 'abstract_corpus.mm'
    ID2WORD_FILENAME = 'abstract_id2word.dict'
    PATH_TO_ABS = '/Users/smacpher/clones/tmpl_venv/tmpl-data/abs/top4/'

    def __init__(self, *args, **kwargs):
        super(AbstractCorpus, self).__init__(*args, **kwargs)

    def saveMmCorpus(self):
        (rawCorpus, meta) = self.reader.loadAllAbstracts(
            AbstractCorpus.PATH_TO_ABS
        )

        # Clean and tokenize corpus (list) of raw documents (strings).
        tokenizedDocs = preprocessAll(rawCorpus)

        # Create and save dictionary (id -> word mappings).
        id2word = Dictionary(tokenizedDocs)
        id2word.save(AbstractCorpus.ID2WORD_FILENAME)

        # Convert corpus to matrix market format, serialize, and save.
        mmCorpus = [id2word.doc2bow(doc) for doc in tokenizedDocs]
        MmCorpus.serialize(
            os.path.join(BaseCorpus.CORPUS_DIR, AbstractCorpus.CORPUS_FILENAME),
            mmCorpus
        )
        return

    def loadMMCorpus(self):
        pass


class FulltextCorpus(BaseCorpus):
    """A gensim-compatible streaming corpus of fulltexts.
    """
    def __iter__(self):
        pass


