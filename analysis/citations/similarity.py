from utils import *
import codecs

def load_by_year(f, num_confs, normalized = True):
    raw_by_year = from_csv(read(f))

    num_topics = ((len(raw_by_year[0]) - 1) / num_confs) - 1

    confs = []
    for i in range(num_confs):
        confs.append(raw_by_year[0][1 + (i * (num_topics + 1))].split()[0])

    years = {}
    for y in raw_by_year[1:]:
        year = y[0]
        idx = 1
        
        for conf in confs:
            num_papers = int(y[idx])
            if num_papers > 0:
                aggregate = map(float, y[idx+1:idx+1+num_topics])

                key = conf + ' ' + year
                if normalized:
                    years[key] = aggregate
                else:
                    years[key] = [topic / num_papers for topic in aggregate]

            idx += num_topics + 1

    return years

def load_vita(f):
    raw_vita = [map(float, p[2:]) for p in from_csv(read(f))]

    vita = [0 for x in range(len(raw_vita[0]))]
    for p in raw_vita:
        for i in range(0,  len(p)):
            vita[i] += p[i]
    vita = [topic / len(raw_vita) for topic in vita]

    return vita

if __name__ == '__main__':
    args = sys.argv[1:]

    num_confs = int(args[0])
    by_year = load_by_year(args[1], num_confs)
    vita = load_vita(args[2])

    years = [(y[0], kl_divergence(vita, y[1]), y[1]) for y in by_year.iteritems()]
        
    years.sort(cmp=lambda y1, y2: cmp(y1[1], y2[1]))

    for y in years:
        print '%s (%f)' % (y[0], y[1])
