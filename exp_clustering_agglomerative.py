import os
import gc
import pickle
import numpy as np
import pandas as pd
from joblib import Parallel, delayed
import multiprocessing
from sklearn.cluster import AgglomerativeClustering
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
results_file = 'exp_clustering_agglomerative_results.csv'


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


test_link = ['complete', 'average']
test_k = np.concatenate([[8], np.arange(5, 301, 5)])

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
                             'v_measure': []})

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

    for link in test_link:
        for k in test_k:
                agglomerative = AgglomerativeClustering(n_clusters=k,
                                                        affinity='precomputed',
                                                        linkage=link)
                pred_labels = agglomerative.fit_predict(vectors_dist)
                (homog,
                 compl,
                 v_measure) = homogeneity_completeness_v_measure(labels,
                                                                 pred_labels)
                results = results.append({'technique': technique['name'],
                                          'clus': 'Agglomerative',
                                          'clus_params': 'link=' + link,
                                          'num_clusters': k,
                                          'homogeneity': homog,
                                          'completeness': compl,
                                          'v_measure': v_measure},
                                         ignore_index=True)
                print("Done:", technique['name'], 'Agglomerative', 'link=' + link, k, homog, compl, v_measure)
                results.to_csv(results_file, index=False)

    vectors_dist = None
    doc_vectors = None
    corpus = None
