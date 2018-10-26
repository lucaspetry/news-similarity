from news_loader import load_news
import os
import string
import nltk
from nltk.corpus import stopwords
from gensim.models import Doc2Vec
from gensim.models.doc2vec import LabeledSentence
from gensim import utils
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd


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

nltk.download('stopwords')
news = load_news(fields=['id', 'title', 'portal', 'text'])

for article in news:
    article['text'] = cleanup_text(article['text'])


##################################
# Create sentences
##################################
sentences = []

for article in news:
    sentences.append(
        LabeledSentence(utils.to_unicode(article['text']).split(),
                        ['Text' + '_%s' % str(article['id'])]))
# TO-DO - Lucas: change for taggeddocument


##################################
# Learn or load doc embeddings
##################################
embedding_size = 100
text_model = None
filename = 'newsEmbeddings_5_clean.d2v'

if os.path.isfile(filename):
    text_model = Doc2Vec.load(filename)
else:
    text_model = Doc2Vec(min_count=1,  # Ignores words with lower counts than this
                         window=5,  # The size of the context window
                         size=embedding_size,
                         #sample=1e-4,
                         #negative=0,
                         workers=4,
                         iter=100,
                         seed=1)
    text_model.build_vocab(sentences)
    text_model.train(sentences,
                     total_examples=text_model.corpus_count,
                     epochs=text_model.iter)
    text_model.save(filename)

embeddings = []
doc2int = dict(zip([s[1][0] for s in sentences], np.r_[0:len(sentences)]))

for sentence in sentences:
    embeddings.append(text_model[sentence[1][0]])

sim_mx = np.absolute(cosine_similarity(embeddings))

# Gambi, just because
for i in range(0, len(sim_mx)):
    sim_mx[i][i] = -9999

# Just a first draft of the result
result = {
    'id': [],
    'title': [],
    'portal': [],
    'most_sim_id': [],
    'most_sim_title': [],
    'most_sim_portal': [],
    'most_sim_score': []
}

for idx, article in enumerate(news):
    doc_id = sentences[idx][1][0]
    #doc_idx = doc2int[doc_id]

    sim_idx = np.argmax(sim_mx[idx])

    result['id'].append(article['id'])
    result['title'].append(article['title'])
    result['portal'].append(article['portal'])
    result['most_sim_id'].append(news[sim_idx]['id'])
    result['most_sim_title'].append(news[sim_idx]['title'])
    result['most_sim_portal'].append(news[sim_idx]['portal'])
    result['most_sim_score'].append(sim_mx[idx][sim_idx])

pd.DataFrame.from_dict(result).to_csv('doc2vec_result.csv', index=False)
