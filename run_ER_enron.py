# create test cases for the functions in createRankings.py
"""
This script performs the following tasks:
1. Generates a random directed and weighted graph using the Erdos-Renyi 
2. Perturbs some links of the generated network, creating 'ghosts', and 'mushrooms'.
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
- os
- networkx (as nx)
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
import pandas as pd

def run():

    df0 = pd.read_csv('/Users/acapozzi/Desktop/ISP/weirdFlowsEnron/data_enron/edgelist/edgelist_2001_4_30.csv')
    df1 = pd.read_csv('/Users/acapozzi/Desktop/ISP/weirdFlowsEnron/data_enron/edgelist/edgelist_2001_5_31.csv')
    df0 = df0.rename(columns={'count': 'weight'})
    df1 = df1.rename(columns={'count': 'weight'})

    print('creating the graphs...')
    g0 = nx.from_pandas_edgelist(df0, edge_attr='weight', create_using=nx.DiGraph())
    g1 = nx.from_pandas_edgelist(df1, edge_attr='weight', create_using=nx.DiGraph())

    print('Adding types to nodes...')
    g0 = nper.add_node_type(g0)
    g1 = nper.add_node_type(g1)

    print('Add nodes to both graphs...')
    g0.add_nodes_from((node, g1.nodes[node]) for node in g1.nodes)
    g1.add_nodes_from((node, g0.nodes[node]) for node in g0.nodes)

    print('Map nodes names...')
    all_nodes = list(set(g1.nodes).union(set(g0.nodes)))
    node_mapping = {name: i for i, name in enumerate(all_nodes)}
    g0 = nx.relabel_nodes(g0, node_mapping)
    g1 = nx.relabel_nodes(g1, node_mapping)
    mapping_df = pd.DataFrame(list(node_mapping.items()), columns=["Original_Name", "Integer_ID"])
    mapping_df.to_csv("/Users/acapozzi/Desktop/ISP/weirdFlowsEnron/data_enron/nodes_mapping.csv", index=False)

    # # Generate a random directed and weighted graph with Erdos-Renyi model
    # g0 = nx.gnm_random_graph(n=NUM_NODES, m=NUM_LINKS, directed=True)

    # # Add weights to the edges
    # for u, v, d in g0.edges(data=True):
    #     d['weight'] = abs(RANDOM_FUNCTION(MEAN, STD_DEV))  # select random weights from a the distribution set in config.py
       
    # # Create the perturbation by nodes 
    # print("Perturbating the network by perturbating some edges' weights...")
    # g1 = nper.perturb_network_by_links(g0, NUM_LINKS_TO_PERTURB)
    
    weirdnodes(g0, g1) # Detect outliers in the network
run()