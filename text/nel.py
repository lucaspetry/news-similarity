import spacy
import pickle
import os
from joblib import Parallel, delayed
import multiprocessing


FAKE_ENTITIES = ['folhapress--', 'folhapress']
num_cores = multiprocessing.cpu_count()


def entities_to_lower(tuples):
    ret_val = []
    for en in list(tuples):
        if str(en).lower() not in FAKE_ENTITIES:
            ret_val.append(str(en).lower())

    return set(ret_val)


def get_entities(text):
    nlp = spacy.load('pt_core_news_sm')
    nlp_text = nlp(text)
    return entities_to_lower(nlp_text.ents)


def load(filename):
    with open(filename, "rb") as fp:
        return pickle.load(fp)


def save(list, filename):
    with open(filename, "wb") as fp:
        pickle.dump(list, fp)


def nel_from_news(news, filename):
    entity_lists = []

    if filename and os.path.isfile(filename):
        entity_lists = load(filename)
    else:
        entity_lists = Parallel(n_jobs=num_cores)(delayed(get_entities)(article) for article in news)
        save(entity_lists, filename)

    return entity_lists
