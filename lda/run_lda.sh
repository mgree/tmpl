#!/bin/bash

if test $# -ne 0;
then
    KS="$*";
else
    KS="50 75 100 125 150 175 200"
fi

PREFIX=`date "+%Y-%m-%d_%H:%M"`
START=`date "+%Y-%m-%d %H:%M"`

echo "PARSING"

python parse.py

for dat in abstracts.dat vocab.dat docs.dat; do
    mv ${dat} ${PREFIX}_${dat}
done

# we don't want to lose this one!
cp stopwords.dat ${PREFIX}_stopwords.dat

echo "RUNNING LDA"

ABS=${PREFIX}_abstracts.dat

for k in ${KS}; do
    lda est 1/50 ${k} settings.txt ${ABS} seeded ${PREFIX}_lda${k} &
    echo ${PREFIX}_lda${k} >>../out/.gitignore
done

wait
echo "PROCESSING TOPICS"

for k in ${KS}; do
    python debug_topics.py ${PREFIX} ${k} > ${PREFIX}_lda${k}_topics.txt
done

echo "GENERATING CSV"

for i in ${PREFIX}_lda*; do
    test -d ${i} && python post.py ${i}/final.gamma ${PREFIX}_docs.dat > ${i}.csv
    test -d ${i} && python by_year.py ${i}/final.gamma ${PREFIX}_docs.dat > ${i}_by_year.csv
done

echo "MOVING TO OUTPUT DIRECTORY"
mv ${PREFIX}* ../out

echo "DONE"
echo All done. Started at ${START}, done at `date "+%Y-%m-%d %H:%M"`.
