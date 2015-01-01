import json
import gensim
import sys, os, glob
import codecs
import stop_words

stops = stop_words.get_stop_words("english")
def tokenize(text):
    words = gensim.utils.simple_preprocess(text)

    return filter(lambda w: w not in stops, words)

def parse(file):
    doc = json.loads(open(file).read())
    
    # if ('abs' not in doc): print file + " is missing an abstract"
    # if ('title' not in doc): print file + " is missing a title"

    title = doc.get('title',"")
    text = title + " " + doc.get('abs',"")
    return (title,tokenize(text))

def POPLdocs(of,d):
    years = {}
    words = []

    doclist = codecs.open(of,"w","utf8")
                          
    for root in glob.glob(os.path.join(d,"POPL*")):

        year = os.path.basename(root)
        years[year] = []
        
        for f in glob.glob(os.path.join(root,"*.txt")):
            title,doc = parse(f)

            doclist.write(title + u'\n')
            
            for word in doc:
                if word not in words:
                    words.append(word)
            
            years[year].append(doc)

    doclist.close()
    return (years,words)

def words_to_dict(words):
    d = {}
    index = 0
    
    for word in words:
        index = index + 1
        d[word] = index

    return d

def docs_to_bow(years,d):
    bows = {}

    for year in years:
        bows[year] = []

        for doc in years[year]:
            bow = {}
            for word in doc:
                wordid = d[word]
                bow[wordid] = bow.get(wordid,0) + 1

            bows[year].append(bow)

    return bows

def as_dat(of, bows):
    out = open(of,"w")
    
    for year in bows:
        for bow in bows[year]:
            out.write(str(len(bow)))
            out.write(' ')
            for term in bow:
                out.write(str(term))
                out.write(':')
                out.write(str(bow[term]))
                out.write(' ')

            out.write('\n')

    out.close()

def as_vocab(of, words):
    out = codecs.open(of,"w","utf8")

    for word in words:
        out.write(word + u'\n')

    out.close()
