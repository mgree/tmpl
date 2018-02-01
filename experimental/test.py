import logging

from pprint import pprint
from gensim import corpora
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', 
                    level=logging.INFO)

RULES = [
    ('---', ' '),
    ('--', ' '),
    ('-', ''),
]


documents = [
    "Human machine interface for lab abc computer applications",
    "A survey of user opinion of computer system response time",
    "The EPS user interface management system",
    "System and human system engineering testing of EPS",
    "Relation of user perceived response time to error measurement",
    "The generation of random binary unordered trees",
    "The intersection graph of paths in trees",
    "Graph minors IV Widths of trees and well quasi ordering",
    "Graph minors A survey",
]


# Stop words are common english words that can be deemed extraneous to certain
# natural language processing techniques and therefore can be filtered
# out of the training corpus.
stoplist = set(stopwords.words('english'))

""" 1. Pre-process corpus. """

def preprocess(documents):
    """Cleans, tokenizes, and stems a list of plain string documents.
    
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

    logging.info('Tokenizing...')
    tokenized = tokenizeDocuments(cleaned)
    logging.info(tokenized)

    logging.info('Stemming...')
    stemmed = stemTokenLists(tokenized)
    logging.info(stemmed)

    logging.info('Lemmatizing...')
    lemmatized = lemmatizeTokenList(tokenized)
    logging.info(lemmatized)

    return stemmed


# 1.a. Tokenization: convert document to individual elements.
# 1.b. Stopword removal: remove trivial, meaningless words.
def tokenizeDocuments(documents):
    """Tokenizes a list of documents.

    Args:
        document: list of plain string documents to tokenize.

    Returns:
        List of tokenized documents.
    """
    return [tokenizeDocument(document) for document in documents]


def tokenizeDocument(document):
    """Converts a single document to lowercase, removes stopwords, and tokenizes.

    Args:
        document: plain string document to be tokenized.

    Returns:
        Tokenized version of document.
    """
    tokenized = []
    for word in document.lower().split():
        if word not in stoplist:
            tokenized.append(word)
    return tokenized


def applyRules(documents, rules):
    """Used to apply hard-coded rules to documents.
    Eg. Replacing hyphens with spaces, replacing em dashes, etc.
    
    Args:
        documents: list of plain string documents to apply rules to.
        rules: list of tuples mapping old pattern to desired pattern.

    Returns:
        Documents with rules applied.
    """
    result = None
    for (old, new) in rules:
        result = [document.replace(old, new) for document in documents]
    return result

# 1.c. Stemming / Lemmatizing: collapse words with similar semantics 
# but different syntactic forms.

# 1.c. (Option 1: Stemming)
# Chops off the ends of the words using a rough heuristic process that
# takes into account the length of the word, number of syllables, etc. to 
# chop off the end of a word in the hopes are arriving at its atomic stem.
def stemTokenLists(tokenLists):
    """Stems a list of token lists.

    Args:
        tokenLists: list of token lists to be stemmed.

    Returns:
        A list of stemmed token lists.
    """
    result = None
    for tokenList in tokenLists:
        result.append(stemTokenLists)
    return [stemTokenList(tokenList) for tokenList in tokenLists]

def stemTokenList(tokenList):
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
def lemmatizeTokenLists(tokenLists):
    """Lemmatizes a list of token lists.

    Args:
        tokenLists: list of token lists to be lemmatized.

    Returns:
        A list of lemmatized token lists.
    """
    return [lemmatizeTokenList(tokenList) for tokenList in tokenLists]

def lemmatizeTokenList(tokenList):
    """Lemmatizes a single token list.

    Args:
        tokenList: the single token list to be lemmatized.

    Returns:
        A lemmatized token list.
    """
    lemmatizer = WordNetLemmatizer()
    return [lemmatizer.lemmatize(token) for token in tokenList]

def main():
    preprocessed = preprocess(documents)


if __name__ == '__main__':
    print("Stop words:")
    pprint(stoplist)
    main()

