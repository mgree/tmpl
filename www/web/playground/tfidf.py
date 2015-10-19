import nltk
import string
import os
import sys
import codecs

from sklearn.feature_extraction.text import CountVectorizer
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
        no_numbers = no_punctuation.translate(None, '0123456789')
        token_dict.append(no_numbers)

        
#this can take some time
#make sure to either set decode_error as ignore or possibly provide support for other encoding
tfidf = TfidfVectorizer(decode_error='ignore', tokenizer=tokenize, stop_words='english')

vect = []
file_path = subdir + os.path.sep + file_name[3]
print file_path
shakes = open(file_path, 'r')
text = shakes.read()
no_punc = text.translate (None, string.punctuation)
no_nums = no_punc.translate(None, '0123456789')
newvect = []
newvect.append(no_nums)
print "no nums "
print no_nums
countVect = CountVectorizer(decode_error='ignore', tokenizer=tokenize, stop_words='english')
res = countVect.fit_transform(newvect)
print "vect\n"
vect = countVect.get_feature_names()
print vect

array = res.toarray()
print array
#print countVect.vocabulary_
#print res[0].tolist()

#tfs is the new document term matrix
tfs = tfidf.fit_transform(token_dict)
feature_names = tfidf.get_feature_names()
dense = tfs.todense()
whitelist = []

def doc(doc_index, count):
    print file_name[doc_index] + "\n"
    first_doc = dense[doc_index].tolist()[0]
    phrase_scores = [pair for pair in zip(range(0, len(first_doc)), first_doc) if pair[1] > 0]
    sorted_phrase_scores = sorted(phrase_scores, key=lambda t: t[1] * -1)
    for phrase, score in [(feature_names[word_id], score) for (word_id, score) in sorted_phrase_scores][:20]:
        whitelist.append(phrase)

doc(3, 20)

print "whitelist\n"
print whitelist

f = open ('resultingfile', 'w')

for index, val in enumerate(vect, start = 0):
    if vect[index] in whitelist:
        for x in range (0, array[0][index].astype(int)):
            f.write(vect[index].encode("UTF-8") + " ")
            print vect[index]

print "\n\nfiltered\n"
def inWhitelist(element):
    return element in whitelist

c4 = filter(lambda x: x in whitelist, vect)
print c4


file_path = subdir + os.path.sep + file_name[3]
shakes = open(file_path, 'r')
text = shakes.read()
no_punc = text.translate (None, string.punctuation)
no_nums = no_punc.translate(None, '0123456789')
no_nums = no_nums.split()
#print no_nums