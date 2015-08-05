from utils import *
import random
import codecs

# metric = distance
metric = kl_divergence

def rs(p,i):
    acc = []
    for (j,pd) in enumerate(p):
        acc += [[str(i),
                 "random"+str(j+1),
                 d[2].replace(" ","").replace('"',''),
                 str(metric(map(float,papers[i]),map(float,d[-20:])))]
                for d in pd]
    return acc

def take(l,num):
    return [l.pop() for i in range(0,num)]

cites = [24,15,27,36]

unified = from_csv(read("unified.dat"))
papers = dict([(1,unified[1][-20:]),
               (2,unified[26][-20:]),
               (3,unified[41][-20:]),
               (4,unified[69][-20:])])

dist = [unified[0] + ["Distance"]] + \
       [d + [metric(map(float,papers[int(d[0])]),
                      map(float,d[-20:]))]
        for d in unified[1:]]
to_csv("dist.dat",dist)

abstr = from_csv(read("../analysis/ft_lda20.csv"))[1:]

#papers = dict([(1,dist[1][-21:-1]),
#               (2,dist[26][-21:-1]),
#               (3,dist[41][-21:-1]),
#               (4,dist[69][-21:-1])])

random.shuffle(abstr)

ps = [[take(abstr,cites[i-1]) for j in range(0,5)] for i in [1,2,3,4]]

ds = [rs(ps[i-1],i) for i in [1,2,3,4]]

dist_rand = [d[0:3] + [d[-1]] for d in dist] + ds[0] + ds[1] + ds[2] + ds[3]

to_csv("dist_rand.dat",dist_rand)
