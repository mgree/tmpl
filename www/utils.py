import codecs
import re
import sys
import os
import math

def mean(l):
    return sum(l) / float(len(l))

def read(f, enc="utf8"):
    return map(lambda s: s.strip(),codecs.open(f,"r",enc).readlines())

def squared(v):
    return v * v

def distance(s1,s2):
    return math.sqrt(sum([squared(v1 - v2) for v1,v2 in zip(s1,s2)]))
