import codecs
import re
import sys,os

def mean(l):
    return sum(l) / float(len(l))

def run(docs,betas,gammas,vocab,num):
    papers = zip(docs,map(lambda s: map(float,s.split()), gammas))

    num_topics = len(betas)    
    for i,raw_betas in enumerate(betas):
        print 'Topic %03d' % i
        print '---------'

        bs = map(float, raw_betas.split())
        print 'Words (mean weight: %f, min weight: %f)' % (mean(bs),min(bs))

        words = range(len(bs))
        words.sort(lambda x,y: -cmp(bs[x],bs[y]))

        for word in words[:num]:
            print '  %s (%f)' % (vocab[word], bs[word])

        print '---------'
        print 'Papers'

        papers.sort(lambda p1,p2: -cmp(p1[1][i],p2[1][i]))

        # topics per document
        for p in papers[:num]:
            print p[0]
            print "  %f" % p[1][i]

        if i + 1 != num_topics:
            print "\n"

def read(f, enc="utf8"):
    return map(lambda s: s.strip(),codecs.open(f,"r",enc).readlines())

if (__name__ == '__main__'):
    args = dict(enumerate(sys.argv))
    prefix = args.get(1,"2015-01-05_23:21")
    k = args.get(2,"200")
    num = int(args.get(3,10))
    
    lda = prefix + "_lda" + k
    beta = read(os.path.join(lda,"final.beta"))
    gamma = read(os.path.join(lda,"final.gamma"))
    docs = read(prefix + "_docs.dat")
    vocab = read(prefix + "_vocab.dat")

    run(docs,beta,gamma,vocab,num)
