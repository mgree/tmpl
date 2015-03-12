import sys, os
import pickle

import gensim
import nltk

from utils import *

def words_to_dict(words):
    return dict(zip(words, range(0, len(words))))

# XXX make these parameters
model = "../lda/2015-03-10_09:16_lda20/final"
words = "../lda/2015-03-10_09:16_vocab.dat"
vocab = words_to_dict(open(words).read().split())
docs = "../lda/2015-03-10_09:16_docs.dat"
num = 20

use_wordnet = True
if use_wordnet:
    stemmer = nltk.stem.wordnet.WordNetLemmatizer()
    stem = stemmer.lemmatize
else:
    stemmer = nltk.stem.porter.PorterStemmer()
    stem = stemmer.stem

def tokenize(text):
    replacements = [("---"," "),
                    ("--"," "),
                    ("-", "")] # trying to capture multi-word keywords

    for (src,tgt) in replacements:
        text = text.replace(src,tgt)
    
    words = gensim.utils.simple_preprocess(text) # XXX can we drop this requirement?

    return words

def make_bow(doc,d):
    bow = {}
    
    for word in doc:
        if word in d:
            wordid = d[word]
            bow[wordid] = bow.get(wordid,0) + 1
        # XXX we should notify something about non-stopwords that we couldn't parse
            
    return bow

if __name__ == '__main__':
    pdf_file = sys.argv[1]
    (base,_) = os.path.splitext(pdf_file)
    
    text = os.popen("pdftotext \"%s\" -" % pdf_file).read() # XXX safe filenames!
    
    bow = make_bow(map(stem,tokenize(text)),vocab)

    dat_file = base + ".dat"
    out = open(dat_file,"w")
    out.write(str(len(bow)))
    out.write(' ')
    for term in bow:
        out.write(str(term))
        out.write(':')
        out.write(str(bow[term]))
        out.write(' ')
    out.write('\n')
    out.close()

    os.system("lda inf settings.txt %s %s %s" % (model,dat_file,base))
    inf = read(base + "-gamma.dat")
    
    gammas = read(model + ".gamma")
    papers = zip(read(docs), map(lambda s: map(float,s.split()), gammas))

    tgt = ["INPUT PDF"] + map(lambda s: map(float,s.split()), inf)
    # XXX these are the topic values, if we want to visualize them
    
    papers = map(lambda s: (distance(s[1],tgt[1]),s), papers)
    papers.sort(lambda x,y: cmp(x[0],y[0]))

    print "\nRelated papers:\n"
    for (d,(doc,gs)) in papers[0:num]:
        print '  %s (%d)' % (doc,d)   
