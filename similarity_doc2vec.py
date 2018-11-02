"""
Paragraph Vector (Doc2Vec)
"""
from news_loader import load_news, add_score
import os
import string
import nltk
from nltk.corpus import stopwords
from gensim.models import Doc2Vec
from gensim.models.doc2vec import LabeledSentence
from gensim import utils
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


##################################
# Clean text
##################################
def cleanup_text(text, remove_stopwords=True):
    text = text.lower().split()

    if remove_stopwords:
        stops = set(stopwords.words("portuguese"))
        text = [w for w in text if not w in stops]

    text = " ".join(text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text


def merge_text(title, subtitle, text):
    return title + ' ' + subtitle + ' ' + text


def load_cleaned_news():
    nltk.download('stopwords')
    news = load_news(fields=['id', 'title', 'subtitle', 'portal', 'text'])

    for article in news:
        article['new_text'] = cleanup_text(merge_text(article['title'],
                                                      article['subtitle'],
                                                      article['text']))
    return news


##################################
# Create sentences
##################################
print("Loading news.")
news = load_cleaned_news()
sentences = []

for article in news:
    sentences.append(
        LabeledSentence(utils.to_unicode(article['new_text']).split(),
                        [article['id']]))


##################################
# Learn or load doc embeddings
##################################
print("Training Doc2Vec network.")

embedding_size = 200
text_model = None
filename = 'similarity_doc2vec_data.d2v'

if os.path.isfile(filename):
    text_model = Doc2Vec.load(filename)
else:
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
    text_model.save(filename)

embeddings = []
doc2int = dict(zip([article['id'] for article in news], np.r_[0:len(news)]))

for article in news:
    embeddings.append(text_model[article['id']])

print("Computing and storing similarity scores.")
sim_mx = np.absolute(cosine_similarity(embeddings))

# Gambi, just because
for i in range(0, len(sim_mx)):
    sim_mx[i][i] = -9999

count = 0

for article1 in news:
    id1 = article1['id']
    idx1 = doc2int[id1]
    portal1 = article1['portal']

    for article2 in news:
        id2 = article2['id']
        idx2 = doc2int[id2]
        portal2 = article2['portal']

        if id1 > id2 or portal1 == portal2:
            continue

        score = sim_mx[idx1][idx2]

        if score > 0.1:
            add_score([id1, id2], 'score_doc2vec', score)

    count += 1
    print('News', count, 'out of', len(news), 'done.')

print("Done.")
