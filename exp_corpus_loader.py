from news_loader import load_news
from text.cleanup import cleanup_text
from joblib import Parallel, delayed
import multiprocessing
import numpy as np


n_jobs = multiprocessing.cpu_count()


def load_cleaned_news(remove_stopwords=True, stem=False):
    news = load_news(fields=['id', 'title', 'subtitle', 'subject', 'portal',
                             'text'])

    results = Parallel(n_jobs=n_jobs)(
        delayed(cleanup_text)(article['text'],
                              article['title'],
                              article['subtitle'],
                              remove_stopwords,
                              stem) for article in news)

    for idx, article in enumerate(news):
        article['new_text'] = results[idx]
    return news


def get_corpus_bow():
    news = load_cleaned_news(remove_stopwords=True, stem=True)
    labels = np.asarray([article['subject'] for article in news])
    corpus = [article['new_text'] for article in news]
    return corpus, labels


def get_corpus_tfidf():
    return get_corpus_bow()


def get_corpus_doc2vec():
    news = load_cleaned_news(remove_stopwords=True, stem=False)
    labels = np.asarray([article['subject'] for article in news])
    corpus = [article['new_text'] for article in news]
    return corpus, labels


def get_corpus_nel():
    news = load_cleaned_news(remove_stopwords=False, stem=False)
    labels = np.asarray([article['subject'] for article in news])
    corpus = [article['text'] for article in news]
    return corpus, labels
