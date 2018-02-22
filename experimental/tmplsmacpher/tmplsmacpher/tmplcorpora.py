"""All of the corpus objects used in tmpl live here.
"""
from preprocess import tokenizeDocuments, _tokenizeDocument
from preprocess import lemmatizeTokenLists, _lemmatizeTokenList
from preprocess import stemTokenLists, stemTokenList
from preprocess import applyRules
from reader import JsonFileReader
from utils import DiskCache

class BaseCorpus(object):
    """Represents a bare-bones corpus object.
    """
    def __init__(self, corpusDir, forceRerun=False):
        self.corpusDir
        self.forceRerun = forceRerun

    @staticmethod
    @DiskCache()
    def preprocessAll(documents, lemmatize=True):
        """Applies replacement rules (cleans), tokenizes, and stems 
        a list of plain string documents.

        By default, will lemmatize corpus using the WordNetLemmatizer. 
        If lemmatize is set to False, will stem the corpus using 
        the PorterStemmer. 

        Args:
            documents: list of plain string documents to be preprocessed.

        Returns:
            A list of cleaned and stemmed/lemmatized token lists. 
        """
        logging.info('Raw documents...')
        logging.info(documents)

        logging.info('Cleaning...')
        cleaned = applyRules(documents, RULES)
        logging.info(cleaned)

        logging.info('Tokenizing and removing stopwords...')
        tokenized = tokenizeDocuments(cleaned)
        logging.info(tokenized)

        if lemmatize:
            logging.info('Lemmatizing...')
            preprocessed = lemmatizeTokenLists(tokenized)
            logging.info(preprocessed)

        # Stem instead.
        else:
            logging.info('Stemming...')
            preprocessed = stemTokenLists(tokenized)
            logging.info(preprocessed)

        return preprocessed

    def preprocessOne(document, lemmatize=True):
        """Cleans
        """

class AbstractCorpus(BaseCorpus):
    """A gensim-compatible streaming corpus of abstracts.
    """
    def __iter__(self):
        pass

class FulltextCorpus(BaseCorpus):
    """A gensim-compatible streaming corpus of fulltexts.
    """
    def __iter__(self):