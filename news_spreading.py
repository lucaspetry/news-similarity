import matplotlib.pyplot as plt
import numpy as np
from text.doc2vec import doc2vec_from_news
from sklearn.metrics.pairwise import cosine_similarities
from news_loader import load_news
from text.cleanup import cleanup_text
from joblib import Parallel, delayed
import multiprocessing


n_jobs = multiprocessing.cpu_count()


def get_spreading(news, sim_matrix, threshold=0.8):
    spread_count = {}
    portals = set([article['portal'] for article in news])

    for idx, article in enumerate(news):
        most_sim = dict(zip(portals, np.zeros(len(portals))))

        for idx2, article in enumerate(news):
            portal = article['portal']

            if sim_matrix[idx][idx2] > most_sim[portal] and sim_matrix[idx][idx2] >= threshold:
                most_sim[portal] = sim_matrix[idx][idx2]

        spread_count[idx] = np.count_nonzero(most_sim.values())
    return spread_count


def plot_data(vectors, labels, title, file):
    sorted_labels = sorted(list(set(labels)))

    plt.rcParams.update({'font.size': 28})
    fig = plt.figure(figsize=(35, 25))
    ax = fig.add_subplot(1, 1, 1)
    colors = ['red', 'hotpink', 'steelblue', 'orange',
              'darkviolet', 'sienna', 'limegreen', 'darkblue']
    handles = []

    for idx, label in enumerate(sorted_labels):
        p = plt.scatter(vectors[np.where(labels == label), 0],
                        vectors[np.where(labels == label), 1],
                        c=colors[idx],
                        linewidths=10,
                        label=label,
                        alpha=0.7)
        handles.append(p)

    plt.legend(loc='best', scatterpoints=1)
    plt.title(title)
    ax.legend(markerscale=4, handles=handles, labels=sorted_labels)
    plt.savefig(file, bbox_inches='tight')


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
news_no_stem = load_cleaned_news(remove_stopwords=True, stem=False)
corpus_no_stem = [article['new_text'] for article in news_no_stem]

doc_vectors = doc2vec_from_news(corpus_no_stem, filename='data/vectors_doc2vec.bin')
vectors_sim = cosine_similarities(doc_vectors)

news_spread = get_spreading(news_no_stem, vectors_sim, threshold=0.8)
x = [1, 2, 3, 4, 5]
y = np.zeros(5)

for news in news_spread:
    y[news_spread[news] - 1] += 1

print(x)
print(y)
