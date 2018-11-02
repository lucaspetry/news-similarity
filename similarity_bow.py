"""
Bag of Words (BoW)
"""
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS as en_sw

debug = True
corpus = [
    "Todos os amigos estao em fila.",
    "Todo mundo podia pular a janela!",
    "Alguem fugiu pela janela.",
    "Voces viram os gatos fugindo em fila?"
]
pt_stop_words = ['.','?','!',',','e','ou','a','as','o','os','em']
pt_stop_words = en_sw.union(pt_stop_words)
vectorizer = CountVectorizer(stop_words=pt_stop_words)
grid_word_count = vectorizer.fit_transform(corpus).toarray()
corpus_index = 0
grid_weighted_words = []
for sentence in grid_word_count:
    sentence_len = len(corpus[corpus_index].split())
    grid_weighted_words.append([])
    for word in sentence:
        normalized_word = float(word/float(sentence_len)) # This is still counting stop words!!
        grid_weighted_words[corpus_index].append(normalized_word)
    corpus_index += 1
if debug:
    for sentence in grid_weighted_words:
        print(sentence)
print("----***----")
