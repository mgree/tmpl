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

if not os.path.exists('poplfull/stemming/'):
    os.makedirs('poplfull/stemming/')

stemmer = nltk.stem.wordnet.WordNetLemmatizer()
stem = stemmer.lemmatize

pattern = re.compile("([0-9])+-fulltext.txt")

def translate_non_alphanumerics(to_translate, translate_to=u'_'):
    not_letters_or_digits = u'!"#%\'()*+,-./:;<=>?@[\]^_`{|}~'
    translate_table = dict((ord(char), translate_to) for char in not_letters_or_digits)
    return to_translate.translate(translate_table)

for subdir, dirs, files in os.walk(path):
    for file in files:
        if pattern.match(file):
            numDocs += 1
            file_path = subdir + os.path.sep + file
            shakes = codecs.open(file_path, 'r', 'utf-8', errors='ignore')
            text = shakes.read()
            lowers = text.lower()
            no_punc_nums = translate_non_alphanumerics(lowers)
            #no_punc = lowers.translate (None, string.punctuation)
            #no_nums = no_punc.translate(None, '0123456789')
            words = no_punc_nums.split()
            words_stemmed = map(stem, words)
            tempDict = {}
            for word in words_stemmed:
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
    topTerms[key] = wordCount[key]/float(numWords)*math.log(wordDocs[key]/numDocs)

whitelist = sorted(topTerms.items(), key=operator.itemgetter(1))[:6000]
whitelist = [i[0] for i in whitelist]
f = open ("whitelist", 'w')
for whitelist_term in whitelist:
    f.write ((whitelist_term + " ").encode("UTF-8"))

print "done with the whitelist..."

for subdir, dirs, files in os.walk(path):
    for file in files:
        if pattern.match(file):
            file_path = subdir + os.path.sep + file
            shakes = codecs.open(file_path, 'r', 'utf-8', errors='ignore')
            text = shakes.read()
            lowers = text.lower()
            no_punc_nums = translate_non_alphanumerics(lowers)
            #no_punc = lowers.translate (None, string.punctuation)
            #no_nums = no_punc.translate(None, '0123456789')
            words = no_punc_nums.split()
            newWords = [x for x in words if x in whitelist]
            newfile = 'poplfull/stemming/' + 'res' + subdir[-4:] + '-' + file
            f = open(newfile, 'w')
            for newWord in newWords:
                f.write((newWord + " " )).encode("UTF-8")
# # if not os.path.exists('/popl'):
# #     os.makedirs(dir)
