import sys
from utils import *

def cma(years):
    avg = years[0]
    
    for y in range(1,len(years)):
        for i in range(0,len(years[y])):
            avg[i] += (years[y][i] - avg[i]) / y
        yield list(avg) # gotta make a copy

def wma(years):
    avg = years[0]
    
    for y in range(1,len(years)):
        for i in range(0,len(years[y])):
            avg[i] += .75*(years[y][i] - avg[i])
        yield list(avg) # gotta make a copy!
        
def to_float(s):
    if s == '':
        return 0.0
    else:
        return float(s)

def error(years, avgs, num_confs, num_topics):    
    errs = []
    for y in range(1,len(years)): # gotta skip the first one
        cs = []
        for c in range(0,num_confs):
            start = 1 + (num_topics+1)*c
            end = start + num_topics

#            if y == 1:
#                print years[y][start:end], avgs[y-1][start:end]
            cs.append(distance(years[y][start:end], avgs[y-1][start:end]))
        errs.append(cs)

    return errs

if (__name__ == '__main__'):
    years = read(sys.argv[1])
    num_topics = int(sys.argv[2])

    header = years[0].split(',')
    years = years[1:]

    years = map(lambda r: map(to_float,r.split(',')), years)
    years.sort(lambda r1,r2: cmp(r1[0],r2[0]))

    num_confs = (len(years[0]) - 1) / (num_topics + 1)

    conf_names = [header[1 + i*(num_topics + 1)].split()[0] for i in range(0,num_confs)]

    ecum = error(years, list(cma(years)), num_confs, num_topics)
    eexp = error(years, list(wma(years)), num_confs, num_topics)

    print csv(["Year"] +
              [c + " Error (CMA)" for c in conf_names] +
              [c + " Error (EMA)" for c in conf_names])
    for y in range(1,len(years)): # gotta skip the first one
        year = years[y][0]

        print csv([int(year),csv(ecum[y-1]),csv(eexp[y-1])])



    
