import matplotlib.pyplot as plt
from MulticoreTSNE import MulticoreTSNE as TSNE
import numpy as np


# def prepare_data(vectors, labels):
#     new_vectors = []
#     area = []
#     def_area = 1
#     threshold = 0.05

#     for idx, label in enumerate(set(labels)):
#         x = vectors[np.where(labels == label), 0:1]
#         dist_mx = euclidean_distances(x)

#         for row in dist_mx:
#             dist_idx_list = np.argsort(row)


def plot_data(vectors, labels, title, file):
    tsne = TSNE(n_components=2, n_jobs=4, random_state=1)
    x_2d = tsne.fit_transform(vectors)
    # area, x_2d = prepare_data(x_2d, labels)

    plt.rcParams.update({'font.size': 24})
    plt.figure(figsize=(25, 25))

    for idx, label in enumerate(set(labels)):
        plt.scatter(x_2d[np.where(labels == label), 0],
                    x_2d[np.where(labels == label), 1],
                    s=15,
                    label=label,
                    alpha=0.5)

    plt.legend(loc='best', scatterpoints=1)
    plt.title(title)
    plt.savefig(file)
