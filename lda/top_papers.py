import codecs
import re
import sys

def quote(s):
    return '"' + s + '"'

title = re.compile(u'(.*) \((.*) (\\d*)\)$')
def split_title(doc):
    m = title.match(doc)
    return [m.group(3),quote(m.group(2)),quote(m.group(1))]


def run(docs,gammas,topic,num_papers):
    print "Showing top " + str(num_papers) + " papers for topic #" + str(topic)

    papers = zip(docs,map(lambda s: map(float,s.split()), gammas))
    def on_topic(v1,v2):
        return cmp(v1[1][topic],v2[1][topic])
    papers.sort(cmp=on_topic, reverse=True)
    
    # topics per document
    for p in papers[:num_papers]:
        print p[0]
        print "\t" + str(p[1][topic])
        

def read(f, enc="utf8"):
    return map(lambda s: s.strip(),codecs.open(f,"r",enc).readlines())

if (__name__ == '__main__'):
    args = dict(enumerate(sys.argv))
    gamma = read(args.get(1,"final.gamma"))
    docs = read(args.get(2,"../docs.dat"))
    topic = int(args.get(3,0))
    num_papers = int(args.get(4,10))

    run(docs,gamma,topic,num_papers)
