import logging

from pprint import pprint
from gensim import corpora
from nltk.corpus import stopwords

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', 
                    level=logging.INFO)

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

# 1.c. Stemming / Lemmatizing: collapse words with equivalent semantics.




# Convert each document to a list of lowercase words without stopwords.
preProcessed = [
    [word for word in document.lower().split() if word not in stoplist] 
    for document in documents
]

if __name__ == '__main__':
    print("Stop words:")
    pprint(stoplist)
