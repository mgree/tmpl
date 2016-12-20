import nltk
import string
import os
import sys
import codecs
import math
import re
import operator


from nltk.stem.porter import PorterStemmer

path = '/Users/mgree/tmpl/raw/abs/popl_to_2014'
token_dict = []
file_name = []
stemmer = PorterStemmer()

wordDocs = {}
wordCount = {}
numWords = 0
numDocs = 0

pattern = re.compile("([0-9])+.txt")

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

#print wordDocs
#print wordCount
print numWords

topTerms = {}
for key in wordCount:
    topTerms[key] = wordCount[key]/float(numWords)*math.log(wordDocs[key]/float(numDocs))

whitelist = sorted(topTerms.items(), key=operator.itemgetter(1))[:6000]
whitelist = [i[0] for i in whitelist]
f = open ("whitelist", 'w')
for whitelist_term in whitelist:
    f.write (whitelist_term + " ")
whitelist = set(whitelist)
print len(whitelist)
blacklist = set (['the', 'of', 'and', 'in', 'is', 'to', 'we', 'that', 'for'])
final_whitelist = whitelist - blacklist
print len(final_whitelist)

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
            newWords = [x for x in words if x in whitelist] # TODO this will be faster if you turn whitelist into a set before the loop
            newfile = 'res' + subdir[-4:] + '-' + file
            f = open(newfile, 'w')
            for newWord in newWords:
                f.write(newWord + " " )
# # if not os.path.exists('/popl'):
# #     os.makedirs(dir)