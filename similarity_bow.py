"""
Bag of Words (BoW)
"""
import nltk
import string
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS as en_sw
from nltk.corpus import stopwords

# as seen in similarity_doc2vec
def cleanup_text(text, remove_stopwords=True):
    text = text.lower().split() # Split text into array of words, lower case
    if remove_stopwords: # Remove portuguese stopwords
        ignore = set(stopwords.words("portuguese"))
        text = [w for w in text if not w in ignore]
    text = " ".join(text) # Make text into a string again
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text

def cleanup_corpus(corpus, remove_stopwords=True):
    retval = list()
    for sentence in corpus:
        clean_text = cleanup_text(sentence, remove_stopwords)
        retval.append(clean_text)
    return retval

def vectorize_sentences(sentences, normalize_words=True):
    corpus = cleanup_corpus(sentences)
    vectorizer = CountVectorizer()
    grid_word_count = vectorizer.fit_transform(corpus).toarray()
    # If not weighted words, simply return the counts from vectorizer
    if not normalize_words:
        return grid_word_count

    normalized_grid = list()
    corpus_index = 0
    for sentence in grid_word_count:
        s_len = len(corpus[corpus_index].split()) # Count words in sentence
        n_list = list()
        for word in sentence:
            n_word = float(word/float(s_len)) # Calc normalized word weight
            n_list.append(n_word)
        normalized_grid[corpus_index].append(n_list)
    return normalized_grid

# A higher SAD means 2 pieces of text are less similar
# So we'll return 1 - SAD for NORMALIZED vectors
# and 1/SAD for INTEGER values
def sad_similarity(s_first, s_second, normalized=True):
    if len(s_first) != len(s_second):
        print("ERROR!! SAD_SIM: Values must be vectorized first!! Stop!")
        exit()
    ad_list = list()
    end = len(s_first)
    i = 0
    while i < end:
        ad = abs(s_first[i] - s_second[i])
        ad_list.append(float(ad))
        i += 1
    sad = float(sum(ad_list))
    if normalized:
        return 1-sad
    else:
        return float(1/sad)

# Testing here:
corpus = [
    "Todos os amigos estao em fila.",
    "Todo mundo podia pular a janela!",
    "Alguem fugiu pela janela.",
    "Voces viram os gatos fugindo em fila?"
]
s_first = corpus[2]
s_second = corpus[1]
vector = vectorize_sentences([s_first,s_second])
i_vector = vectorize_sentences([s_first,s_second], False)
print(vector)
n_sim = sad_similarity(vector[0], vector[1])
i_sim = sad_similarity(i_vector[0], i_vector[1], False)
print(n_sim)
print(i_sim)
