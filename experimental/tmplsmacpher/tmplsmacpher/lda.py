import logging

from copy import copy
from datetime import datetime
from pprint import pprint

from gensim.corpora import Dictionary
from gensim.models.ldamodel import LdaModel

from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer

from reader import JsonFileReader
from utils import DiskCache


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', 
                    level=logging.DEBUG)

RULES = [
    ('---', ' '),
    ('--', ' '),
    ('-', ''),
]


""" Step 1: Pre-process corpus. """
@DiskCache(forceRerun=False)
def preprocess(documents, lemmatize=True):
    """Cleans, tokenizes, and stems a list of plain string documents.
    By default, will lemmatize corpus using the WordNetLemmatizer. 
    If lemmatize is set to False, will stem the corpus using the PorterStemmer. 
    
    Args:
        documents: list of plain string documents to be preprocessed.

    Returns:
        A list of cleaned and stemmed token lists. 
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


# 1.a. Tokenization: convert document to individual elements.
# 1.b. Stopword removal: remove trivial, meaningless words.
@DiskCache(forceRerun=False)
def tokenizeDocuments(documents):
    """Tokenizes a list of documents.

    Args:
        document: list of plain string documents to tokenize.

    Returns:
        List of tokenized documents.
    """
    return [_tokenizeDocument(document) for document in documents]


def _tokenizeDocument(document):
    """Converts a single document to lowercase, removes stopwords, and tokenizes.

    Args:
        document: plain string document to be tokenized.

    Returns:
        Tokenized version of document.
    """
    # Stop words are common english words that can be deemed extraneous to 
    # certain natural language processing techniques and therefore can be 
    # filtered out of the training corpus.
    stoplist = set(stopwords.words('english'))
    tokenized = []
    for word in document.lower().split():
        if word not in stoplist:
            tokenized.append(word)
    return tokenized

@DiskCache(forceRerun=False)
def applyRules(documents, rules):
    """Used to apply hard-coded rules to documents.
    Eg. Replacing hyphens with spaces, replacing em dashes, etc.
    
    Args:
        documents: list of plain string documents to apply rules to.
        rules: list of tuples mapping old pattern to desired pattern.

    Returns:
        Documents with rules applied.
    """
    cleanedDocuments = []
    for document in documents:

        cleaned = copy(document)

        # Cycle through rules and apply them to each document one by one.
        for (old, new) in rules:
            cleaned = cleaned.replace(old, new)

        # Add fully cleaned document (with all rules applied) to list.
        cleanedDocuments.append(cleaned)

    return cleanedDocuments


# 1.c. Stemming / Lemmatizing: collapse words with similar semantics 
# but different syntactic forms.

# 1.c. (Option 1: Stemming)
# Chops off the ends of the words using a rough heuristic process that
# takes into account the length of the word, number of syllables, etc. to 
# chop off the end of a word in the hopes are arriving at its atomic stem.
@DiskCache(forceRerun=False)
def stemTokenLists(tokenLists):
    """Stems a list of token lists.

    Args:
        tokenLists: list of token lists to be stemmed.

    Returns:
        A list of stemmed token lists.
    """
    return [_stemTokenList(tokenList) for tokenList in tokenLists]


def _stemTokenList(tokenList):
    """Stems a single token list. Trims off ends of words in
    the hopes of reducing semantically related words to the same stem.

    Eg. 'chopping', 'chopped', 'chopper' --> 'chop'

    Args:
        tokenLists: the single token list to be stemmed.

    Returns:
        A stemmed token lists.
    """
    stemmer = PorterStemmer()
    return [stemmer.stem(token) for token in tokenList]


# 1.c. (Option 2: Lemmatization)
# Uses vocubulary and morphological analysis with the aim of
# only removing inflectional endings (eg. 'chopping' vs. 'chopped')
# and returning the dictionary base of a word -- known as the word's 'lemma.'
@DiskCache(forceRerun=False)
def lemmatizeTokenLists(tokenLists):
    """Lemmatizes a list of token lists.

    Args:
        tokenLists: list of token lists to be lemmatized.

    Returns:
        A list of lemmatized token lists.
    """
    return [_lemmatizeTokenList(tokenList) for tokenList in tokenLists]


def _lemmatizeTokenList(tokenList):
    """Lemmatizes a single token list.

    Args:
        tokenList: the single token list to be lemmatized.

    Returns:
        A lemmatized token list.
    """
    lemmatizer = WordNetLemmatizer()
    return [lemmatizer.lemmatize(token) for token in tokenList]


""" Step 2: Convert preprocessed corpus into a document-term matrix. """
@DiskCache(forceRerun=False)
def generateDictionary(tokenized):
    """Geneates a dictionary mapping unique terms to id's from a tokenized
    corpus.

    Args:
        tokenized: tokenzied corpus (list of token lists) to generate a
            dictionary from.

    Returns:
        A dictionary mapping unique terms to id's.
    """

    # Gensim provides us this Dictionary function which
    # assigns unique integer id's to each distinct token and
    # caches other statistics about the corpus.
    # Note: we can print the term to term id mappings with the
    # Dictionary.token2id() method.
    logging.info("Constructing dictionary from tokenized corpus...")
    dictionary = Dictionary(tokenized)
    logging.info(dictionary)

    return dictionary

@DiskCache(forceRerun=False)
def tokenizedToDTMatrix(tokenized, dictionary):
    """Converts tokenized corpus to a document-term matrix.
    A document-term matrix is a matrix whose rows represent documents and
    columns represent words mapped to their frequency heuristics.

    Args:
        tokenized: tokenized corpus (list of token lists) to covert to a
            DTMatrix (document-term matrix).
        dictionary: a gensim.corpora.Dictionary object mapping unique terms
            to id's.

    Returns:
        A document-term matrix of the corpus.
    """

    # Uses our newly constructed dictionary and tokenized corpus to
    # build a bag of words. The bag of words is comprised of
    # document vectors (one per document in our corpus) whose elements are
    # tuples mapping dictionary term id's to the term's frequency.
    logging.info(
        "Using dictionary and tokenized corpus to create bag of words..."
    )
    bagOfWords = [dictionary.doc2bow(tokenList) for tokenList in tokenized]
    logging.info(bagOfWords)

    return bagOfWords


""" Step 3: Generate LDA topic model from corpus' document-term matrix. """
def lda(documents, num_topics, passes):
    tokenized = preprocess(documents)
    dictionary = generateDictionary(tokenized)
    DTMatrix = tokenizedToDTMatrix(tokenized, dictionary)

    logging.info(
        'Running lda model with {num_topics} topics and {passes} passes...'
        .format(num_topics=num_topics, passes=passes)
    )
    ldamodel = LdaModel(DTMatrix,
                        num_topics=num_topics,
                        id2word=dictionary, 
                        passes=passes)
    logging.info(ldamodel.print_topics(num_topics=num_topics, num_words=10))

    return ldamodel

def read():
    pathToAbs = '/Users/smacpher/clones/tmpl_venv/tmpl-data/abs/top4/'
    reader = JsonFileReader()
    (documents, meta) = reader.loadAllAbstracts(pathToAbs, recursive=True)
    return (documents, meta)


def main():
    NUM_TOPICS = 20
    PASSES = 50
    modelArchiveDir = '/Users/smacpher/clones/tmpl_venv/tmpl/experimental/models'
    modelFileName = 'lda-{num_topics}-{passes}-{timestamp}'.format(
        num_topics=NUM_TOPICS, 
        passes=PASSES, 
        timestamp=datetime.now().isoformat()
    )
    model = lda(documents, num_topics=NUM_TOPICS, passes=PASSES)
    model.save(os.path.join(modelArchiveDir, modelFileName))
    return model


if __name__ == '__main__':
    main()
