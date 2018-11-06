from text.doc2vec import doc2vec_from_news
from text.bag_of_words import bow_from_news
from text.nel import nel_from_news
from news_loader import load_news
import nltk
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer
import string
from sklearn.metrics.pairwise import cosine_distances
import numpy as np
from joblib import Parallel, delayed
import multiprocessing
from plot_news import plot_data
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import homogeneity_completeness_v_measure
from sklearn.metrics import silhouette_score
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from MulticoreTSNE import MulticoreTSNE as TSNE
from sklearn.decomposition import PCA

nltk.download('rslp')
stemmer = RSLPStemmer()
stops = set(stopwords.words("portuguese"))
num_cores = multiprocessing.cpu_count()


def cleanup_text(title, subtitle, body, remove_stopwords=True, stem=False):
    text = merge_text(title, subtitle, body).lower().split()

    if remove_stopwords:
        text = [w for w in text if not w in stops]

    if stem:
        text = [stemmer.stem(w) for w in text]

    text = " ".join(text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text


def merge_text(title, subtitle, text):
    return title + ' ' + subtitle + ' ' + text


def load_cleaned_news(remove_stopwords=True, stem=False):
    nltk.download('stopwords')
    news = load_news(fields=['id', 'title', 'subtitle', 'subject', 'text'])

    results = Parallel(n_jobs=num_cores)(delayed(cleanup_text)(article['title'],
                                                               article['subtitle'],
                                                               article['text'],
                                                               remove_stopwords,
                                                               stem) for article in news)

    for idx, article in enumerate(news):
        article['new_text'] = results[idx]
    return news


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


def evaluate_clusters(true_labels, pred_labels, technique):
    homog, compl, v_measure = homogeneity_completeness_v_measure(
        true_labels, pred_labels)

    print('Clustering Evaluation of', technique)
    print('    Homogeneity: ', homog)
    print('    Completeness:', compl)
    print('    V-Measure:   ', v_measure)


print("Loading news...")
news = load_cleaned_news(remove_stopwords=True, stem=True)
news_nel = load_cleaned_news(remove_stopwords=False, stem=False)
news_no_stem = load_cleaned_news(remove_stopwords=True, stem=False)
corpus = [article['new_text'] for article in news]
corpus_nel = [article['text'] for article in news_nel]
corpus_no_stem = [article['new_text'] for article in news_no_stem]

labels = np.asarray([article['subject'] for article in news])
print("Loading news... DONE!")

print("Computing baseline (Bag of Words)...")
doc_bow = bow_from_news(corpus,
                        filename=None,  # 'vectors_baseline_bow.bin',
                        normalize_words=False)
sel_doc_bow = SelectKBest(chi2, k=5000).fit_transform(doc_bow, labels)
idx_filter = np.where(labels != 'Unclassified')

tsne = TSNE(n_components=2, n_jobs=4, random_state=1)
doc_bow_2d = tsne.fit_transform(sel_doc_bow)

plot_data(vectors=doc_bow_2d[idx_filter], labels=labels[idx_filter],
          title='TSNE of News Dataset (Baseline Bag of Words)',
          file='tsne_baseline.pdf')
print("Computing baseline (Bag of Words)... DONE!")

pca = PCA(n_components=5000)
doc_bow = pca.fit_transform(doc_bow)

bow_dist = cosine_distances(doc_bow)
cluster = AgglomerativeClustering(n_clusters=len(set(labels)),
                                  affinity='precomputed',
                                  linkage='complete')
pred_labels_bow = cluster.fit_predict(bow_dist)

evaluate_clusters(labels, pred_labels_bow, technique='Bag of Words')
plot_data(vectors=doc_bow_2d[idx_filter], labels=pred_labels_bow[idx_filter],
          title='TSNE of News Dataset (Agglomerative Clustering from Bag of Words)',
          file='data/tsne_bow.pdf')

doc_embeddings = doc2vec_from_news(corpus_no_stem,
                                   filename='data/vectors_doc2vec.d2v')
embeddings_dist = cosine_distances(doc_embeddings)

cluster = AgglomerativeClustering(n_clusters=len(set(labels)),
                                  affinity='precomputed',
                                  linkage='complete')
pred_labels_doc2vec = cluster.fit_predict(embeddings_dist)

evaluate_clusters(labels, pred_labels_doc2vec, technique='Doc2Vec')
plot_data(vectors=doc_bow_2d[idx_filter], labels=pred_labels_doc2vec[idx_filter],
          title='TSNE of News Dataset (Agglomerative Clustering from Doc2Vec)',
          file='data/tsne_doc2vec.pdf')

print("Computing NEL clustering...")
doc_nel = nel_from_news(corpus_nel, filename='data/vectors_nel.bin')
nel_dist = jaccard_distances(doc_nel)

cluster = AgglomerativeClustering(n_clusters=50,  # len(set(labels)),
                                  affinity='precomputed',
                                  linkage='complete')
pred_labels_nel = cluster.fit_predict(nel_dist)

evaluate_clusters(labels, pred_labels_nel, technique='Named Entity Lists (NEL)')
plot_data(vectors=doc_bow_2d[idx_filter], labels=pred_labels_nel[idx_filter],
          title='TSNE of News Dataset (Agglomerative Clustering from NEL)',
          file='data/tsne_nel.pdf')
print("Computing NEL clustering... DONE!")
