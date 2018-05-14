import logging

from argparse import ArgumentParser

from parser import Parser
from reader import Reader
from topic_model import TopicModel


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    argParser = ArgumentParser(description='Used to run LDA or NMF topic models over a corpus.',
                               epilog='Happy topic modeling!')
    argParser.add_argument('corpus', type=str,
                           help='The path to the directory containing the corpus.')
    argParser.add_argument('--parsed', default=False, action='store_true',
                           help='Include flag if corpus directory is pre-parsed.')
    argParser.add_argument('--model', '-m', dest='model',
                           choices={'lda', 'nmf'}, default='nmf', type=str,
                           help='The type of model to train (lda or nmf). Defaults to nmf.')
    argParser.add_argument('--num_topics', '-n', dest='num_topics',
                           default=20, type=int,
                           help='The number of topics you want the model to find.')
    argParser.add_argument('--num_features', '-f', dest='num_features',
                           default=1000, type=int,
                           help='The number of features (unique word tokens) you want the model to use.')
    argParser.add_argument('--vectorizer', '-v', dest='vectorizer',
                           choices={'count', 'tfidf'}, default='count', type=str,
                           help='''The type of word vectorizer to use (count or tfidf). \
                                   As of now, LDA only supports using the count vectorizer.''')
    argParser.add_argument('--max_iter', '-i', dest='max_iter',
                           default=None, type=int,
                           help='The maximum number of training iterations to run.')
    argParser.add_argument('--name', '-u', dest='name',
                           default=None, type=str,
                           help='Optional name to keep track of your model with.')
    args = argParser.parse_args()

    pathToCorpus = args.corpus
    parsed = args.parsed
    modelType = args.model
    vectorizerType = args.vectorizer
    noTopics = args.num_topics
    noFeatures = args.num_features
    maxIter = args.max_iter
    name = args.name

    # Corpus was pre-parsed.
    if parsed:
        reader = Reader(directory=pathToCorpus)
    else:
        parser = Parser(directory=pathToCorpus)
        reader = Reader(parser=parser)

    # Instantiate TopicModel object with desired parameters.
    model = TopicModel(reader,
                       modelType=modelType,
                       vectorizerType=vectorizerType,
                       noTopics=noTopics,
                       noFeatures=noFeatures,
                       maxIter=maxIter,
                       name=name)


    # Train the model; training time is saved in model.trainingTime attribute.
    model.train()
    model.save()

    