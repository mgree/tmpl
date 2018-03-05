import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.datasets import fetch_20newsgroups
from sklearn.decomposition import NMF, LatentDirichletAllocation

from reader import JsonFileReader


# def display_topics(model, feature_names, no_top_words):
#     for topic_idx, topic in enumerate(model.components_):
#         print "Topic %d:" % (topic_idx)
#         print " ".join([feature_names[i]
#                         for i in topic.argsort()[:-no_top_words - 1:-1]])

def display_topics(H, W, feature_names, corpus, no_top_words, no_top_documents):
    (documents, metas) = corpus
    for topic_idx, topic in enumerate(H):
        print "---------------- Topic %d: ----------------" % (topic_idx)
        print ("\n")
        print "Top words..."
        print " ".join([feature_names[i]
                        for i in topic.argsort()[:-no_top_words - 1:-1]])
        print "\n"
        print "Top papers..."
        print "\n"
        top_doc_indices = np.argsort( W[:,topic_idx] )[::-1][0:no_top_documents]
        for doc_index in top_doc_indices:
            print metas[doc_index]['title']
        print "\n"

def loadCorpus():
    pathToAbs = '/Users/smacpher/clones/tmpl_venv/tmpl-data/abs/top4/'
    reader = JsonFileReader()
    (documents, meta) = reader.loadAllAbstracts(pathToAbs, recursive=True)
    return (documents, meta)

# dataset = fetch_20newsgroups(shuffle=True, random_state=1, remove=('headers', 'footers', 'quotes'))
# documents = dataset.data

(documents, metas) = loadCorpus()

print "Corpus size..."
print len(documents)

no_features = 1000

# NMF is able to use tf-idf
tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, max_features=no_features, stop_words='english')
tfidf = tfidf_vectorizer.fit_transform(documents)
tfidf_feature_names = tfidf_vectorizer.get_feature_names()

# LDA can only use raw term counts for LDA because it is a probabilistic graphical model
tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=no_features, stop_words='english')
tf = tf_vectorizer.fit_transform(documents)
tf_feature_names = tf_vectorizer.get_feature_names()

no_topics = 20

# Run NMF
nmf_model = NMF(n_components=no_topics, 
          random_state=1, 
          alpha=.1, 
          l1_ratio=.5, 
          init='nndsvd',
          verbose=5,
          ).fit(tfidf)
nmf_W = nmf_model.transform(tfidf)
nmf_H = nmf_model.components_

# Run LDA
lda_model = LatentDirichletAllocation(n_topics=no_topics, 
                                max_iter=5, learning_method='online', 
                                learning_offset=50.,
                                random_state=0,
                                verbose=5,
                                ).fit(tf)
lda_W = lda_model.transform(tf)
lda_H = lda_model.components_

no_top_words = 10
no_top_documents = 10

print "*** Displaying topics for nmf *** "
display_topics(nmf_H, nmf_W, tfidf_feature_names, (documents, metas), no_top_words, no_top_documents)

print "*** Displaying topics for lda ***"
display_topics(lda_H, lda_W, tf_feature_names, (documents, metas), no_top_words, no_top_documents)

# no_top_words = 10
# print "Displaying topics for nmf..."
# display_topics(nmf, tfidf_feature_names, no_top_words)

# print "Displaying topics for lda..."
# display_topics(lda, tf_feature_names, no_top_words)
