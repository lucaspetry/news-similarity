"""
Bag of Words (BoW)
"""
from sklearn.feature_extraction.text import CountVectorizer
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
