# create test cases for the functions in createRankings.py
"""
This script performs the following tasks:
1. Generates a random directed and weighted graph using the Erdos-Renyi 
2. Perturbs some nodes of the generated network, creating 'intermediaries', 'indirect_sources', and 'indirect_targets'.
3. Calculates and ranks nodes by various centrality measures.
4. Plots and compares the graphs based on centrality measures.
5. Calculates concordance between the rankings of the original and perturbd graphs.
6. Stores the concordance results in a file.
7. Plots the ranked nodes comparison and identifies the top k nodes based on rank residuals.
8. Stores the top k nodes in a file.
9. Calculates precision, recall, average precision, and mean average precision at k for the top k nodes.
10. Stores the evaluation results in files.
11. Plots the evaluation results.
12. Stores the graphs in GML files.
13. Stores nodes ranks and other attributes in CSV files.
14. Stores graphs' basic metrics in a file.
Used modules in the weirdflows package:
- create_rankings (as cr)
- concordance_check (as cc)
- net_perturbation (as nper)
- evaluation (as ev)
Used external modules:
- matplotlib.pyplot (as plt)
- os
- networkx (as nx)
- numpy (as np)
- scipy.stats.spearmanr
- config
Configuration:
- NUM_NODES: Number of nodes in the graph.
- NUM_LINKS: Number of links in the graph.
- NUM_NODES_TO_PERTURB: Number of nodes to perturb in the graph.
- CENTRALITY_MEASURES: List of centrality measures to be calculated.
- WORKING_DIRECTORY: Directory to store the results.
- TOP_K: Number of top nodes to consider for evaluation.
Functions:
- perturb_network_by_nodes: Perturbs the network by nodes.
- rank_nodes_by_centrality: Ranks nodes by the given centrality measure.
- plot_graphs_comparison: Plots and compares the graphs based on centrality measures.
- concordance_check: Calculates concordance between the rankings.
- plot_ranked_nodes_comparison: Plots the ranked nodes comparison.
- precision_at_k: Calculates precision at k.
- recall_at_k: Calculates recall at k.
- avg_precision_at_k: Calculates average precision at k.
- store_nodes_ranks: Stores nodes ranks and other attributes in CSV files.
"""

import net_perturbation as nper
import networkx as nx
from config import *
from outliers_detection_proc import weirdnodes

def run():
    # Generate a random directed and weighted graph with Erdos-Renyi model
    g0 = nx.gnm_random_graph(n=NUM_NODES, m=NUM_LINKS, directed=True)

    # Add weights to the edges
    for u, v, d in g0.edges(data=True):
        d['weight'] = abs(RANDOM_FUNCTION(MEAN, STD_DEV))  # select random weights from a the distribution set in config.py
       
    # Create the perturbation by nodes 
    print("Perturbating the network by adding intermediary nodes...")
    g1 = nper.perturb_network_with_intermediary_nodes(g0, NUM_LINKS_TO_PERTURB, NUM_INTERMEDIARY_NODES)
    
    weirdnodes(g0, g1) # Detect outliers in the network