dl.py

What it does:
- In the current directory, parses through .xml files based on the argument provided (the names of conferences). Each .xml file contains information about all the papers presented at a given conference for a given year.
- Creates a directory based on the arguments provided (the specified output directory).
- Creates subdirectories using the following format: conference_name year (e.g. POPL 1973).
- Creates a .txt file in the subdirectory for each paper at the given conference for the given year.
- Each .txt file contains the conference, year, uniqueID, title, authors, abstract, and fulltext in JSON format.

How to run:
- cd into the directory with the .xml files that you want to use
- run following command: python ~/tmpl/raw/dl.py conference_name -o output_directory (e.g. python ~/tmpl/raw/dl.py POPL -o all_popl)

parse.py

What it does:
- Takes in a directory and parses through the files in the directory to produce a given number of topics based on key words.
- Ignores specified stopwords and replaces dashes with appropriate spacing.
- Updates docs.dat, abstracts.dat, and vocab.dat.
- In this project, runs with run_lda.sh.

How to run:
- cd into the directory with run_lda.sh (tmpl/lda)
- run following command: \CocoaLigature0 ./run_lda.sh directory list-of-number-of-topics (e.g. ./run_lda.sh ../../acm/proceedings/sigplan 25 50 100)

count.py

What it does:
- Takes in the following arguments: the file to be counted, the number of top words wanted, and the new output file
- Prints a list of the top words in the file from the highest count to the lowest count, and the count of each word
- Also outputs list into the new output file
- Used for debugging and cross-checking purposes

How to run:
- cd into the directory with the file to be counted
- run the following command: python ~/tmpl/raw/count.py count-file top-word output-file (e.g. python ~/tmpl/raw/count.py words.txt 100 count.txt)

spring 2016 history

- Worked on dl.py
- Created sigplan, a directory with POPL, PLDI, ICFP, LFP, FPCA, and OOPSLA, using dl.py
- Ran LDA on sigplan with 25, 50, and 100 topics
- Fixed dl.py to eliminate \\" that broke R script
- Ran LDA on sigplan, all_popl, and all_pldi multiple times with 10, 25, 50, and 100 topics
- Made changes in an attempt to eliminate garbage data, and ran LDA on sigplan, all_popl, and all_pldi after each change
	- Lowered em convergence factor from 1e-4 to 1e-5
	- Changed single quotes to double quotes and vice versa
	- Eliminated non-ASCII characters
	- Created count.py to compare word counts from newer and older POPL directories
- Had one run of all_popl with 10 topics that did not repeat

Remaining Hypotheses:
- Vocabulary size too large
- General issue with fulltext and parse.py

work in progress

- tfidf.py