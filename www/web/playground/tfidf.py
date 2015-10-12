import nltk
import string
import os
import sys
import codecs

from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.porter import PorterStemmer

path = '/Users/evelynding/Documents/College/Junior/IW/tmpl/raw/abs/top4/ICFP 1996'
token_dict = []
file_name = []
stemmer = PorterStemmer()

def stem_tokens(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed

def tokenize(text):
    tokens = nltk.word_tokenize(text)
    stems = stem_tokens(tokens, stemmer)
    return stems

for subdir, dirs, files in os.walk(path):
    for file in files:
        file_path = subdir + os.path.sep + file
        file_name.append(file)
        shakes = open(file_path, 'r')
        text = shakes.read()
        lowers = text.lower()
        no_punctuation = lowers.translate(None, string.punctuation)
        token_dict.append(no_punctuation)

        
#this can take some time
#make sure to either set decode_error as ignore or possibly provide support for other encoding
tfidf = TfidfVectorizer(decode_error='ignore', tokenizer=tokenize, stop_words='english')

tfs = tfidf.fit_transform(token_dict)
feature_names = tfidf.get_feature_names()
dense = tfs.todense()

def doc(doc_index, count):
    print file_name[doc_index] + "\n"
    first_doc = dense[doc_index].tolist()[0]
    phrase_scores = [pair for pair in zip(range(0, len(first_doc)), first_doc) if pair[1] > 0]
    sorted_phrase_scores = sorted(phrase_scores, key=lambda t: t[1] * -1)
    for phrase, score in [(feature_names[word_id], score) for (word_id, score) in sorted_phrase_scores][:20]:
        #line = unicode(phrase) + "\t\t" + unicode(score)
        line = ('{0: <20} {1}'.format(phrase, score))
        #line = line.encode('utf-8')
        sys.stdout = codecs.getwriter('utf8')(sys.stdout)
        sys.stdout.write(line + "\n")

doc(3, 20)
