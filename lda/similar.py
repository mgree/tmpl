from utils import *

def run(docs,gammas,query,num):
    papers = zip(docs,map(lambda s: map(float,s.split()), gammas))

    tgt = filter(lambda (t,gs): query in t.lower(), papers)

    if len(tgt) == 0:
        print "Couldn't find a paper matching " + query
        sys.exit(-1)
    elif len(tgt) > 1:
        print "Found too many papers:"
        for (title,gs) in tgt:
            print '  %s' % title
        sys.exit(-1)

    tgt = tgt[0]
    papers = map(lambda s: (distance(s[1],tgt[1]),s), papers)
    papers.sort(lambda x,y: cmp(x[0],y[0]))

    if papers[0][1] != tgt:
        print ">>> Huh, would have expected the first paper to be the one we queried."
        print '%s (%d)' % (papers[0][1][0],papers[0][0])

    for (d,(doc,gs)) in papers[1:num+1]:
        print '%s (%d)' % (doc,d)   

if (__name__ == '__main__'):
    args = dict(enumerate(sys.argv))
    query = args.get(1,"BI as an Assertion Language for Mutable Data Structures").lower()
    num = int(args.get(2,10))
    prefix = args.get(3,"2015-01-06_11:06")
    k = args.get(4,"20")
    
    lda = prefix + "_lda" + k
    gamma = read(os.path.join(lda,"final.gamma"))
    docs = read(prefix + "_docs.dat")

    run(docs,gamma,query,num)
