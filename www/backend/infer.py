import sys, os
import pickle

import nltk

from utils import *

def words_to_dict(words):
    return dict(zip(words, range(0, len(words))))

use_wordnet = True
if use_wordnet:
    stemmer = nltk.stem.wordnet.WordNetLemmatizer()
    stem = stemmer.lemmatize
else:
    stemmer = nltk.stem.porter.PorterStemmer()
    stem = stemmer.stem
    
def tokens(text):
    replacements = [("---"," "),
                    ("--"," "),
                    ("-", "")] # trying to capture multi-word keywords

    for (src,tgt) in replacements:
        text = text.replace(src,tgt)
    
    return preprocess(text)

def make_bow(doc,d):
    bow = {}
    
    for word in doc:
        if word in d:
            wordid = d[word]
            bow[wordid] = bow.get(wordid,0) + 1
        # XXX we should notify something about non-stopwords that we couldn't parse
            
    return bow


modes = ["fulltext","abstracts"]
ks = ["20","50","100","200"]

if __name__ == '__main__':
    args = sys.argv[1:]

    mode = modes[0]
    k = ks[0]
    num = 20
    while len(args) > 1:
        if args[0] == "-k":
            if args[1] in ks:
                k = args[1]

            args = args[2:]

        if args[0] in ["-m","--mode"]:
            if args[1] in modes:
                mode = args[1]

            args = args[2:]

        if args[0] in ["-n","--num"]:
            if args[1] in range(1,50):
                num = args[1]

            args = args[2:]

    model = os.path.join(mode,"lda" + k,"final")
    words = os.path.join(mode,"vocab.dat")
    docs = os.path.join(mode,"docs.dat")
            
    pdf_file = args[0]
    (base,_) = os.path.splitext(pdf_file)
    
    text = os.popen("pdftotext \"%s\" -" % pdf_file).read() # XXX safe filenames!

    vocab = words_to_dict(open(words).read().split())
    
    bow = make_bow(map(stem,tokens(text)),vocab)

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
    # XXX capture output, handle errors
    inf = read(base + "-gamma.dat")
    
    gammas = read(model + ".gamma")
    papers = zip(read(docs), map(lambda s: map(float,s.split()), gammas))

    tgt = ["INPUT PDF"] + map(lambda s: map(float,s.split()), inf)
    # XXX these are the topic values, if we want to visualize them
    # XXX be careful to not leak our filenames
    
    papers = map(lambda s: (distance(s[1],tgt[1]),s), papers)
    papers.sort(lambda x,y: cmp(x[0],y[0]))

    print "\nRelated papers:\n"
    for (d,(doc,gs)) in papers[0:num]:
        print '  %s (%d)' % (doc,d)   
