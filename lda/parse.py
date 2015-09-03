import json
import sys, os, glob
import codecs

import utils
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
    
    words = utils.preprocess(text)

    return filter(lambda w: w not in stops, words)

def no_crlf(s):
    return ' '.join(s.split())

def parse(f):
    doc = json.load(open(f))
    
    # if ('abs' not in doc): print file + " is missing an abstract"
    # if ('title' not in doc): print file + " is missing a title"

    conf = os.path.basename(os.path.dirname(f))
    title = doc.get('title',"").strip()
    authors = ' '.join(map(no_crlf, doc.get('authors',"")))
    meta = title + " - " + authors + " (" + conf + ")"

    (base,_) = os.path.splitext(f)
    pdf = base + "-fulltext.txt"
    if os.path.exists(pdf):
        # we've got fulltext
        text = open(pdf).read()
    elif 'abs' in doc:
        # just an abstract
        text = title + " " + doc.get('abs',"")
    else:
        print "Couldn't find an abstract or a PDF for " + title + " (" + base + ")"
        text = title

    return (meta.replace('"','\\"'), tokenize(text))

def load_docs(d):
    years = {}
    words = set()

    for root in glob.glob(os.path.join(d,"*")):

        year = os.path.basename(root)

        years[year] = []
        
        for f in glob.glob(os.path.join(root,"*.txt")):
            if "fulltext" in os.path.basename(f):
                continue
            
            title,doc = parse(f)
            doc = map(stem,doc)
            words.update(doc)
                    
            years[year].append((title,doc))

    return (years,words)

def words_to_dict(words):
    return dict(zip(words, range(0, len(words))))

def make_bow(doc,d):
    bow = {}
    
    for word in doc:
        wordid = d[word]
        bow[wordid] = bow.get(wordid,0) + 1

    return bow

def docs_to_bow(years,d):
    bows = {}

    for year in years:
        bows[year] = []

        for (title,doc) in years[year]:
            bows[year].append((title,make_bow(doc,d)))

    return bows

def years_to_bow(years,d):
    bows = {}

    for year in years:
        year_doc = []
        for (title,doc) in years[year]:
            year_doc += doc

        bows[year] = [(year,make_bow(year_doc,d))] # list for compatibility w/docs_to_bow

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


by_year = False
def run(doc_dir,doc_file,dat_file,vocab_file):
    global by_year
    
    years,words = load_docs(doc_dir)

    d = words_to_dict(words)
    #print d.keys()
    if by_year:
        print "Running by year"
        bows = years_to_bow(years,d)
    else:
        bows = docs_to_bow(years,d)
    as_dat(bows, abs_of=dat_file, doc_of=doc_file)
    as_vocab(words, vocab_of=vocab_file)

if __name__ == '__main__':
    args = dict(enumerate(sys.argv))
    d = args.get(1,"../raw/abs/icfp/")
    doc_file = args.get(2,"docs.dat")
    dat_file = args.get(3,"abstracts.dat")
    vocab_file = args.get(4,"vocab.dat")
    by_year = args.get(5,"") == "--by-year"
    
    run(d,doc_file,dat_file,vocab_file)
