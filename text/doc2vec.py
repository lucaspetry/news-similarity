"""
Paragraph Vector (Doc2Vec)
"""
import os
from gensim.models import Doc2Vec
from gensim.models.doc2vec import LabeledSentence
from gensim import utils


def doc2vec_from_news(corpus, filename=None):
    sentences = []

    for idx, article in enumerate(corpus):
        sentences.append(
            LabeledSentence(utils.to_unicode(article).split(),
                            [idx]))

    ##################################
    # Learn or load doc embeddings
    ##################################
    embedding_size = 200
    text_model = None

    if filename and os.path.isfile(filename):
        text_model = Doc2Vec.load(filename)
    else:
        print("Training Doc2Vec network...")
        text_model = Doc2Vec(min_count=1,  # Ignores words with lower counts than this
                             window=5,  # The size of the context window
                             vector_size=embedding_size,
                             #sample=1e-4,
                             #negative=0,
                             workers=4,
                             epochs=100,
                             seed=1)
        text_model.build_vocab(sentences)
        text_model.train(sentences,
                         total_examples=text_model.corpus_count,
                         epochs=text_model.iter)

        if filename:
            text_model.save(filename)
            print("Model saved to file", filename)

        print("Training Doc2Vec network... DONE!")
    embeddings = []

    for idx, article in enumerate(corpus):
        embeddings.append(text_model[idx])

    return embeddings
