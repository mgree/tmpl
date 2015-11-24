import nltk
import string
import os
import sys
import codecs
import math
import re
import operator


from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords

path = '/Users/evelynding/Documents/College/Junior/IW/tmpl/raw/full/popl'
token_dict = []
file_name = []
stemmer = PorterStemmer()

wordDocs = {}
wordCount = {}
numWords = 0
numDocs = 0

pattern = re.compile("([0-9])+-fulltext.txt")

for subdir, dirs, files in os.walk(path):
    for file in files:
        if pattern.match(file):
            numDocs += 1
            file_path = subdir + os.path.sep + file
            shakes = open(file_path, 'r')
            text = shakes.read()
            lowers = text.lower()
            no_punc = lowers.translate (None, string.punctuation)
            no_nums = no_punc.translate(None, '0123456789')
            words = no_nums.split()
            tempDict = {}
            for word in words:
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
#blacklist = set (['the', 'of', 'and', 'in', 'is', 'to', 'we', 'that', 'for'])
final_whitelist = whitelist.difference(blacklist)
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
            newfile = 'res' + subdir[-4:] + '-' + file
            f = open(newfile, 'w')
            for newWord in newWords:
                f.write(newWord + " " )
# # if not os.path.exists('/popl'):
# #     os.makedirs(dir)