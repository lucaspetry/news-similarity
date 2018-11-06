"""
Bag of Words (BoW)
"""
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np


def bow_from_news(corpus, normalize_words=True):
    vectorizer = CountVectorizer()
    grid_word_count = vectorizer.fit_transform(corpus).toarray()
    # If not weighted words, simply return the counts from vectorizer
    if not normalize_words:
        return grid_word_count

    for idx, sentence in enumerate(grid_word_count):
        grid_word_count[idx] = sentence / np.sum(sentence)

    return grid_word_count
