import os
import gc
import pickle
import numpy as np
import pandas as pd
from joblib import Parallel, delayed
import multiprocessing
from sklearn.metrics.pairwise import cosine_distances

from exp_corpus_loader import load_cleaned_news
from exp_corpus_loader import get_corpus_bow
from exp_corpus_loader import get_corpus_tfidf
from exp_corpus_loader import get_corpus_doc2vec
from exp_corpus_loader import get_corpus_nel

from text.bag_of_words import bow_from_news
from text.tfidf import tfidf_from_news
from text.doc2vec import doc2vec_from_news
from text.nel import nel_from_news


n_jobs = multiprocessing.cpu_count()
results_file = 'exp_spreading_portals_results.csv'


def get_spreading(idx2portal, news_portals, sim_matrix, threshold):
    dist_portals = list(idx2portal.values())
    spread_count = np.zeros((len(dist_portals), len(dist_portals)))

    for idx1, portal in enumerate(dist_portals):
        for idx2 in range(idx1 + 1, len(dist_portals)):
            filtered_mx = sim_matrix[:,np.where(news_portals == dist_portals[idx2])]
            filtered_mx = filtered_mx[np.where(news_portals == portal),:]
            filtered_mx = np.squeeze(filtered_mx)
            total = len(filtered_mx) + len(filtered_mx[0])
            cond = np.where(filtered_mx >= threshold, 1, 0)
            sum1 = np.sum(np.any(cond, axis=0))
            sum2 = np.sum(np.any(cond, axis=1))
            spread_count[idx1][idx2] = (sum1 + sum2) / total

    spread_count += np.transpose(spread_count)
    return spread_count


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


test_threshold = [0.5, 0.6, 0.7, 0.8, 0.9]

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
                             'threshold': [],
                             'portal1': [],
                             'portal2': [],
                             'match_percentage': []})

news = load_cleaned_news()
portals = np.array([n['portal'] for n in news])
idx2portal = dict(zip(np.r_[0:len(set(portals))], set(portals)))

for technique in techniques:
    gc.collect()
    corpus, labels = technique['corpus']()
    dist_fun = technique['dist']
    file = technique['filename']
    dist_file = technique['dist_file']
    vector_fun = technique['vectors']

    print("Computing spreading for technique", technique['name'], '...')

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
    sim_matrix = 1 - vectors_dist
    distinct_portals = list(idx2portal.values())

    for threshold in test_threshold:
        spreading = get_spreading(idx2portal, portals, sim_matrix, threshold)

        for idx1, _ in enumerate(distinct_portals):
            for idx2 in range(idx1 + 1, len(distinct_portals)):
                res = {
                    'technique': technique['name'],
                    'threshold': threshold,
                    'portal1': idx2portal[idx1],
                    'portal2': idx2portal[idx2],
                    'match_percentage': spreading[idx1][idx2]
                }
                results = results.append(res, ignore_index=True)
        results.to_csv(results_file, index=False)
        print(technique['name'], 'threshold=' + str(threshold))

    vectors_dist = None
    doc_vectors = None
    corpus = None
