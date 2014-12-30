import json
import gensim
import sys, os, glob

def parse(file):
    doc = json.loads(open(file).read())
    
    # if ('abs' not in doc): print file + " is missing an abstract"
    # if ('title' not in doc): print file + " is missing a title"
    
    text = doc.get('title',"") + " " + doc.get('abs',"")
    return (text,gensim.utils.simple_preprocess(text))
   

class PoplCorpus(object):
    def __init__(self,dir):
        self.dir = dir

        self.documents = []
        for root,dirs,files in os.walk(self.dir):
            for file in filter(lambda f: f.endswith('.txt'), files):
                self.documents.append(parse(os.path.join(root,file))[1])
        
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
    print "Loading SIGPLAN corpus..."
    c = PoplCorpus(dir)
    
    # tfidf transformation to get discover and normalize away stopwords
    print "Calculating TF-IDF..."
    tfidf = gensim.models.tfidfmodel.TfidfModel(corpus=c, id2word=c.dictionary)
    tc = tfidf[c]

    # run latent semantic indexing to train some topics
    print "Running LSI..."
    lsi = gensim.models.lsimodel.LsiModel(corpus=tc, id2word=c.dictionary, **kw)

    print "Assembling topics..."
    topics = {}
    years = {}
    # for each iteration of POPL
    for root in glob.glob(os.path.join(dir,"POPL*")):
        year = os.path.basename(root)
        
        print "Processing " + year
        topics[year] = []
        years[year] = {}
        for doc in glob.glob(os.path.join(root,"*.txt")):
            tokens = c.dictionary.doc2bow(parse(doc)[1])
            vec = lsi[tokens]
            topics[year].append(vec)

            # just grab the positive contributions
            for id,n in vec:
                years[year][id] = years[year].get(id,0) + max(n,0)

    s = {}
    for year in years:
        s[year] = []
        for id in years[year]:
            s[year].append(years[year][id])
                
    return (c,tfidf,lsi,topics,years,s)

def POPLdocs(dict,dir):
    years = {}
    for root in glob.glob(os.path.join(dir,"POPL*")):

        year = os.path.basename(root)
        years[year] = []
        
        for f in glob.glob(os.path.join(root,"*.txt")):
            text,doc = parse(f)
            bow = dict.doc2bow(doc)
            years[year].append((text,bow))

    return years

def cmp_on_topics(v1,v2):
    return cmp(v1[1],v2[1])


def summary(lsi,years):
    summaries = {}
    
    for year in years:
        summaries[year] = []
        
        for text,bow in years[year]:
            topics = lsi[bow]
                        
            topics.sort(cmp=cmp_on_topics, reverse=True)
            summaries[year].append((text,bow,topics))

    return summaries

lsi = gensim.models.lsimodel.LsiModel.load("sigplan.lsi")
d = lsi.id2word
docs = POPLdocs(d,"scrape/full")
s = summary(lsi,docs)
        
def topics(text, threshold = 0.25):
    bow = d.doc2bow(gensim.utils.simple_preprocess(text))
    tp = lsi[bow]
    tp.sort(cmp=cmp_on_topics, reverse=True)

    return set(map(lambda v: v[0], filter(lambda v: v[1] > threshold,tp)))
    
def contribution(v,ts):
    contrib = 0

    vs = dict(v[2])
    
    for t in ts:
        contrib = contrib + max(vs.get(t,0),0)
    return contrib

def summary_by_topic(s,topic1,topic2):
    summaries = {}
    
    for year in s:
        summaries[year] = { 't1': 0, 't2': 0 }
        
        for v in s[year]:
            summaries[year]['t1'] = summaries[year]['t1'] + contribution(v,topic1)
            summaries[year]['t2'] = summaries[year]['t2'] + contribution(v,topic2)

    return summaries

def compare_topics(s,text1,text2):
    t1 = topics(text1)
    t2 = topics(text2)

    i = t1.intersection(t2)
    t1.difference_update(i)
    t2.difference_update(i)

    return summary_by_topic(s,t1,t2)

def as_csv(of,s,topic1,topic2):
    stdout = sys.stdout
    sys.stdout = open(of,"w")
    
    print "Year," + topic1 + "," + topic2
    for year in s:
        print year + "," + str(s[year]['t1']) + "," + str(s[year]['t2'])
    sys.stdout.close()

    sys.stdout = stdout

# compare FP and OO
fp_text = "functional programming higher-order function application applicative abstraction pure lambda arrow type immutable algebraic datatype scheme ml ocaml sml sml/nj racket haskell miranda lazy eager cbv call by value call by name call by need"
oo_text = "object-oriented programming object class prototype instance field method application inheritance hierarchy inherited interface self modula-3 java c++ scala virtual table abstract"
st = compare_topics(s,fp_text,oo_text)
as_csv('fpvsoo.csv',st,'FP','OO')
