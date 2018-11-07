import matplotlib.pyplot as plt
import numpy as np
from text.doc2vec import doc2vec_from_news
from sklearn.metrics.pairwise import cosine_similarity
from news_loader import load_news
from text.cleanup import cleanup_text
from joblib import Parallel, delayed
import multiprocessing
from clustering import jaccard_distances
from text.nel import nel_from_news


n_jobs = multiprocessing.cpu_count()


def get_spreading(news, sim_matrix, threshold=0.7):
    spread_count = list()
    portals = set([article['portal'] for article in news])

    def par_spread(idx):
        most_sim = dict(zip(portals, np.zeros(len(portals))))
        for idx2, article2 in enumerate(news):
                portal = article2['portal']
                if sim_matrix[idx][idx2] > most_sim[portal] and sim_matrix[idx][idx2] >= threshold:
                    most_sim[portal] = sim_matrix[idx][idx2]

        return np.count_nonzero(list(most_sim.values()))

    spread_count = Parallel(n_jobs=1)(delayed(par_spread)(idx) for idx,_ in enumerate(news))
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

def count_nel_jac(corpus):
    coords = nel_from_news(corpus, filename='data/vectors_nel.bin')
    return (1 - jaccard_distances(coords))
    
def count_doc2vec(corpus):
    doc_vectors = doc2vec_from_news(corpus, filename='data/vectors_doc2vec.bin')
    vectors_sim = cosine_similarity(doc_vectors)
    return vectors_sim

def count_bow(corpus):
    return ""

def count_breaking(corpus, technique="neljac"):
    if technique == "neljac":
        return count_nel_jac(corpus)
    elif technique == "doc2vec":
        return count_doc2vec(corpus)
    else:
        return count_bow(corpus)


print("Loading news...")

news_nel = load_cleaned_news(remove_stopwords=False, stem=False)
news_no_stem = load_cleaned_news(remove_stopwords=True, stem=False)

corpus_nel = [article['text'] for article in news_nel]
corpus_no_stem = [article['new_text'] for article in news_no_stem]

vectors_sim = count_breaking(corpus_nel, "neljac")

print("Counting Breaking News with .7 threshold")
breaking_news07 = list()
news_spread = get_spreading(news_nel, vectors_sim, threshold=0.4)
x = [1, 2, 3, 4, 5]
y = np.zeros(5)

for idx,count in enumerate(news_spread):
    if count == 4:
        breaking_news07.append(news_nel[idx]['id'])
    y[count - 1] += 1

print(x)
print(y)
print(breaking_news07)

print("Counting Breaking News with .8 threshold")
breaking_news08 = list()
news_spread = get_spreading(news_nel, vectors_sim, threshold=0.5)
x = [1, 2, 3, 4, 5]
y = np.zeros(5)

for idx,count in enumerate(news_spread):
    if count >= 3:
        breaking_news08.append(news_nel[idx]['id'])
    y[count - 1] += 1

print(x)
print(y)
print(breaking_news08)

#Result doc2vec
#[1, 2, 3, 4, 5]
#[6711. 1946.  131.   25.    0.]
#[12548, 15545, 21388, 22721, 24657, 24736, 24789, 24906, 25013, 25181, 25279, 25349, 25411, 25491, 25663, 25755, 25811, 25912, 26003, 26066, 26190, 26259, 26378, 26552, 27099]
#Counting Breaking News with .8 threshold
#[1, 2, 3, 4, 5]
#[6940. 1855.   18.    0.    0.]
#[8586, 8779, 12051, 12688, 12958, 15938, 24693, 24704, 25075, 25396, 25538, 26259, 27118, 27188, 27330, 27518, 27519, 27683]