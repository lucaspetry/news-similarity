from text.bag_of_words import bow_from_news
from exp_corpus_loader import load_cleaned_news
from exp_corpus_loader import get_corpus_bow

import os
import numpy as np
import pandas as pd
import pickle

from sklearn.cluster import DBSCAN
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from MulticoreTSNE import MulticoreTSNE as TSNE


def load(filename):
    with open(filename, "rb") as fp:
        return pickle.load(fp)


def save(obj, filename):
    with open(filename, "wb") as fp:
        pickle.dump(obj, fp, protocol=4)


news = load_cleaned_news()

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

ids = np.array([n['id'] for n in news])
titles = np.array([n['title'] for n in news])

print("Computing ground truth... DONE!")

print("Computing agglomerative clustering Doc2Vec...")

dbscan = DBSCAN(eps=0.35,
                min_samples=5,
                metric='precomputed',
                n_jobs=2)


dist_file = 'data/dist_doc2vec.bin'
vectors_dist = load(dist_file)

pred_labels = dbscan.fit_predict(vectors_dist)
pd.DataFrame({'id': ids[idx_filter],
              'title': titles[idx_filter],
              'cluster': pred_labels[idx_filter],
              'label': labels[idx_filter]}).to_csv('data/dbscan_doc2vec_groups.csv', index=False)

print("Computing agglomerative clustering Doc2Vec... DONE!")


print("Computing agglomerative clustering TF-IDF...")

dbscan = DBSCAN(eps=0.65,
                min_samples=5,
                metric='precomputed',
                n_jobs=2)


dist_file = 'data/dist_tfidf.bin'
vectors_dist = load(dist_file)

pred_labels = dbscan.fit_predict(vectors_dist)
pd.DataFrame({'id': ids[idx_filter],
              'title': titles[idx_filter],
              'cluster': pred_labels[idx_filter],
              'label': labels[idx_filter]}).to_csv('data/dbscan_tfidf_groups.csv', index=False)

print("Computing agglomerative clustering TF-IDF... DONE!")


print("Computing agglomerative clustering BOW...")


dbscan = DBSCAN(eps=0.6,
                min_samples=20,
                metric='precomputed',
                n_jobs=2)


dist_file = 'data/dist_bow.bin'
vectors_dist = load(dist_file)

pred_labels = dbscan.fit_predict(vectors_dist)
pd.DataFrame({'id': ids[idx_filter],
              'title': titles[idx_filter],
              'cluster': pred_labels[idx_filter],
              'label': labels[idx_filter]}).to_csv('data/dbscan_bow_groups.csv', index=False)

print("Computing agglomerative clustering BOW... DONE!")


print("Computing agglomerative clustering NEL...")

dbscan = DBSCAN(eps=0.75,
                min_samples=15,
                metric='precomputed',
                n_jobs=2)


dist_file = 'data/dist_nel.bin'
vectors_dist = load(dist_file)

pred_labels = dbscan.fit_predict(vectors_dist)
pd.DataFrame({'id': ids[idx_filter],
              'title': titles[idx_filter],
              'cluster': pred_labels[idx_filter],
              'label': labels[idx_filter]}).to_csv('data/dbscan_nel_groups.csv', index=False)

print("Computing agglomerative clustering NEL... DONE!")
