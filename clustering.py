from text.doc2vec import doc2vec_from_news
from text.bag_of_words import bow_from_news
from text.nel import nel_from_news
from sklearn.metrics.pairwise import cosine_distances
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import homogeneity_completeness_v_measure
from sklearn.decomposition import PCA
import numpy as np


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


def clustering_bow(corpus, labels, filename=None):
    doc_vectors = bow_from_news(corpus,
                                filename=filename)

    pca = PCA(n_components=5000, copy=False)
    doc_vectors = pca.fit_transform(doc_vectors)

    vectors_dist = cosine_distances(doc_vectors)
    cluster = get_clustering_algorithm(k=len(labels))
    pred_labels = cluster.fit_predict(vectors_dist)
    evaluate_clusters(labels, pred_labels, technique='Bag of Words')
    return pred_labels


def clustering_doc2vec(corpus, labels, filename=None):
    doc_vectors = doc2vec_from_news(corpus,
                                    filename=filename)
    vectors_dist = cosine_distances(doc_vectors)

    cluster = get_clustering_algorithm(k=len(labels))
    pred_labels = cluster.fit_predict(vectors_dist)
    evaluate_clusters(labels, pred_labels, technique='Doc2Vec')
    return pred_labels


def clustering_nel(corpus, labels, filename=None):
    doc_vectors = nel_from_news(corpus,
                                filename=filename)
    vectors_dist = jaccard_distances(doc_vectors)

    cluster = get_clustering_algorithm(k=len(labels))
    pred_labels = cluster.fit_predict(vectors_dist)
    evaluate_clusters(labels, pred_labels, technique='Named Entity List')
    return pred_labels
