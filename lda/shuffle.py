import sys
import random
from utils import *


if __name__ == '__main__':
    args = dict(enumerate(sys.argv[1:]))
    pfx1 = args.get(0, "2015-03-10_09:16")
    pfx2 = args.get(0, "2015-03-11_12:17")

    ds1 = filter(lambda s:
                 "1991" not in s[1] and
                 "POPL 1996" not in s[1] and
                 "POPL 1997" not in s[1] and
                 "POPL 1998" not in s[1] and
                 "POPL 1998" not in s[1],
                 enumerate(read(pfx1 + "_docs.dat")))
    ds2 = read(pfx2 + "_docs.dat")

    j = []
    for (k1,v1) in ds1:
        try:
            k2 = ds2.index(v1)
            j.append((k1,k2,v1))
        except ValueError:
            continue
        
    random.seed()
    random.shuffle(j)

    print '\n'.join(map(str,j[:20]))
    
    out1 = open(pfx1 + "_ldaseeds.txt", "w")
    out1.write('\n'.join(map(lambda r: str(r[0]), j)))
    out1.close()
               
    out2 = open(pfx2 + "_ldaseeds.txt", "w")
    out2.write('\n'.join(map(lambda r: str(r[1]), j)))
    out2.close()

                
