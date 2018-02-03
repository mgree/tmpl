import logging

from copy import copy
from pprint import pprint

from gensim.corpora import Dictionary
from gensim.models.ldamodel import LdaModel
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

""" Step 1: Pre-process corpus. """
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

    logging.info('Tokenizing and removing stopwords...')
    tokenized = tokenizeDocuments(cleaned)
    logging.info(tokenized)

    logging.info('Stemming...')
    stemmed = stemTokenLists(tokenized)
    logging.info(stemmed)

    logging.info('Lemmatizing...')
    lemmatized = lemmatizeTokenLists(tokenized)
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
def stemTokenLists(tokenLists):
    """Stems a list of token lists.

    Args:
        tokenLists: list of token lists to be stemmed.

    Returns:
        A list of stemmed token lists.
    """
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


""" Step 2: Convert preprocessed corpus into a document-term matrix. """
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


# TODO: refactor to separate dictionary and bagOfWords logic.
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

    logging.info('Running lda model with 2 topics and 20 passes...')
    ldamodel = LdaModel(DTMatrix, 
                        num_topics=num_topics, 
                        id2word=dictionary, 
                        passes=passes)
    logging.info(ldamodel.print_topics(num_topics=2, num_words=3))

    return lda

if __name__ == '__main__':
    lda(documents, num_topics=2, passes=20)

