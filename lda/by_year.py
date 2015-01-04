import codecs
import re
import sys
from operator import add

def quote(s):
    return '"' + s + '"'

title = re.compile(u'(.*) \((.*) (\\d*)\)$')
def split_title(doc):
    m = title.match(doc)
    return [m.group(3),m.group(2),quote(m.group(1))]


def run(docs,gammas,normalize=True):
    # show the header
    num_topics = len(gamma[0].split())

    # topics per document, collecting conference names
    years = {}
    all_years = set()
    confs = set()
    for d,g in zip(docs, gammas):
        year,conf,title = split_title(d)
        ts = map(float,g.split())

        if year not in years:
            years[year] = {}

        confs.add(conf)
        if conf not in years[year]:
            years[year][conf] = [1] + ts
        else:
            years[year][conf] = map(add, [1] + ts, years[year][conf])

    # fix a conference order
    conf_order = list(confs)
    conf_order.sort()

    # print out the header
    header = ["Year"]
    for conf in conf_order:
        header += [conf + " # of papers"] + [conf + " Topic " + str(i) for i in range(0,num_topics)]
    print ','.join(header)

    # print out the topics
    for year in years:
        tvals = []
        for conf in conf_order:
            if conf in years[year]:
                if normalize:
                    ts = years[year][conf]
                    num_papers = ts[0]

                    for i in range(1,len(ts)):
                        ts[i] = ts[i] / float(num_papers)

                    tvals += ts
                else:
                    tvals += years[year][conf]
            else:
                tvals += [0] + ["" for i in range(0,num_topics)]

        print ','.join([year] + map(str,tvals))
        

def read(f, enc="utf8"):
    return map(lambda s: s.strip(),codecs.open(f,"r",enc).readlines())

if (__name__ == '__main__'):
    args = dict(enumerate(sys.argv))
    gamma = read(args.get(1,"final.gamma"))
    docs = read(args.get(2,"../docs.dat"))
    nflag = args.get(3,"--normalize")
    
    run(docs, gamma, normalize=(nflag == "--normalize"))
