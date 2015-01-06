import json
import gensim
import sys, os, glob
import codecs

import nltk

use_wordnet = True
if use_wordnet:
    stemmer = nltk.stem.wordnet.WordNetLemmatizer()
    stem = stemmer.lemmatize
else:
    stemmer = nltk.stem.porter.PorterStemmer()
    stem = stemmer.stem

stops = set(map(lambda s: s.strip(),
                codecs.open("stopwords.dat","r","utf8").readlines()))

def tokenize(text):
    replacements = [("---"," "),
                    ("--"," "),
                    ("-", "")] # trying to capture multi-word keywords

    for (src,tgt) in replacements:
        text = text.replace(src,tgt)
    
    words = gensim.utils.simple_preprocess(text)

    return filter(lambda w: w not in stops, words)

def no_crlf(s):
    return ' '.join(s.split())

def parse(f):
    doc = json.loads(open(f).read())
    
    # if ('abs' not in doc): print file + " is missing an abstract"
    # if ('title' not in doc): print file + " is missing a title"

    conf = os.path.basename(os.path.dirname(f))
    title = doc.get('title',"").strip()
    authors = ' '.join(map(no_crlf, doc.get('authors',"")))
    meta = title + " - " + authors + " (" + conf + ")"
    return (meta.replace('"','\\"'),
            tokenize(title + " " + doc.get('abs',"")))

def load_docs(d):
    years = {}
    words = []

    for root in glob.glob(os.path.join(d,"*")):

        year = os.path.basename(root)
        years[year] = []
        
        for f in glob.glob(os.path.join(root,"*.txt")):
            title,doc = parse(f)

            doc = map(stem,doc)
            
            for word in doc:
                if word not in words:
                    words.append(word)
            
            years[year].append((title,doc))

    return (years,words)

def words_to_dict(words):
    d = {}
    index = 0
    
    for word in words:
        d[word] = index
        index = index + 1

    return d

def docs_to_bow(years,d):
    bows = {}

    for year in years:
        bows[year] = []

        for (title,doc) in years[year]:
            bow = {}
            for word in doc:
                wordid = d[word]
                bow[wordid] = bow.get(wordid,0) + 1

            bows[year].append((title,bow))

    return bows

def as_dat(bows, abs_of="abstracts.dat", doc_of="docs.dat"):
    out = open(abs_of,"w")

    doclist = codecs.open(doc_of,"w","utf8")

    for year in bows:
        for (title,bow) in bows[year]:
            doclist.write(title + u'\n')

            out.write(str(len(bow)))
            out.write(' ')
            for term in bow:
                out.write(str(term))
                out.write(':')
                out.write(str(bow[term]))
                out.write(' ')

            out.write('\n')

    doclist.close()
    out.close()

def as_vocab(words, vocab_of="vocab.dat"):
    out = codecs.open(vocab_of,"w","utf8")

    for word in words:
        out.write(word + u'\n')

    out.close()


def run(d,doc_file,dat_file,vocab_file):
    years,words = load_docs(d)

    d = words_to_dict(words)
    bows = docs_to_bow(years,d)
    as_dat(bows, abs_of=dat_file, doc_of=doc_file)
    as_vocab(words, vocab_of=vocab_file)

if __name__ == '__main__':
    args = dict(enumerate(sys.argv))
    d = args.get(1,"../scrape/main/")
    doc_file = args.get(2,"docs.dat")
    dat_file = args.get(3,"abstracts.dat")
    vocab_file = args.get(4,"vocab.dat")
    
    run(d,doc_file,dat_file,vocab_file)
