"""
This is the main driver script for riptide.

Usage:
    Run this script from the command line to train Tmpl topic models
    over a given corpus.

    All outputs for topic model runs are saved in the 'models' directory
    in subdirectories corresponding to their respective runs.

Example:

    When running the script, there are various command line arguments that
    you can pass in. The only command line argument that is required is a
    path to the corpus. As with the reader, you can either pass in a pre-parsed
    corpus (and if so, must also include the '--parsed' command line flag), or
    the raw proceedings directory.

    Train and save a topic model with the default parameters:

        smacpher$ python main.py /Users/smacpher/clones/tmpl_venv/acm-data/proceedings

    Train and save a topic model passing in various parameters:

        smacpher$ python main.py /Users/smacpher/clones/tmpl_venv/acm-data/proceedings \
            --model nmf --num_topics 20 --vectorizer tfidf --max_iter 50


For more information on what each command line argument does,
see the help blurbs for each argument below.
"""
import logging

from argparse import ArgumentParser

from parser import Parser
from reader import Reader
from topic_model import TopicModel


if __name__ == '__main__':
    argParser = ArgumentParser(
        description='Used to run LDA or NMF topic models over a corpus.',
        epilog='Happy topic modeling!'
    )
    argParser.add_argument(
        'corpus', type=str,
        help='The path to the directory containing the corpus.'
    )
    argParser.add_argument(
        '--parsed', default=False, action='store_true',
        help='Include flag if corpus directory is pre-parsed.'
    )

    argParser.add_argument(
        '--model', '-m', dest='model',
        choices={'lda', 'nmf'}, default='nmf', type=str,
        help='The type of model to train (lda or nmf). Defaults to nmf.'
    )
    argParser.add_argument(
        '--num_topics', '-n', dest='num_topics',
        default=20, type=int,
        help='The number of topics you want the model to find.'
    )
    argParser.add_argument(
        '--num_features', '-f', dest='num_features',
        default=1000, type=int,
        help=('The number of features (unique word tokens) '
              'you want the model to use.')
    )
    argParser.add_argument(
        '--vectorizer', '-v', dest='vectorizer',
        choices={'count', 'tfidf'}, default='count', type=str,
        help='''The type of word vectorizer to use (count or tfidf). \
        As of now, LDA only supports using the count vectorizer.'''
    )
    argParser.add_argument(
        '--max_iter', '-i', dest='max_iter',
        default=None, type=int,
        help='The maximum number of training iterations to run.'
    )
    argParser.add_argument(
        '--name', '-u', dest='name',
        default=None, type=str,
        help='Optional name to keep track of your model with.'
    )
    argParser.add_argument(
        '--verbose', default=False, action='store_true',
        help='Whether to print verbose logging or not.'
    )
    args = argParser.parse_args()

    pathToCorpus = args.corpus
    parsed = args.parsed
    modelType = args.model
    vectorizerType = args.vectorizer
    noTopics = args.num_topics
    noFeatures = args.num_features
    maxIter = args.max_iter
    name = args.name
    verbose = args.verbose

    # Initialize a logger (will be inherited by every module in pipeline).
    if verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logger = logging.getLogger('Riptide')
    logger.setLevel(level=level)

    if parsed:
        reader = Reader(directory=pathToCorpus, parentLogger=logger)
    else:
        parser = Parser(directory=pathToCorpus, parentLogger=logger)
        reader = Reader(parser=parser, parentLogger=logger)

    # Instantiate TopicModel object with desired parameters.
    model = TopicModel(reader,
                       modelType=modelType,
                       vectorizerType=vectorizerType,
                       noTopics=noTopics,
                       noFeatures=noFeatures,
                       maxIter=maxIter,
                       name=name,
                       parentLogger=logger)
    model.train()
    model.save()
