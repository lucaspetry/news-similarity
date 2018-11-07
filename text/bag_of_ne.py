import numpy as np


def bon_from_news(named_entities):
    entities = set()

    for ent in named_entities:
        entities.union(ent)

    entities = np.asarray(list(entities))
    vectors = np.zeros(shape=(len(named_entities), len(entities)))

    for idx, ent in enumerate(named_entities):
        vectors[idx][np.isin(entities, ent)] = 1
