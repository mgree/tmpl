# Programs

The main program to run is `run_lda.sh`. You'll need to have installed
[LDA-C](http://www.cs.princeton.edu/~blei/lda-c/index.html),
[gensim](https://radimrehurek.com/gensim/), and
[nltk](http://www.nltk.org/). You'll need to have installed, via
`nltk.download()` in Python, the stopword list and wordnet database.

You may need to set `PYTHONIOENCODING=utf8` when running some of these
scripts, but perhaps not on platforms other than OS X.

* `run_lda.sh`

This program ties together all of the programs described below to
create a 'run' of analysis. All of the files for a run share a
timestamp prefix of the form `2015-01-03_13:26`. I'll just write `PFX`
below.

The general plan for a run is:
  1. Use `parse.py` to parse the scraped data into
     `PFX_abstracts.dat`, `PFX_docs.dat`, and `PFX_vocab.dat`.
  2. Run LDA-C in parallel for a variety of numbers of topics (by
     default, K={50,75,...,200}). _This can take an hour or two
     on my 4-core i7._ LDA-C generates a directory named
     `PFX_ldaK` for each K.
  3. Use `topics.py` to process the output from LDA-C to find the
     top words for each topic; these go into `PFX_ldaK_topics.txt`.
  4. Use `post.py` to build a CSV with the topic assignments for
     each document in `PFX_ldaK.csv`.
  5. Use `by_year.py` to aggregate topics per conference per year,
     generating `PFX_ldaK_by_year.csv`. These aggregate topic
     weights are normalized by the number of papers in the
     conference.

`run_lda.sh` takes the list of numbers of topics as its arguments. By
default, it runs as if it were invoked as:

```
./run_lda.sh 50 75 100 125 150 175 200
```


* `parse.py`

This script reads the scraped data and generates three files:

  ** `abstracts.dat`, which represents each document as a bag of words
  ** `docs.dat`, which tracks each document's name, conference, and year
  ** `vocab.dat`, which maps word ids to actual words
  
By default, `parse.py` generates prefixless `.dat` files, which
`run_lda.sh` renames to the prefixed form.

* `topics.py`

This script has been copied wholesale from David Blei's LDA-C. It
looks up the assignments in `PFX_ldaK/final.beta` and correlates the
word ids in each topic with the mapping `PFX_vocab.dat`.

* `post.py`

This script combines the information in `PFX_ldaK/final.gamma` with
the document names recorded in `PFX_docs.dat`.

The CSV file is output with K + 3 columns: the year, the conference,
the document title, and then one column for each topic.

* `by_year.py`

This script aggregates information in `PFX_ldaK/final.gamma` with the
conference and year information stored in `PFX_docs.dat`. It sums up
the topic values, grouping by conference and year---and, by, default,
normalizing the topic values by the number of papers in that year's
conference.

The CSV file is output with C*(K+1) + 1 columns, where C is the number
of conferences: the year, and then for each conference, there is a
column for the number of papers that year and a column for each of the
K topics.

* `top_papers.py`

This script lists the top papers for a given topic. It should be run
manually, as in:

```
  python top_papers.py PFX_ldaK/final.gamma PFX_ldaK_docs.dat 0-based-topic# num-papers
```

* `similar.py`

This script finds papers that are simialr to one given by a query. By
default, it finds papers similar to Peter O'Hearn's seminal 2001 work,
_BI as an Assertion Language for Mutable Data Structures_. For our LDA
model with k=20, we find:

```
Proof search for propositional abstract separation logics via labelled sequents - Zhé Hóu, Ranald Clouston, Rajeev Goré, Alwen Tiu (POPL 2014) (4)
Context logic as modal logic: completeness and parametric inexpressivity - Cristiano Calcagno, Philippa Gardner, Uri Zarfaty (POPL 2007) (4)
Verifying infinite state processes with sequential and parallel composition - Ahmed Bouajjani, Rachid Echahed, Peter Habermehl (POPL 1995) (6)
First order programming logic - Robert Cartwright, John McCarthy (POPL 1979) (6)
Verified decision procedures for MSO on words based on derivatives of regular expressions - Dmitriy Traytel, Tobias Nipkow (ICFP 2013) (8)
Axiomatic definability and completeness for recursive programs - Albert R. Meyer, John C. Mitchell (POPL 1982) (8)
Symbolic Algorithms for Language Equivalence and Kleene Algebra with Tests - Damien Pous (POPL 2015) (10)
The power of parameterization in coinductive proof - Chung-Kil Hur, Georg Neis, Derek Dreyer, Viktor Vafeiadis (POPL 2013) (10)
Conjugate Hylomorphisms -- Or: The Mother of All Structured Recursion Schemes - Ralf Hinze, Nicolas Wu, Jeremy Gibbons (POPL 2015) (12)
Shape analysis with inductive recursion synthesis - Bolei Guo, Neil Vachharajani, David I. August (PLDI 2007) (12)
```

The number at the end is the Euclidean distance of the topic vectors
of the two documents.

To run the script on another document, write a search term, like:

  $ python similar.py "Your title search term here"

You can ask the script to print more similar papers by giving a number
after the search term. For example,

  $ python similar.py "edit lenses" 20

will print out the 20 most similar papers to Hofmann, Wagner, and
Pierce's POPL 2012 paper.

# File formats

There are many file formats involved in all of these tools, all only
somewhat documented.

* scraped data

By default the scraped data is kept in `../scrape/main`. It's not
included in this repository for copyright reasons.

The data is structured such that each conference/year is a directory
in `../scrape/main` holding JSON data on each abstract. For example,
`../scrape/main/POPL 2015/15.txt` contains the text:

```
{"title":"Space-Efficient Manifest Contracts",
 "authors":["Michael Greenberg"],
 "abs":"The standard algorithm for higher-order contract checking can
  lead to unbounded space consumption and can destroy tail recursion,
  altering a program's asymptotic space complexity. While space
  efficiency for gradual types---contracts mediating untyped and
  typed code---is well studied, sound space efficiency for manifest
  contracts---contracts that check stronger properties than simple
  types, e.g., \"is a natural'' instead of \"is an
  integer''---remains an open problem. We show how to achieve sound
  space efficiency for manifest contracts with strong predicate
  contracts. The essential trick is breaking the contract checking
  down into coercions: structured, blame-annotated lists of
  checks. By carefully preventing duplicate coercions from appearing,
  we can restore space efficiency while keeping the same observable
  behavior."}
```

(NB that I've wrapped the text, and there are no newlines in the abstracts.)

* `abstracts.dat`

This file follows the format specified by
[LDA-C](http://www.cs.princeton.edu/~blei/lda-c/readme.txt):

```
[E]ach document is succinctly represented as a sparse vector of word
counts. The data is a file where each line is of the form:

     [M] [term_1]:[count] [term_2]:[count] ...  [term_N]:[count]

where [M] is the number of unique terms in the document, and the
[count] associated with each term is how many times that term appeared
in the document.  Note that [term_1] is an integer which indexes the
term; it is not a string.
```

That is, each line in `abstracts.dat` (or, more properly,
`PFX_abstracts.dat`) represents a document. Metadata on these
documents is stored in `docs.dat` on a line-by-line basis: line n in
`docs.dat` described line n in `abstracts.dat`.

The `[term_1]` is a _word id_, and the numbering of words begins at 0.

* `docs.dat`

Each line in this file gives the title, authors, conference, and year
for a paper. For example, the first line of `2015-01-03_13:26_docs.dat` is:

```
A reflection on call-by-value - Simon Peyton Jones Will Partain André Santos (ICFP 1996)
```

* `vocab.dat`

This file is a mapping from a word id (called a 'term' in LDA-C) to an
actual word. Since word id's are _numbered from 0_, the first line in
this file specifies the meaning of word id 0. For example, the first
line in `2015-01-03_13:26_vocab.dat` is:

```
reflection
```

Unsurprisingly, 'reflection' is also the first non-stopword in the
title of the first paper. More surprisingly, the paper mentioned above
wasn't written by Simon et al.---this documentation was written when
the web scraper was acting buggy. Here we are.
