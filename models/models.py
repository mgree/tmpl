import json
import gensim
import sys, os

class PoplCorpus(object):
    def __init__(self,dir):
        self.dir = dir

        self.documents = []
        for root,dirs,files in os.walk(self.dir):
            for file in filter(lambda f: f.endswith('.txt'), files):
                doc = json.loads(open(os.path.join(root,file)).read())
                
                # if ('abs' not in doc): print file + " is missing an abstract"
                # if ('title' not in doc): print file + " is missing a title"

                text = doc.get('title',"") + " " + doc.get('abs',"")
                self.documents.append(gensim.utils.simple_preprocess(text))
        
        self.metadata = None
        self.dictionary = gensim.corpora.Dictionary(self.documents)

    def __len__(self):
        return len(self.documents)
        
    def __iter__(self):
        for tokens in self.documents:
            yield self.dictionary.doc2bow(tokens)
        
    def get_texts(self):
        for doc in self.documents:
            yield doc

def model(dir, **kw):
    c = PoplCorpus(dir)

    # TODO stopwords/stemming
    
    lsi = gensim.models.lsimodel.LsiModel(corpus=c, id2word=c.dictionary, **kw)
    return (c,lsi)
