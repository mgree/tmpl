# Fathom

Fathom is a package that streamlines Tmpl topic modeling. It takes care of all of the heavy lifting involved with preprocessing Tmpl corpora,
storing important data throughout a topic model training run, and curating the output
of the models to be ready-to-use and easy to evaluate and perform analysis on right after training.

It uses a pair of Scikit-learn's pre-built models -- LatentDirichletAllocation and NMF --
to build and train topic models at its core.

Note that this is the second iteration of the Tmpl topic modeling suite.

## Getting Started

Let's walk through how to get started developing and training Tmpl topic models using Fathom.
There will be various asides and explanations sprinkled throughout this to help familiarize you
with working with the various features and aspects of Fathom (eg. there will be various notes on
Python packages).

### Installing

#### Cloning the repository

First, clone this repository! Run this command in your terminal:

    git clone https://github.com/mgree/tmpl.git

#### Setting up a virtual environment
Now we'll set up a virtual environment to install Fathom in and develop and train models in. A virtual environment
gives you a dedicated space where you can install any sort of dependencies you need without messing with
your global dependencies. Moreover, since Fathom is built in Python 2.7, the virtual environment will ensure
that we are using Python 2.7 and that all of the dependencies we install are in version compatible with Python 2.7.
You can read more about Python virtual environments here: https://virtualenv.pypa.io/en/stable/

First, make sure that you have `pip` installed. `pip` is the Python package manager that makes it easy
to install Python packages. Run the following:

    which pip

If you have `pip`, you will see the path of the executable where it lives. If not, you won't see anything and
you should follow the steps here to install `pip`: https://pip.pypa.io/en/stable/installing/

Now, install the Python package `virtualenv` used to create and manage virtual environments:

    pip install virtualenv

With that installed, created a new virtual environment (where you want in your filesystem):

    virtualenv tmpl_venv

Feel free to replace `tmpl_venv` with whatever name you want.

Navigate to your new virtual environment's directory (in the above case, `cd tmpl_venv`) and use the following
to activate your environment:

    source bin/activate

You can now install Python packages and develop in your new isolated virtual environment. That is, if you install
any Python packages in it while its activated, they will only be accessible while its activated.

To deactivate your virtual environment, use the `deactivate` command.

#### Installing Fathom in your virtual environment
Next, make sure you're in the `fathom/` directory:

    cd fathom

You should now see a file named `setup.py`. This is the setup script for the Python package. All
Python packages have one of these -- they help make sure all the necessary dependency packages are installed
and that the package is made available to be imported into other Python programs that you may create.

Run the following command to install the Fathom Python package:

    python setup.py install

If for some reason this fails, you can manually install the dependencies with the following command:

    pip install -r requirements.txt

If everything goes right (and I really hope it did), Fathom should be installed and ready to use!

### Running your first pipeline

The main entry point for using Fathom is `main.py` located at `fathom/fathom/main.py`:

To train a pipeline, you must specify the local directory path where the Tmpl corpora of interest is saved.
The following command will kick of a pipeline with the default parameters:

    python main.py /Users/smacpher/clones/tmpl_venv/tmpl-corpus/proceedings

This run will be have three main steps: 1) parse the raw XML proceeding files (one per conference and year),
2) read the parsed corpus into the topic model and store relevant data (papers, conferences, authors, etc.) into
a TmplDB instance along the way, and 3) train a topic model over the corpus which when finished, will produce an
output directory of the form `models/<model_unique_name>` where `<model_unique_name>` will look something like
`mf_tfidfv_20n_1000f_200i_2018-05-15T20:43:51.844410`.

There is one output directory per model and it contains three
output files: 1) `model.pkl`, the pickled TopicModel object (to save its exact state, attributes, and the trained
Scikit-learn model to make future inferences should we need to), 2) `db.sqlite3`, the Sqlite3 database produced by
the TmplDB module that stores the scores (topic vectors) of all of the papers in the corpus and relevant metadata
about the corpus (see `fathom/fathom/schemas/init.sql` for the full database schema), and 3) `summary.txt`, a
human-readable text file summarizing the results of the topic model (top 10 words and top 10 papers per topic).

## Built With

