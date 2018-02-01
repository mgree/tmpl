import logging

from pprint import pprint
from gensim import corpora
from nltk.corpus import stopwords


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

# 1.a. Tokenization: convert document to individual elements.
# 1.b. Stopword removal: remove trivial, meaningless words.
def tokenizeDocuments(documents):
    """Tokenizes documents.

    Args:
        document: list of plain string documents to tokenize.

    Returns:
        List of tokenized documents.
    """
    return [tokenizeDocument(document) for document in documents]


def tokenizeDocument(document):
    """Converts document to lowercase, removes stopwords, and tokenizes.

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

# 1.c. Stemming / Lemmatizing: collapse words with equivalent semantics.



def main():
    tokenized = tokenizeDocuments(documents)
    logging.info(tokenized)

if __name__ == '__main__':
    print("Stop words:")
    pprint(stoplist)
    main()

