import sys
from utils import *

def to_float(s):
    if s == '':
        return 0.0
    else:
        return float(s)

def read_model(d, k):
    pfx = "%s_lda%d" % (d,k)
    
    betas = floats(read(os.path.join(pfx,"final.beta")))
    gammas = floats(read(os.path.join(pfx,"final.gamma")))
    docs = zip(read(d + "_docs.dat"), gammas)
    
    return (betas,docs)

def cmp_on(i):
    return lambda p1,p2: -cmp(p1[1][i],p2[1][i])

if (__name__ == '__main__'):
    args = dict(enumerate(sys.argv))
    pfx1 = args.get(1,"fulltext/ft")
    pfx2 = args.get(2,"abstracts/abs")
    k = int(args.get(3,20))
    num = int(args.get(4,50))
    
    (betas1, docs1) = read_model(pfx1, k)
    (betas2, docs2) = read_model(pfx2, k)

    counts = []
    for (i, (b1, b2)) in enumerate(zip(betas1, betas2)):

        # make copies
        top1 = list(docs1)
        top2 = list(docs2)

        # sort by weight in topic i
        compare = cmp_on(i)
        top1.sort(compare)
        top2.sort(compare)

        # get the top N of them
        top1 = [d[0] for d in top1[:num]]
        top2 = [d[0] for d in top2[:num]]

        # find the ones that are in common
        common = set([d for d in top1]).intersection([d for d in top2])

        print 'Topic %03d' % i
        print '---------'
        print "Found %d documents in common out of the top %d.\n" % (len(common),num)
        counts.append(len(common))
        
        # sort them by minimum sum of indices
        def by_index(d):
            i1 = top1.index(d)
            i2 = top2.index(d)
            return (d,i1 + i2,i1,i2)
        common = map(by_index, list(common))
        common.sort(lambda d1,d2: cmp(d1[1],d2[1]))

        for (d,_,i1,i2) in common:
            print "%s (#%d/#%d)" % (d,i1,i2)

        print "\n"

    print 'Counts'
    print '\n'.join(map(str,counts))

        
