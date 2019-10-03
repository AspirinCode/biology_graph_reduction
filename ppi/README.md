# Protein-Protein Interaction Network Reduction

This is an example of network reduction for PPI network.

1. Network representation

    The network is represented as a node table and an edge table. The node table takes the following format:
    
    |   node_id   |   feature_1   |   feature_2   |   ...   |   feature_m   |
    |:---:|:---:|:---:|:---:|:---:|
    | ENSEMBLID_1 | x1_1 | x1_2 | ... | x1_m |
    | ENSEMBLID_2 | x2_1 | x2_2 | ... | x2_m |
    | ... | ... | ... | ... | ... | ... |
    | ENSEMBLID_n | xn_1 | xn_2 | ... | xn_m |

    The node table is the table collected by the user. It contains any features you wish to use for your purpose. However, the node presented in the node table must also be presented in the edge table. Otherwise, the network will have an isolated node, which won't propagate any information in terms for the graph feature extraction.

    An example of the edge table is shown as follow:
    
    |   node1_id   |   node2_id   |   score   |
    |:---:|:---:|:---:|
    | ENSEMBLID_1 | ENSEMBLID_2 | s_12 |
    | ENSEMBLID_1 | ENSEMBLID_3 | s_13 |
    | ... | ... | ... |
    | ENSEMBLID_n | ENSEMBLID_k | s_nk |

    The edge table is the connections provided by the STRING database. It often require some preprocess (connected component) based on particular applications.
    
    These two tables are often enough to represent the PPI network.
    
2. Network reduction

    The network reduction is highly correlated with the applications/purpose of the study since it is related to certain node features. In this example, we presented a simple case. We reduce the network by contracting edges (merging nodes), whose two nodes (proteins) belong to the same pathway AND have the same gene expression AND neither of them are kinases. In order to do that, we loaded the following data:
    
    - `./data/master_edge_table.csv` -- The edge table from STRING as described above. NOTE that this is not the original string. Only interactions with score above 500 is retained and some isolated proteins are removed.
    - `./data/affinity.csv` -- Binding affinity data. This has no effect on the network reduction. It is used to load add the binding affinity features to nodes.
    - `./data/pathway_info.csv` -- Pathway information of all the proteins in the processed STIRING. "unknown" is used for the missing values.
    - `./data/diseases_scores.csv` -- Disease related importance scores of all the proteins in the processed STIRING. 0 is used for the missing values.
    - `./data/kinases.pkl` -- A list of all kinases.
    - `./data/1321N1.csv` -- Gene expressions of all the proteins in the processed STIRING. The missing values are filled by the majority of the neighbors' gene expression.
