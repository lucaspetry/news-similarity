# Similarity Metrics Analysis in Newspapers

Source code and results for the paper "Mining Journals to the Ground: An Exploratory Analysis of Newspaper Articles", published in the proceedings of the 8th Brazilian Conference on Intelligent Systems (BRACIS).

### Cite

```
@inproceedings{silva2019mining,
    author={Camila Leite da Silva and Lucas May Petry and Vinicius Freitas and Carina Friedrich Dorneles},
    booktitle={8th Brazilian Conference on Intelligent Systems (BRACIS)}, 
    title={Mining Journals to the Ground: An Exploratory Analysis of Newspaper Articles}, 
    year={2019},
    volume={8},
    pages={78-83},
    month={Oct}
}
```

### Clustering Experiment

* [DBSCAN - Source code](exp_clustering_dbscan.py)
* [DBSCAN - Results](exp_clustering_dbscan_results.csv)
* [Hierarchical Agglomerative Clustering - Source code](exp_clustering_agglomerative.py)
* [Hierarchical Agglomerative Clustering - Results](exp_clustering_agglomerative_results.csv)

### News Replication Experiment

* [Source code](exp_replication.py)
* [Results](exp_replication_results.csv)

### News Spreading Experiment

* [Source code](exp_spreading.py)
* [Results](exp_spreading_results.csv)

### Data

* [Plain (SQL) - Compressed](data/database_plain.tar.xz)
* [Postgres Binary](data/database_postgres_binary.backup)
