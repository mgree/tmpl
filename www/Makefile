SRC = infer.py utils.py

.PHONY : test deploy

test : $(SRC)
	python infer.py fh.pdf

deploy : $(SRC) settings.txt abstracts fulltext
	rsync -Cavr . weaselhat:tmpl

clean :
	rm -f *~ *.pyc *-gamma.dat *-lda-lhood.dat

