import json
import gensim
import sys, os, glob
import codecs

stops = set(codecs.open("stopwords.dat","r","utf8"))

def tokenize(text):
    words = gensim.utils.simple_preprocess(text)

    return filter(lambda w: w not in stops, words)

def parse(file):
    doc = json.loads(open(file).read())
    
    # if ('abs' not in doc): print file + " is missing an abstract"
    # if ('title' not in doc): print file + " is missing a title"
    
    text = doc.get('title',"") + " " + doc.get('abs',"")
    return tokenize(text)

class PoplCorpus(object):
    def __init__(self,dir):
        self.dir = dir

        self.documents = []
        for root,dirs,files in os.walk(self.dir):
            for file in filter(lambda f: f.endswith('.txt'), files):
                self.documents.append(parse(os.path.join(root,file)))
        
        self.metadata = None
        self.dictionary = gensim.corpora.Dictionary(self.documents)

    def __len__(self):
        return len(self.documents)
        
    def __iter__(self):
        for tokens in self.documents:
            yield self.dictionary.doc2bow(tokens)
        
def on_snd_asc(v1,v2):
    return -cmp(v1[1],v2[1])
            
def tfidf(d):
    c = PoplCorpus(d)
    
    # tfidf transformation to get discover and normalize away stopwords
    tfidf = gensim.models.tfidfmodel.TfidfModel(corpus=c, id2word=c.dictionary)
    tc = tfidf[c]

    dfs = tfidf.dfs.items()
    dfs.sort(cmp=on_snd_asc)
    
    return (len(tc),tfidf.id2word,dfs)

num_docs,d,dfs = tfidf("../scrape/main")

threshold = num_docs / 5.0

for stop in map(lambda v: d[v[0]], filter(lambda v: v[1] > threshold, dfs)):
    print stop

