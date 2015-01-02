#!/bin/bash

lda est 1/50 50 settings.txt abstracts.dat seeded lda50 &
lda est 1/50 75 settings.txt abstracts.dat seeded lda75 &
lda est 1/50 100 settings.txt abstracts.dat seeded lda100 &
lda est 1/50 125 settings.txt abstracts.dat seeded lda125 &
lda est 1/50 150 settings.txt abstracts.dat seeded lda150 &
lda est 1/50 175 settings.txt abstracts.dat seeded lda175 &
lda est 1/50 200 settings.txt abstracts.dat seeded lda200 &

wait
echo "DONE, outputting topics..."

for i in lda*; do
    python topics.py ${i}/final.beta vocab.dat 15 > ${i}_topics.txt
done

