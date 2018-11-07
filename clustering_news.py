from news_loader import load_news
from text.cleanup import cleanup_text
from text.bag_of_words import baseline
from plot_news import plot_data
from clustering import clustering_bow
from clustering import clustering_doc2vec
from clustering import clustering_nel
from clustering import clustering_nel_cosine
from joblib import Parallel, delayed
import multiprocessing
import numpy as np


n_jobs = multiprocessing.cpu_count()


def load_cleaned_news(remove_stopwords=True, stem=False):
    news = load_news(fields=['id', 'title', 'subtitle', 'subject', 'text'])

    results = Parallel(n_jobs=n_jobs)(delayed(cleanup_text)(article['text'],
                                                            article['title'],
                                                            article['subtitle'],
                                                            remove_stopwords,
                                                            stem) for article in news)

    for idx, article in enumerate(news):
        article['new_text'] = results[idx]
    return news


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
baseline_2d = baseline(corpus=corpus,
                       labels=labels,
                       filename='data/vectors_baseline_bow.bin',
                       k_best=5000,
                       normalize_words=False)
print("Computing baseline (Bag of Words)... DONE!")

# print("Computing clustering Bag of Words...")
# clus_bow = clustering_bow(corpus=corpus,
#                           labels=labels,
#                           filename='data/vectors_bow.bin')
# print("Computing clustering Bag of Words... DONE!")

print("Computing clustering Doc2Vec...")
clus_doc2vec = clustering_doc2vec(corpus=corpus_no_stem,
                                  labels=labels,
                                  filename='data/vectors_doc2vec.bin')
print("Computing clustering Doc2Vec... DONE!")

print("Computing clustering Named Entity List...")
clus_nel = clustering_nel(corpus=corpus_nel,
                          labels=labels,
                          filename='data/vectors_nel.bin')
print("Computing clustering Named Entity List... DONE!")

print("Computing clustering Bag of Named Entities...")
clus_nel_cosine = clustering_nel_cosine(corpus=corpus_nel,
                                        labels=labels,
                                        filename='data/vectors_nel.bin')
print("Computing clustering Bag of Named Entities... DONE!")

idx_filter = np.where(labels != 'Unclassified')

plot_data(vectors=baseline_2d[idx_filter], labels=labels[idx_filter],
          title='TSNE of News Dataset (Baseline Bag of Words)',
          file='data/tsne_baseline.pdf')

# plot_data(vectors=baseline_2d[idx_filter], labels=clus_bow[idx_filter],
#           title='TSNE of News Dataset (Agglomerative Clustering from Bag of Words)',
#           file='data/tsne_bow.pdf')

plot_data(vectors=baseline_2d[idx_filter], labels=clus_doc2vec[idx_filter],
          title='TSNE of News Dataset (Agglomerative Clustering from Doc2Vec)',
          file='data/tsne_doc2vec.pdf')

plot_data(vectors=baseline_2d[idx_filter], labels=clus_nel[idx_filter],
          title='TSNE of News Dataset (Agglomerative Clustering from Named Entity List)',
          file='data/tsne_nel.pdf')

plot_data(vectors=baseline_2d[idx_filter], labels=clus_nel_cosine[idx_filter],
          title='TSNE of News Dataset (Agglomerative Clustering from Bag of Named Entities)',
          file='data/tsne_nel_cosine.pdf')
