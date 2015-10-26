import nltk
import string
import os
import sys
import codecs
import math
import re


from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.porter import PorterStemmer

path = '/Users/evelynding/Documents/College/Junior/IW/tmpl/raw/full/popl'
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

pattern = re.compile("([0-9])+-fulltext.txt")

textvect = []
for subdir, dirs, files in os.walk(path):
    for file in files:
        if pattern.match(file):
            file_path = subdir + os.path.sep + file
            file_name.append(subdir[-4:] + file)
            shakes = open(file_path, 'r')
            text = shakes.read()
            lowers = text.lower()
            no_punc = lowers.translate (None, string.punctuation)
            no_nums = no_punc.translate(None, '0123456789')
            textvect.append(no_nums)

print "finished reading\n"
countVect = CountVectorizer(decode_error='ignore', tokenizer=tokenize, stop_words='english')
countRes = countVect.fit_transform(textvect)
print "finish transform\n"
countArray = countRes.toarray()
termNames = countVect.get_feature_names()
print termNames

numTerms = len(countArray[0])
print numTerms
numDocs = len(countArray)
print numDocs
numWords = 0;
for i in range(numDocs):
    for j in range(numTerms):
        numWords += countArray[i][j]
print numWords

termOccurs = []
numOccurs = []
for i in range(numTerms):
    termOccurs.append(0)
    numOccurs.append(0)
print "occurs done\n"

for j in range(numTerms):
    for i in range(numDocs):
        if (countArray[i][j] != 0):
            termOccurs[j] = termOccurs[j] +1;
            numOccurs[j] = numOccurs[j] + countArray[i][j]
print "calculations\n"

topTerms = [[0 for x in range(numTerms)] for x in range(numDocs)]
for i in range(numDocs):
    for j in range(numTerms):
        topTerms[i][j] = numOccurs[j]/float(numWords)* math.log(numDocs/ termOccurs[j])
print "top terms\n"
# if not os.path.exists('/popl'):
#     os.makedirs(dir)

for i in range(numDocs):
    whitelist = [x for (y, x) in sorted(zip(topTerms[i], termNames), key=lambda pair: pair[0] *-1 )][:3000]
    newfile = 'res' + file_name[i]
    f = open(newfile, 'w')
    for j in range(numTerms):
        if termNames[j] in whitelist:
            for x in range (0, countArray[i][j].astype(int)):
                f.write(termNames[j].encode("UTF-8") + " ")
