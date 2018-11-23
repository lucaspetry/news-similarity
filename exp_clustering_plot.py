from text.bag_of_words import bow_from_news
from exp_corpus_loader import get_corpus_bow
from exp_corpus_loader import get_corpus_tfidf
from exp_plot_news import plot_data

import os
import numpy as np
import pickle

from sklearn.cluster import AgglomerativeClustering
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from MulticoreTSNE import MulticoreTSNE as TSNE


def load(filename):
    with open(filename, "rb") as fp:
        return pickle.load(fp)


def save(obj, filename):
    with open(filename, "wb") as fp:
        pickle.dump(obj, fp, protocol=4)


corpus, labels = get_corpus_bow()
ground_truth_file = 'data/vectors_ground_truth.bin'

print("Computing ground truth...")
if os.path.isfile(ground_truth_file):
    doc_bow_2d = load(ground_truth_file)
else:
    doc_bow = bow_from_news(corpus,
                            filename=None,
                            normalize_words=False)
    sel_doc_bow = SelectKBest(chi2, k=5000).fit_transform(doc_bow, labels)

    tsne = TSNE(n_components=2, n_jobs=4, random_state=1)
    doc_bow_2d = tsne.fit_transform(sel_doc_bow)
    save(doc_bow_2d, ground_truth_file)


idx_filter = np.where(labels != 'Unclassified')

plot_data(vectors=doc_bow_2d[idx_filter], labels=labels[idx_filter],
          title='',
          file='data/tsne_clustering_ground_truth.pdf')

print("Computing ground truth... DONE!")

print("Computing agglomerative clustering TF-IDF...")

agglomerative = AgglomerativeClustering(n_clusters=35,
                                        affinity='precomputed',
                                        linkage='average')


corpus, labels = get_corpus_tfidf()
dist_file = 'data/dist_tfidf.bin'
vectors_dist = load(dist_file)

pred_labels = agglomerative.fit_predict(vectors_dist)

plot_data(vectors=doc_bow_2d[idx_filter], labels=pred_labels[idx_filter],
          title='',
          file='data/tsne_clustering_tfidf.pdf')

print("Computing agglomerative clustering TF-IDF... DONE!")
