import codecs
import logging
import os

from copy import copy
from datetime import datetime
from pprint import pprint

from gensim.corpora import Dictionary
from gensim.models.ldamodel import LdaModel

# from nltk.corpus import stopwords
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

def loadStopwords():
    stopwords = set(map(lambda s: s.strip(),
                codecs.open("stopwords.dat","r","utf8").readlines()))
    return stopwords

stopwords = loadStopwords()

""" Step 1: Pre-process corpus. """
@DiskCache(forceRerun=True)
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
    # stoplist = set(stopwords.words('english'))
    tokenized = []
    for word in document.lower().split():
        if word not in stopwords:
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
def lda(documents, num_topics, passes, iterations, chunksize, alpha, gamma_threshold):
    tokenized = preprocess(documents)
    dictionary = generateDictionary(tokenized)
    DTMatrix = tokenizedToDTMatrix(tokenized, dictionary)
    ldamodel = LdaModel(DTMatrix,
                        num_topics=num_topics,
                        id2word=dictionary, 
                        iterations=iterations,
                        alpha=alpha,
                        passes=passes,
                        chunksize=chunksize,
                        gamma_threshold=gamma_threshold)
    logging.info(ldamodel.print_topics(num_topics=num_topics, num_words=20))
    return ldamodel

def read():
    pathToAbs = '/Users/smacpher/clones/tmpl_venv/tmpl-data/abs/top4/'
    reader = JsonFileReader()
    (documents, meta) = reader.loadAllAbstracts(pathToAbs, recursive=True)
    return (documents, meta)


def topPapers(corpus, modelFilepath, numTopics, n):
    """Prints the top n papers for each topic number in numTopics of a given model.
    """
    (documents, meta) = corpus
    model = LdaModel.load(modelFilepath)

    # Default probability value for fetching topic probabilities for each document
    # (to account for cases when a topic isn't present in the document's topic vector)
    defaultValue = 0

    # Zip documents' meta data and topic vectors to keep them together 
    # when we sort.
    metaAndVectorTuples = zip(meta, model[documents])
    allTops = []
    for topicNum in range(numTopics):
        curTops = sorted( # Top papers for current topic.
            metaAndVectorTuples, 
            reverse=True, 
            key=lambda x: abs(dict(x[1]).get(topicNum, defaultValue)) # Get probability from second value in tuple (topic vector) and sort.
        )
        allTops.append(curTops[:n])
    return allTops


def topPapersToFile(topPapers, filepath):
    """Writes contents of list, a, line-by-line to filepath.
    """
    with open(filepath, 'w') as f:
        for topicNum in range(len(topPapers)):
            f.write("Topic #{topicNum}".format(topicNum=topicNum))
            f.write('\n')
            f.writelines(
                map(lambda x: x.encode('ascii', 'replace') + '\n', topPapers[topicNum])
            )
            f.write('\n\n')
    return


"""Run LDA

Parameters:
    
    Alpha and beta:

    Symmetric distribution:

        alpha: hyperparameter that affects sparsity of document-topic
            distribution (eg. higher alpha = documents are made up of more topics,
            lower alpha = documents contain fewer topics.)
        beta: hyperparameter that affects topic-word distribution.
            (high beta = topics are made up of most of the words in the corpus,
            low beta = consist of few words)
    Assymetric distribution:
        alpha: higher alpha results in more specific topic distribution per document.
        beta: higher beta results in more specific word distribution per topic.

        In general, higher alpha values mean documents contain more similar topic contents.
        (assymetric alpha is more useful than assymetric beta according to Wallach.)

    *I think gensim's LDA 'eta' param is 'beta'.

    Gensim specific params:
        passes: number of training passes through the corpus.

Parameters to test:
    Changing dtype to np.float64, tweak gamma_threshold (same as EM convergence),
    and iterations (same as em max iter)

*** Added program, programs, used, language to stopwords.dat. -> didn't really help.
"""


if __name__ == '__main__':
    # Gensim LDA parameters.
    NUM_TOPICS = 50
    PASSES = 100
    ITERATIONS = 1000
    CHUNKSIZE = 3744 # Number of documents in the abstract corpus.
    ALPHA = 'auto'
    GAMMA_THRESHOLD = 0.0001

    # Saved model path info.
    MODEL_ARCHIVE_DIR = '/Users/smacpher/clones/tmpl_venv/tmpl/experimental/models'
    MODEL_DIR = 'model-{numTopics}t-{passes}p-{iterations}i-{alpha}a-{gammaThreshold}g'.format(
        numTopics=NUM_TOPICS,
        passes=PASSES,
        iterations=ITERATIONS,
        alpha=ALPHA,
        gammaThreshold=GAMMA_THRESHOLD,
    )
    MODEL_FILENAME = 'model'
    # MODEL_FILEPATH = os.path.join(MODEL_ARCHIVE_DIR, MODEL_DIR, MODEL_FILENAME)
    MODEL_FILEPATH = os.path.join(MODEL_ARCHIVE_DIR, MODEL_FILENAME)
    TOP_PAPERS_FILEPATH = '/Users/smacpher/clones/tmpl_venv/tmpl/experimental/top_papers.test'

    (documents, meta) = read()
    tokenized = preprocess(documents)
    dictionary = generateDictionary(tokenized)
    DTMatrix = tokenizedToDTMatrix(tokenized, dictionary)

    # model = lda(documents, num_topics=NUM_TOPICS, iterations=ITERATIONS, alpha='auto')
    # model.save(os.path.join(modelArchiveDir, modelFileName))
    allTops = topPapers((DTMatrix, meta), MODEL_FILEPATH, 50, 10)

    allTopTitles = []
    for tops in allTops:
        topTitles = [meta['title'] for (meta, topicVector) in tops]
        allTopTitles.append(topTitles)

    topPapersToFile(allTopTitles, TOP_PAPERS_FILEPATH)


