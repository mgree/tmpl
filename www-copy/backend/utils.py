import codecs
import re
import sys
import os
import math
import unicodedata

def mean(l):
    return sum(l) / float(len(l))

def read(f, enc="utf8"):
    return map(lambda s: s.strip(),codecs.open(f,"r",enc).readlines())

def floats(l):
    return [map(float,s.split()) for s in l]

def squared(v):
    return v * v

def to_probability(v):
    total = float(sum(v)) + sys.float_info.epsilon
    
    return [vi / total for vi in v]

def kl_asym(p, q):
    return sum([pi * math.log(pi / qi) for (pi,qi) in zip(p,q)])

def kl_divergence(p, q):
    pn = to_probability(p)
    qn = to_probability(q)
    
    return kl_asym(pn,qn) + kl_asym(qn,pn)

def distance(s1,s2):
    return math.sqrt(sum([squared(v1 - v2) for v1,v2 in zip(s1,s2)]))

def csv(l):
    return ','.join(map(str,l))

def from_csv(l):
    return [s.split(',') for s in l]

def to_csv(f,l):
    codecs.open(f,"w","utf8").write('\n'.join([','.join(map(unicode,s)) for s in l]))


def quote(s):
    return '"' + s.replace('\\', '\\\\').replace('"','\\"') + '"'

# the following definitions are taken from gensim.utils
# see https://github.com/piskvorky/gensim/blob/develop/gensim/utils.py

PAT_ALPHABETIC = re.compile('(((?![\d])\w)+)', re.UNICODE)

def any2unicode(text, encoding='utf8', errors='strict'):
    if isinstance(text, unicode):
        return text
    return unicode(text, encoding, errors=errors)
to_unicode = any2unicode

def tokenize(text, lowercase=False, deacc=False, errors="strict", to_lower=False, lower=False):
    lowercase = lowercase or to_lower or lower
    text = to_unicode(text, errors=errors)
    if lowercase:
        text = text.lower()
    if deacc:
        text = deaccent(text)
    for match in PAT_ALPHABETIC.finditer(text):
        yield match.group()

def preprocess(doc, deacc=False, min_len=2, max_len=15):
    tokens = [token for token in tokenize(doc, lower=True, deacc=deacc, errors='ignore')
            if min_len <= len(token) <= max_len and not token.startswith('_')]
    return tokens
