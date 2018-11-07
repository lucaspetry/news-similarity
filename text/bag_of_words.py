"""
Bag of Words (BoW)
"""
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from MulticoreTSNE import MulticoreTSNE as TSNE
import numpy as np
import pickle
import os


def load(filename):
    with open(filename, "rb") as fp:
        return pickle.load(fp)


def save(obj, filename):
    with open(filename, "wb") as fp:
        pickle.dump(obj, fp)


def bow_from_news(corpus, filename=None, normalize_words=True):
    if filename and os.path.isfile(filename):
        return load(filename)
    else:
        vectorizer = CountVectorizer()
        grid_word_count = vectorizer.fit_transform(corpus).toarray()
        # If not weighted words, simply return the counts from vectorizer
        if not normalize_words:
            if filename:
                save(grid_word_count, filename)
            return grid_word_count

        for idx, sentence in enumerate(grid_word_count):
            grid_word_count[idx] = sentence / np.sum(sentence)

        if filename:
            save(grid_word_count, filename)
        return grid_word_count


def baseline(corpus, labels, filename=None, k_best=5000,
             normalize_words=False):
    if filename and os.path.isfile(filename):
        return load(filename)
    else:
        doc_bow = bow_from_news(corpus,
                                filename=None,
                                normalize_words=normalize_words)
        sel_doc_bow = SelectKBest(chi2, k=k_best).fit_transform(doc_bow,
                                                                labels)

        tsne = TSNE(n_components=2, n_jobs=4, random_state=1)
        doc_bow_2d = tsne.fit_transform(sel_doc_bow)

        if filename:
            save(doc_bow_2d, filename)

        return doc_bow_2d
