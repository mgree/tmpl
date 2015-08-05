#!/bin/bash

for f in `find $1 -name \*.pdf`; do
    python ~/sigplan/www/backend/infer.py -m fulltext ${f}
done

OUT="$1.dat"
rm ${OUT}
touch ${OUT}

for f in $1/*-gamma.dat; do
    (echo -n "paper,${f}," && sed -e "s/ /,/g" ${f}) >> ${OUT}
done

for f in $1/related/*-gamma.dat; do
    (echo -n "cite,${f}," && sed -e "s/ /,/g" ${f}) >> ${OUT}
done