* [Scikit-learn](http://scikit-learn.org/) - For Fathom's core topic modeling functionality

## Authors

**Sean MacPherson** - RA Spring 2018 - sean.j.macpherson@gmail.com

**Professor Michael Greenberg** - Advisor

## Resources
Here's a list of resources that I found particularly helpful when learning
about topic modeling:

Python LDA Topic Modeling Script using gensim: https://rstudio-pubs-static.s3.amazonaws.com/79360_850b2a69980c4488b1db95987a24867a.html

Greenberg’s tmpl source code: https://github.com/mgree/tmpl/tree/master/lda

Python gensim (Python distributed Topic Modeling package built on numpy; fast and uses constant memory (via Python generators)) source code: https://github.com/RaRe-Technologies/gensim

LDA-C source code: https://github.com/blei-lab/lda-c

EM (Expectation Maximization; apparently LDA-C is an EM variation for LDA built on C) paper: https://www2.ee.washington.edu/techsite/papers/documents/UWEETR-2010-0002.pdf

Really clear and concise overview of stemming and lemmatization:
https://nlp.stanford.edu/IR-book/html/htmledition/stemming-and-lemmatization-1.html

Attempting to use supervised learning to avoid rule-based tokenization (using rules doesn’t scale well! For NLP applications, preprocessing is very important for solid ML results): http://gmb.let.rug.nl/elephant/about.php

Really good high-level overview of how LDA works (in the context of finding similar magazines in Issuu); also has some cool preprocessing techniques: https://www.youtube.com/watch?v=3mHy4OSyRf0

High-level overview of LSA (Latent Semantic Analysis) / PLSA (Probabilistic Latent Semantic Analysis) / LDA (Latent Dirichlet Allocation): https://cs.stanford.edu/~ppasupat/a9online/1140.html

Great high-level overview of LDA and analogies from Quora: https://www.quora.com/What-is-a-good-explanation-of-Latent-Dirichlet-Allocation

Jupyter Notebook using PyLDAvis (visualization tool for topic models; also uses gensim): http://nbviewer.jupyter.org/github/dsquareindia/gensim/blob/a4b2629c0fdb0a7932db24dfcf06699c928d112f/docs/notebooks/topic_coherence_tutorial.ipynb

Article: “How to choose the best topic model”: https://www.kdnuggets.com/2016/07/americas-next-topic-model.html

Good humanist explanation to LDA: https://www.google.com/amp/s/tedunderwood.com/2012/04/07/topic-modeling-made-just-simple-enough/amp/
Short description of LDA hyperparameters, alpha and beta: https://www.thoughtvector.io/blog/lda-alpha-and-beta-parameters-the-intuition/

About Gensim Multicore Blog Post: https://rare-technologies.com/multicore-lda-in-python-from-over-night-to-over-lunch/

Gensim Google Group (lots of good answers to questions!!): https://groups.google.com/forum/#!forum/gensim

Gensim FAQ and Recipes: https://github.com/RaRe-Technologies/gensim/wiki/Recipes-&-FAQ

Very helpful tips on using Gensim’s LDA Model from a community user: https://miningthedetails.com/blog/python/lda/GensimLDA/

David Blei Topic Modelling Lecture: http://videolectures.net/mlss09uk_blei_tm/

Google Word2Vec tool: https://code.google.com/archive/p/word2vec/

Good Medium articles on using Scikit-learn’s LDA and NMF topic modeling algorithms: https://medium.com/mlreview/topic-modeling-with-scikit-learn-e80d33668730 and https://towardsdatascience.com/improving-the-interpretation-of-topic-models-87fd2ee3847d

Scikit-learn docs for LDA and NMF and example: http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.LatentDirichletAllocation.html#sklearn.decomposition.LatentDirichletAllocation,
http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.NMF.html#sklearn.decomposition.NMF, http://scikit-learn.org/stable/auto_examples/applications/plot_topics_extraction_with_nmf_lda.html#sphx-glr-auto-examples-applications-plot-topics-extraction-with-nmf-lda-py

Really good tutorial on NMF and other pre-existing matrix factorization techniques (PCA and VQ): https://www.youtube.com/watch?v=UQGEB3Q5-fQ
