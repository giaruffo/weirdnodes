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

import create_rankings as cr
import concordance_check as cc
import net_perturbation as nper
import evaluation as ev
import os
import networkx as nx
from scipy.stats import spearmanr
from config import *

def run():
    # Generate a random directed and weighted graph with Erdos-Renyi model
    g0 = nx.gnm_random_graph(n=NUM_NODES, m=NUM_LINKS, directed=True)

    # Add weights to the edges
    for u, v, d in g0.edges(data=True):
        d['weight'] = abs(RANDOM_FUNCTION(MEAN, STD_DEV))  # select random weights from a the distribution set in config.py
       
    # Create the perturbation by nodes 
    print("Perturbating the network by perturbating nodes and edges...")
    g01 = nper.perturb_network_by_links(g0, NUM_LINKS_TO_PERTURB)
    g02 = nper.perturb_network_by_nodes(g01, NUM_NODES_TO_PERTURB)
    g1 = nper.perturb_network_with_intermediary_nodes(g02,  NUM_LINKS_TO_PERTURB, NUM_INTERMEDIARY_NODES)

    
    print("-----------------------------------")

    # set the centrality measures to be calculated
    for centrality_measure in CENTRALITY_MEASURES:
        # show the differences between the two graphs
        # print("Graph 0 and Graph 1 differences:")
        # print(nx.difference(g0, g1).edges(data=True))

        # rank the nodes by the given centrality
        print(f"Calculating {centrality_measure}, and ranking nodes accordingly...")
        cr.rank_nodes_by_centrality(g0, centrality_measure)
        cr.rank_nodes_by_centrality(g1, centrality_measure)

        # store the ranks of the nodes in a dictionary for both graphs
        ranks = {}
        ranks['g0'] = [g0.nodes[i][f'{centrality_measure}_rank'] for i in g0.nodes()]
        ranks['g1'] = [g1.nodes[i][f'{centrality_measure}_rank'] for i in g1.nodes()]

        # store the centrality sequence of the graphs 
        centralities_g0 = g0.nodes(data=centrality_measure)
        centralities_g1 = g1.nodes(data=centrality_measure)

        # plot graphs with the same layout and save them to files
        print("Plotting graphs...")
        nper.plot_graphs_comparison(g0, g1, centralities_g0, centralities_g1, centrality_measure)

        # Calculate the concordance between the two rankings
        print(f"Calculating concordance between the two rankings (by {centrality_measure})...")
        kendallSignal, kendall = cc.concordance_check(ranks['g0'], ranks['g1'])
        spearmanSignal, spearman = cc.concordance_check(ranks['g0'], ranks['g1'], spearmanr)

        # store the concordance results in a file in the working directory as defined in config.py
        concordance_file_path = os.path.join(WORKING_DIRECTORY+f'/rank_correlations', f"concordance_by{centrality_measure}.txt")
        with open(concordance_file_path, "w") as f:
            f.write(f"Kendall's tau: {kendall}\n")
            f.write(f"Spearman's rho: {spearman}\n")
            f.write(f"Kendall's tau signal: {kendallSignal}\n")
            f.write(f"Spearman's rho signal: {spearmanSignal}\n")

        # plot the ranked nodes comparison and get the top k nodes sorted by the 
        # absolute value of the residuals of the ranks
        print(f"Plotting ranked nodes (by {centrality_measure}) comparison...")
        top_k_nodes = cr.plot_ranked_nodes_comparison(g1, ranks['g0'], ranks['g1'], centrality_measure)

        # store the top k nodes in a file in the working directory as defined in config.py
        strategy = f'{centrality_measure}based'
        print(f"Storing top k nodes (sorted by {centrality_measure}'s ranks residuals) in a file...")
        ev.store_top_k_nodes_in_file(g1, top_k_nodes, strategy)
        
        # calculate precision, recall, average precision and mean average precision at k, for k = 1,..., 30
        # using function in evaluation.py
        print(f"Calculating evaluation results (strategy: {strategy})...")
        precisions, recalls, avg_precisions = ev.evaluate_results(g1, top_k_nodes)

        # store and plot the results in a file in the working directory as defined in config.py
        ev.store_and_plot_evaluation_results(strategy, precisions, recalls, avg_precisions)
        
        # save evaluation summary in a latex file
        ev.create_latex_tabular(centrality_measure, precisions, recalls, avg_precisions)
        
        print("-----------------------------------")

    # store graphs in files in the working directory as defined in config.py
    print("Storing graphs in gml files...")
    nx.write_gml(g0, os.path.join(WORKING_DIRECTORY+'/graphs', 'g0.gml'))
    nx.write_gml(g1, os.path.join(WORKING_DIRECTORY+'/graphs', 'g1.gml'))

    # store nodes ranks and other attributes in files in the working directory as defined in config.py as csv files
    print("Storing nodes ranks and other attributes in csv files...")
    for graph_name in ['g0', 'g1']:
        cr.store_nodes_ranks(locals()[graph_name], graph_name, CENTRALITY_MEASURES)

    # store graphs' basic metrics in a file under WORKING_DIRECTORY+'/graphs'
    print("Storing graphs' basic metrics in a file...")
    with open(os.path.join(WORKING_DIRECTORY+'/graphs', 'graphs_metrics.txt'), 'w') as f:
        for graph_name in ['g0', 'g1']:
            g = locals()[graph_name]
            nper.store_graph_metrics_infile(f, g, graph_name)

    # store degree, indegree, outdegree, strength, in_strength, out_strength, and weight distributions in a file under WORKING_DIRECTORY+'/plots'
    print("Storing degree, indegree, outdegree, strength, in_strength, out_strength, and weight distributions in a file...")
    for graph_name in ['g0', 'g1']:
        g = locals()[graph_name]
        nper.plot_graph_distributions(g, graph_name)
    print("Graphs' degree/strength distributions saved.") 
    
    print("Done.")

    


