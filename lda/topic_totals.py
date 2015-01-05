import codecs
import re
import sys
from operator import add
from math import log

def quote(s):
    return '"' + s + '"'

title = re.compile(u'(.*) \((.*) (\\d*)\)$')
def split_title(doc):
    m = title.match(doc)
    return [m.group(3),quote(m.group(2)),quote(m.group(1))]


def run(raw_gammas):
    gammas = map(lambda s: map(float,s.split()), raw_gammas)

    totals = gammas[0]

    for g in gammas[1:]:
        totals = map(add,totals,g)

    print "Topic Number,Total Weight,Log(Total Weight)"
    for i in range(0,len(totals)):
        print str(i) + "," + str(totals[i]) + "," + str(log(totals[i]))

def read(f, enc="utf8"):
    return map(lambda s: s.strip(),codecs.open(f,"r",enc).readlines())

if (__name__ == '__main__'):
    args = dict(enumerate(sys.argv))
    gammas = read(args.get(1,"final.gamma"))

    run(gammas)
