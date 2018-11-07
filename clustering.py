from text.doc2vec import doc2vec_from_news
from text.bag_of_words import bow_from_news
from text.nel import nel_from_news
from sklearn.metrics.pairwise import cosine_distances
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import homogeneity_completeness_v_measure
from sklearn.decomposition import PCA
import numpy as np
import os
import random
import pickle


def get_clustering_algorithm(k):
    return AgglomerativeClustering(n_clusters=k,
                                   affinity='precomputed',
                                   linkage='complete')


def evaluate_clusters(true_labels, pred_labels, technique):
    homog, compl, v_measure = homogeneity_completeness_v_measure(
        true_labels, pred_labels)

    print('Clustering Evaluation of', technique)
    print('    Homogeneity: ', homog)
    print('    Completeness:', compl)
    print('    V-Measure:   ', v_measure)


def jaccard_distances(nel_list):
    def jaccard(list1, list2):
        intersection = len(list(set(list1).intersection(list2)))
        union = (len(list1) + len(list2)) - intersection
        return float(intersection / union)

    dist_mx = np.zeros(shape=(len(nel_list), len(nel_list)))

    for idx, list1 in enumerate(nel_list):
        for idx2, list2 in enumerate(nel_list):
            dist_mx[idx][idx2] = 1 - jaccard(list1, list2)

    return dist_mx


def load(filename):
    with open(filename, "rb") as fp:
        return pickle.load(fp)


def save(obj, filename):
    with open(filename, "wb") as fp:
        pickle.dump(obj, fp)


def clustering_bow(corpus, labels, filename=None):
    doc_vectors = None

    if filename and os.path.isfile(filename):
        doc_vectors = load(filename)
    else:
        doc_vectors = bow_from_news(corpus,
                                    filename=None)

    vectors_dist = cosine_distances(doc_vectors)
    cluster = get_clustering_algorithm(20)
    pred_labels = cluster.fit_predict(vectors_dist)
    evaluate_clusters(labels, pred_labels, technique='Bag of Words')
    return pred_labels


def clustering_doc2vec(corpus, labels, filename=None):
    doc_vectors = doc2vec_from_news(corpus,
                                    filename=filename)
    vectors_dist = cosine_distances(doc_vectors)

    cluster = get_clustering_algorithm(k=len(set(labels)))
    pred_labels = cluster.fit_predict(vectors_dist)
    evaluate_clusters(labels, pred_labels, technique='Doc2Vec')
    return pred_labels


def clustering_nel(corpus, labels, filename=None):
    doc_vectors = nel_from_news(corpus,
                                filename=filename)
    vectors_dist = jaccard_distances(doc_vectors)

    cluster = get_clustering_algorithm(k=len(set(labels)))
    pred_labels = cluster.fit_predict(vectors_dist)
    evaluate_clusters(labels, pred_labels, technique='Named Entity List')
    return pred_labels
