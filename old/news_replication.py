import numpy as np
from news_loader import load_news
from text.cleanup import cleanup_text
from joblib import Parallel, delayed
import multiprocessing
from clustering import jaccard_distances
from text.nel import nel_from_news


n_jobs = multiprocessing.cpu_count()


def get_replication(news, sim_matrix, threshold=0.7):
    portals = set([article['portal'] for article in news])
    replication = dict(zip(portals, np.zeros(len(portals))))
    obs = dict(zip(portals, [[] for _ in range(0, len(portals))]))

    for idx, article in enumerate(news):
        portal = article['portal']
        for idx2, article2 in enumerate(news):
            if idx >= idx2 or portal != article2['portal']:
                continue

            if sim_matrix[idx][idx2] >= threshold:
                replication[portal] += 1
                obs[portal].append((news[idx]['id'], news[idx2]['id']))

    return replication, obs


def load_cleaned_news(remove_stopwords=True, stem=False):
    news = load_news(fields=['id', 'title', 'subtitle', 'subject', 'portal', 'text'])

    results = Parallel(n_jobs=n_jobs)(delayed(cleanup_text)(article['text'],
                                                            article['title'],
                                                            article['subtitle'],
                                                            remove_stopwords,
                                                            stem) for article in news)

    for idx, article in enumerate(news):
        article['new_text'] = results[idx]
    return news


print("Loading news...")

news_nel = load_cleaned_news(remove_stopwords=False, stem=False)
corpus_nel = [article['text'] for article in news_nel]

coords = nel_from_news(corpus_nel, filename='data/vectors_nel.bin')
vectors_sim = (1 - jaccard_distances(coords))


print("Counting Breaking News with .8 threshold")
replication, obs = get_replication(news_nel, vectors_sim, threshold=0.8)
print(replication)

print("Counting Breaking News with .9 threshold")
replication, obs = get_replication(news_nel, vectors_sim, threshold=0.9)
print(replication)
print(obs)
