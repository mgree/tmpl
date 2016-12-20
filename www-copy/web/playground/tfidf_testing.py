import nltk
import string
import os
import sys
import codecs
import math
import re
import operator
import unicodedata

from nltk.corpus import stopwords

stemmer = nltk.stem.wordnet.WordNetLemmatizer()
stem = stemmer.lemmatize

def encode_ascii (word):
    return word.encode('ascii', 'ignore')

words = ["ponies", "cats", "cat", "caresses"]
words = map(stem, words)
words = map(encode_ascii, words)
print words

f = open ("sort_trial", 'w')
final_whitelist = set(['a', 'aa', 'aaa', 'a', 'b', '%%', '%32*', '*'])
final_whitelist = list(final_whitelist)
final_whitelist.sort(key = len)
for whitelist_term in final_whitelist:
    f.write(whitelist_term + "\n")

path = '/Users/evelynding/Documents/College/Junior/IW/tmpl/raw/full/pldi_full'
token_dict = []
file_name = []

wordDocs = {}
wordCount = {}
numWords = 0
numDocs = 0

pattern = re.compile("([0-9])+-fulltext.txt")

dir = '/Users/evelynding/Documents/College/Junior/IW/tmpl/www/web/playground/pldi_lemmatized'
if not os.path.exists(dir):
    os.makedirs(dir)

regex = re.compile('[^ a-z]')

for subdir, dirs, files in os.walk(path):
    for file in files:
        if pattern.match(file):
            numDocs += 1
            file_path = subdir + os.path.sep + file
            shakes = open(file_path, 'r')
            text = shakes.read()
            lowers = text.lower()
            #no_punc = lowers.translate (None, string.punctuation)
            #no_nums = no_punc.translate(None, '0123456789')
            no_nums = regex.sub('', lowers)
            words = no_nums.split()
            words = map(stem, words)
            words = map(encode_ascii, words)
            tempDict = {}
            for word in words:
                if len(word) >= 3:
                    numWords += 1
                    if word in tempDict:
                        tempDict[word] += 1
                    else:
                        tempDict[word] = 1
            for key, value in tempDict.iteritems():
                if key in wordCount:
                    wordCount[key] += value
                    wordDocs[key] += 1
                else:
                    wordCount[key] = value
                    wordDocs[key] = 1

print numWords

topTerms = {}
for key in wordCount:
    topTerms[key] = abs (wordCount[key]/float(numWords)*math.log(wordDocs[key]/float(numDocs)))

print numWords
print numDocs

whitelist = sorted(topTerms.items(), key=operator.itemgetter(1), reverse=True)[:6000]
whitelist = [i[0] for i in whitelist]
f = open ("whitelist", 'w')


whitelist = set(whitelist)
print len(whitelist)
blacklist = set(stopwords.words('english'))
curated_stopwords = set(['bdbc', 'bcbc', 'ddd', 'dddd', 'dda', 'dcd', 'dbd', 'cbd', 'bba', 'bdb', 'bdba', 'bdbe', 'beba', 'bfba', 'cbc', 'ccd', 'cdd', 
    'dbdd', 'dbddd', 'ddb', 'ddbd', 'dddb', 'dddda', 'ddddd', 'dddddb', 'dddddd', 'acd'])
secondary_whitelist = whitelist.difference(blacklist)
final_whitelist = secondary_whitelist.difference(curated_stopwords)
final_whitelist = list(final_whitelist)
final_whitelist.sort(key = len)
for whitelist_term in final_whitelist:
    f.write(whitelist_term + "\n")

print len(final_whitelist)
    #if (wordDocs[whitelist_term] < cutOff):
    #    f.write( '{:<20} {:<20} {:<10} {:<10}\n'.format (whitelist_term, topTerms[whitelist_term], wordCount[whitelist_term], wordDocs[whitelist_term]))
    #f.write (whitelist_term + " ")

print "done with the whitelist..."

for subdir, dirs, files in os.walk(path):
    for file in files:
        if pattern.match(file):
            file_path = subdir + os.path.sep + file
            shakes = open(file_path)
            text = shakes.read()
            lowers = text.lower()
            no_punc = lowers.translate (None, string.punctuation)
            no_nums = no_punc.translate(None, '0123456789')
            words = no_nums.split()
            newWords = [x for x in words if x in final_whitelist]
            newfile = dir + '/res' + subdir[-4:] + '-' + file
            f = open(newfile, 'w')
            for newWord in newWords:
                f.write(newWord + " " )
# # if not os.path.exists('/popl'):
# #     os.makedirs(dir)