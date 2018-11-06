import matplotlib.pyplot as plt
import numpy as np


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
