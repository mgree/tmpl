import codecs
import re
import sys

def quote(s):
    return '"' + s + '"'

title = re.compile(u'(.*) \((.*)\)$')
def split_title(doc):
    m = title.match(doc)
    return [quote(m.group(1)),quote(m.group(2))]


def run(docs,gammas):
    # show the header
    num_topics = len(gamma[0].split())
    print ','.join(["Title","Conference"] +
                   ["Topic " + str(i) for i in range(0,num_topics)])

    # topics per document
    for d,g in zip(docs, gammas):
        print ','.join(split_title(d) + g.split())
        

def read(f, enc="utf8"):
    return map(lambda s: s.strip(),codecs.open(f,"r",enc).readlines())

if (__name__ == '__main__'):
    args = dict(enumerate(sys.argv))
    gamma = read(args.get(1,"final.gamma"))
    docs = read(args.get(2,"../docs.dat"))

    run(docs, gamma)
