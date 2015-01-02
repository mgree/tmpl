#!/bin/bash

PREFIX=`date "+%Y-%m-%d_%H:%M"`

lda est 1/50  50 settings.txt abstracts.dat seeded ${PREFIX}_lda50 &
lda est 1/50  75 settings.txt abstracts.dat seeded ${PREFIX}_lda75 &
lda est 1/50 100 settings.txt abstracts.dat seeded ${PREFIX}_lda100 &
lda est 1/50 125 settings.txt abstracts.dat seeded ${PREFIX}_lda125 &
lda est 1/50 150 settings.txt abstracts.dat seeded ${PREFIX}_lda150 &
lda est 1/50 175 settings.txt abstracts.dat seeded ${PREFIX}_lda175 &
lda est 1/50 200 settings.txt abstracts.dat seeded ${PREFIX}_lda200 &

wait
echo "DONE, outputting topics..."

for i in ${PREFIX}_lda*; do
    python topics.py ${i}/final.beta vocab.dat 15 > ${i}_topics.txt
done

