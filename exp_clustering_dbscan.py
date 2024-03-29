import os
import gc
import pickle
import numpy as np
import pandas as pd
from joblib import Parallel, delayed
import multiprocessing
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_distances
from sklearn.metrics import homogeneity_completeness_v_measure

from exp_corpus_loader import get_corpus_bow
from exp_corpus_loader import get_corpus_tfidf
from exp_corpus_loader import get_corpus_doc2vec
from exp_corpus_loader import get_corpus_nel

from text.bag_of_words import bow_from_news
from text.tfidf import tfidf_from_news
from text.doc2vec import doc2vec_from_news
from text.nel import nel_from_news


n_jobs = multiprocessing.cpu_count()
results_file = 'exp_clustering_dbscan_results.csv'


def jaccard_distances(nel_list):
    def jaccard(list1, list2):
        intersection = len(list(set(list1).intersection(list2)))
        union = (len(list1) + len(list2)) - intersection
        return float(intersection / union)

    def one_to_many(idx1, list1):
        res = []
        for idx2 in range(0, idx1):
            res.append(1 - jaccard(list1, nel_list[idx2]))
        res = np.concatenate([np.array(res), np.zeros(len(nel_list) - idx1)])
        return res

    dist_mx = Parallel(n_jobs=n_jobs)(
        delayed(one_to_many)(idx1, list1) for idx1, list1 in enumerate(nel_list))

    dist_mx = np.array(dist_mx)
    return dist_mx + np.transpose(dist_mx)


def chunk_cosine_distances(vectors):
    chunk = 500
    mx_len = vectors.shape[0]
    dist_mx = np.zeros(shape=(mx_len, mx_len))

    for idx1 in range(0, mx_len, chunk):
        gc.collect()
        end1 = idx1 + chunk

        if end1 > mx_len:
            end1 = mx_len

        res_row = None

        for idx2 in range(0, mx_len, chunk):
            end2 = idx2 + chunk

            if end2 > mx_len:
                end2 = mx_len

            if isinstance(res_row, np.ndarray):
                dist = cosine_distances(
                    vectors[idx1:end1], vectors[idx2:end2])
                res_row = np.hstack((res_row, dist))
            else:
                res_row = cosine_distances(
                    vectors[idx1:end1], vectors[idx2:end2])

        dist_mx[idx1:end1] = res_row
    return dist_mx


def load(filename):
    with open(filename, "rb") as fp:
        return pickle.load(fp)


def save(obj, filename):
    with open(filename, "wb") as fp:
        pickle.dump(obj, fp, protocol=4)


test_eps = np.arange(0.05, 0.91, 0.05)
test_min_samples = [5, 10, 15, 20, 25]

techniques = [{'name': 'Doc2Vec',
               'vectors': doc2vec_from_news,
               'corpus': get_corpus_doc2vec,
               'dist': cosine_distances,
               'filename': 'data/vectors_doc2vec.bin',
               'dist_file': 'data/dist_doc2vec.bin'},
              {'name': 'NEL',
               'vectors': nel_from_news,
               'corpus': get_corpus_nel,
               'dist': jaccard_distances,
               'filename': 'data/vectors_nel.bin',
               'dist_file': 'data/dist_nel.bin'},
              {'name': 'TF-IDF',
               'vectors': tfidf_from_news,
               'corpus': get_corpus_tfidf,
               'dist': chunk_cosine_distances,
               'filename': None,
               'dist_file': 'data/dist_tfidf.bin'},
              {'name': 'BOW',
               'vectors': bow_from_news,
               'corpus': get_corpus_bow,
               'dist': chunk_cosine_distances,
               'filename': None,
               'dist_file': 'data/dist_bow.bin'}]

results = pd.DataFrame(data={'technique': [],
                             'clus': [],
                             'clus_params': [],
                             'num_clusters': [],
                             'homogeneity': [],
                             'completeness': [],
                             'v_measure': [],
                             'outliers': []})

for technique in techniques:
    gc.collect()
    corpus, labels = technique['corpus']()
    dist_fun = technique['dist']
    file = technique['filename']
    dist_file = technique['dist_file']
    vector_fun = technique['vectors']

    print("Computing clustering for technique", technique['name'], '...')

    if file and os.path.isfile(file):
        doc_vectors = load(file)
    else:
        doc_vectors = vector_fun(corpus,
                                 filename=file)

    print("Computing/loading distances for technique", technique['name'], '...')

    if dist_file and os.path.isfile(dist_file):
        vectors_dist = load(dist_file)
    else:
        vectors_dist = dist_fun(doc_vectors)
        save(vectors_dist, dist_file)

    print("Computing/loading distances for technique", technique['name'], '... DONE!')

    articles_filter = np.where(labels != "Unclassified")
    keep_idxs = np.r_[0:len(labels)][articles_filter]
    # new_vectors = []

    # for idx, vec in enumerate(doc_vectors):
    #     if idx in keep_idxs:
    #         new_vectors.append(vec)

    # doc_vectors = new_vectors
    new_dist = []

    for idx, row in enumerate(vectors_dist):
        if idx in keep_idxs:
            new_dist.append(row[articles_filter])

    vectors_dist = np.array(new_dist)
    labels = labels[articles_filter]

    for eps in test_eps:
        for min_samples in test_min_samples:
                dbscan = DBSCAN(eps=eps,
                                min_samples=min_samples,
                                metric='precomputed',
                                n_jobs=2)
                pred_labels = dbscan.fit_predict(vectors_dist)
                outliers = np.count_nonzero(np.where(pred_labels == -1))
                num_clusters = len(set(pred_labels))
                (homog,
                 compl,
                 v_measure) = homogeneity_completeness_v_measure(labels,
                                                                 pred_labels)
                results = results.append({'technique': technique['name'],
                                          'clus': 'DBSCAN',
                                          'clus_params': 'eps=' + str(eps) + ';min_samples=' + str(min_samples),
                                          'num_clusters': num_clusters,
                                          'homogeneity': homog,
                                          'completeness': compl,
                                          'v_measure': v_measure,
                                          'outliers': outliers},
                                         ignore_index=True)
                print(technique['name'], 'DBSCAN', 'eps=' + str(eps) + ';min_samples=' + str(min_samples), num_clusters, homog, compl, v_measure, 'outliers=', outliers)
                results.to_csv(results_file, index=False)

    vectors_dist = None
    doc_vectors = None
    corpus = None
