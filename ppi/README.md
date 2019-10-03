# Protein-Protein Interaction Network Reduction

This is an example of network reduction for PPI network.

1. Data representation

  The network is represented as a node table and an edge table. The node table takes the following format
  |   node_id   |   feature_1   |   feature_2   |   ...   |   feature_m   |
  |:---:|:---:|:---:|:---:|
  | ENSEMBLID_1 | x1_1 | x1_2 | ... | x1_m |
  | ENSEMBLID_2 | x2_1 | x2_2 | ... | x2_m |

  The node table is the table collected by the user. It contains any features you wish to use for your purpose. However, the node presented in the node table must also be presented in the edge table. Otherwise, the network will have an isolated node, which won't propagate any information in terms for the graph feature extraction.

  An example of the edge table is shown as follow
