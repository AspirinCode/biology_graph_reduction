# Biological Network Reduction for Graph-Based Machine Learning

This repo provides algorithms and examples for the network reduction for different biological networks (protein-protein interaction, DNA, drug-target interaction). The reduction is necessary for the machine learning applications since most of these networks are large and sparse (both topological and feature-wise). The size of the networks makes them difficult for certain applications (graph classification). And the sparsity in features also poses trouble for the machine learning models since the useful information can be well scattered in the network. Imagine looking at two images with only handful of pixels differen and try to find the underlying difference. Thus it is important to reduce the networks before they can be used for any graph-based machine learning.

This README file is written by Limeng Pu.

# Prerequisites

1. Python 3
2. pandas 0.25.1 +
3. networkx 2.2 +
4. numpy 1.16.2 +
