from utils import *
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

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
    topic1 = int(args.get(1,"7"))
    topic2 = int(args.get(2,"9"))
    topic3 = int(args.get(3,"12"))
    prefix = args.get(4,"2015-01-06_11:06")
    k = args.get(5,"20")
    
    lda = prefix + "_lda" + k
    gammas = map(lambda s: map(float, s.split()),
                 read(os.path.join(lda,"final.gamma")))

    def select(i):
        return map(lambda g: g[i], gammas)

    xs = select(topic1)
    ys = select(topic2)
    zs = select(topic3)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(xs,ys,zs)

    ax.set_xlabel('Topic ' + str(topic1))
    ax.set_ylabel('Topic ' + str(topic2))
    ax.set_zlabel('Topic ' + str(topic3))

    ax.set_xbound(lower=min(xs), upper=max(xs))
    ax.set_ybound(lower=min(ys), upper=max(ys))
    ax.set_zbound(lower=min(zs), upper=max(zs))

    plt.show()


