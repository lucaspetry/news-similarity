"""
Term Frequency-Inverse Document Frequency (TF-IDF)
"""
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import os


def load(filename):
    with open(filename, "rb") as fp:
        return pickle.load(fp)


def save(obj, filename):
    with open(filename, "wb") as fp:
        pickle.dump(obj, fp)


def tfidf_from_news(corpus, filename=None, norm=None):
    if filename and os.path.isfile(filename):
        return load(filename)
    else:
        vectorizer = TfidfVectorizer(norm=norm)
        grid_word_count = vectorizer.fit_transform(corpus).toarray()

        if filename:
            save(grid_word_count, filename)

        return grid_word_count
