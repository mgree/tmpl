Topic modeling for the programming languages literature.

You can [run our tool](http://tmpl.weaselhat.com)!

# Structure

The `analysis` directory holds the R scripts we used to generate
figures for the
[paper](http://www.cs.pomona.edu/~michael/papers/snapl2015.pdf).

The `lda` directory holds the Python and bash scripts we used to run
David Blei's [LDA-C](https://github.com/Blei-Lab/lda-c). Outputs get
put in the `out` directory.

The `sessions` directory is the (not quite finished) analysis of
session data for POPL.

The `www` directory is the website frontend and backend.

# Using our tool

You'll need David Blei's [LDA-C](https://github.com/Blei-Lab/lda-c), compiled and with `lda` on your path. You'll also need the Python library [nltk](http://www.nltk.org/install.html), with the `stopwords` and `wordnet` modules installed.

To do the R analysis, you'll need R with `ggplot2` installed.
