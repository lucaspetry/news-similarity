from news_loader import load_news
import os
import string
import nltk
from nltk.corpus import stopwords
from gensim.models import Doc2Vec
from gensim.models.doc2vec import LabeledSentence
from gensim import utils


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
news = load_news(fields=['text'])

for article in news:
    article['text'] = cleanup_text(article['text'])


##################################
# Create sentences
##################################
sentences = []

for index, article in enumerate(news):
    sentences.append(
        LabeledSentence(utils.to_unicode(article['text']).split(),
                        ['Text' + '_%s' % str(index)]))


##################################
# Learn or load doc embeddings
##################################
embedding_size = 300
text_model = None
filename = 'newsEmbeddings_5_clean.d2v'

if os.path.isfile(filename):
    text_model = Doc2Vec.load(filename)
else:
    text_model = Doc2Vec(min_count=1,  # Ignores words with lower counts than this
                         window=5,  # The size of the context window
                         size=embedding_size,
                         sample=1e-4,
                         negative=5,
                         workers=4,
                         iter=5,
                         seed=1)
    text_model.build_vocab(sentences)
    text_model.train(sentences,
                     total_examples=text_model.corpus_count,
                     epochs=text_model.iter)
    text_model.save(filename)

print(len(text_model[sentences[0][0][0]]))
