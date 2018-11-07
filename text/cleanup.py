import nltk
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer
import string


nltk.download('rslp')
nltk.download('stopwords')
stemmer = RSLPStemmer()
stops = set(stopwords.words("portuguese"))


def cleanup_text(body='', title='', subtitle='',
                 remove_stopwords=True, stem=False):
    text = merge_text(title, subtitle, body).lower().split()

    if remove_stopwords:
        text = [w for w in text if not w in stops]

    if stem:
        text = [stemmer.stem(w) for w in text]

    text = " ".join(text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text


def merge_text(title, subtitle, text):
    return title + ' ' + subtitle + ' ' + text
