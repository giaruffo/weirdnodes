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

import create_rankings as cr
import concordance_check as cc
import net_perturbation as nper
import evaluation as ev
import matplotlib.pyplot as plt
import os
import networkx as nx
import numpy as np
from scipy.stats import spearmanr
from config import *

if __name__ == "__main__":
    # Generate a random directed and weighted graph with Erdos-Renyi model
    g0 = nx.gnm_random_graph(n=NUM_NODES, m=NUM_LINKS, directed=True)

    # Add weights to the edges
    for u, v, d in g0.edges(data=True):
        d['weight'] = abs(RANDOM_FUNCTION(MEAN, STD_DEV))  # select random weights from a the distribution set in config.py
       
    # Create the perturbation by nodes 
    print("Perturbating the network by adding intermediary nodes...")
    g1 = nper.perturb_network_with_intermediary_nodes(g0, NUM_LINKS_TO_PERTURB, NUM_INTERMEDIARY_NODES)
    
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
        strategy = f'sorting_by{centrality_measure}_rankresiduals'
        print(f"Storing top k nodes (sorted by {centrality_measure}'s ranks residuals) in a file...")
        top_k_nodes_file_path = os.path.join(WORKING_DIRECTORY+'/evaluation_results', f"topknodes_{centrality_measure}based.txt")
        with open(top_k_nodes_file_path, "w") as f:
            f.write(f"Top {TOP_K} nodes sorted by the absolute value of the residuals of the ranks:\n")
            for node in top_k_nodes:
                f.write(f"{node}\t")
                # write node type to file
                f.write(f"Type: {g1.nodes[node[0]]['type']}\n")
        
        # calculate precision, recall, average precision and mean average precision at k, for k = 1,..., 30
        # using function in evaluation.py
        print(f"Calculating evaluation results (strategy: {strategy})...")
        precisions = []
        recalls = []   
        avg_precisions = []
        for i in range(1, TOP_K+1):
            precision = ev.precision_at_k(g1, top_k_nodes[:i], i)
            recall = ev.recall_at_k(g1, top_k_nodes[:i], i)
            average_precision = ev.avg_precision_at_k(g1, top_k_nodes[:i], i)
            # print(f"P@{i}: {precision}")
            # print(f"R@{i}: {recall}")
            # print(f"avg P@{i}: {average_precision}")
            precisions.append(precision)
            recalls.append(recall)
            avg_precisions.append(average_precision)

        # store the results in a file in the working directory as defined in config.py
        print(f"Storing evaluation results (by {centrality_measure}) in files...")
        precision_at_k_file_path = os.path.join(WORKING_DIRECTORY+'/evaluation_results', f"precision_at_k_{centrality_measure}based.txt")
        recall_at_k_file_path = os.path.join(WORKING_DIRECTORY+'/evaluation_results', f"recall_at_k_{centrality_measure}based.txt")
        avg_precision_at_k_file_path = os.path.join(WORKING_DIRECTORY+'/evaluation_results', f"avg_precision_at_k_{centrality_measure}based.txt")
        with open(precision_at_k_file_path, "w") as f:
            f.write("Precision at k:\n")
            for i in range(1, TOP_K+1):
                f.write(f"P@{i}: {precisions[i-1]}\n")
        with open(recall_at_k_file_path, "w") as f:
            f.write("Recall at k:\n")
            for i in range(1, TOP_K+1):
                f.write(f"R@{i}: {recalls[i-1]}\n")
        with open(avg_precision_at_k_file_path, "w") as f:
            f.write("Average precision at k:\n")
            for i in range(1, TOP_K+1):
                f.write(f"avg P@{i}: {avg_precisions[i-1]}\n")
        # plot the results
        plt.clf()
        plt.plot(range(1, TOP_K+1), precisions, label='Precision at k')
        plt.plot(range(1, TOP_K+1), recalls, label='Recall at k')
        plt.plot(range(1, TOP_K+1), avg_precisions, label='Average precision at k')
        plt.xlabel('k')
        plt.title(f'Evaluation results with strategy: {strategy}')
        
        plt.legend()
        plt.savefig(os.path.join(WORKING_DIRECTORY+'/plots', f'evaluation_by{centrality_measure}.png'))
        plt.close()

        print("-----------------------------------")

    # store graphs in files in the working directory as defined in config.py
    print("Storing graphs in gml files...")
    nx.write_gml(g0, os.path.join(WORKING_DIRECTORY+'/graphs', 'g0.gml'))
    nx.write_gml(g1, os.path.join(WORKING_DIRECTORY+'/graphs', 'g1.gml'))

    # store nodes ranks and other attributes in files in the working directory as defined in config.py as csv files
    print("Storing nodes ranks and other attributes in csv files...")
    for graph_name in ['g0', 'g1']:
        cr.store_nodes_ranks(globals()[graph_name], graph_name, CENTRALITY_MEASURES)

    # store graphs' basic metrics in a file under WORKING_DIRECTORY+'/graphs'
    print("Storing graphs' basic metrics in a file...")
    with open(os.path.join(WORKING_DIRECTORY+'/graphs', 'graphs_metrics.txt'), 'w') as f:
        f.write(f"Graph 0: Number of nodes: {g0.number_of_nodes()}, Number of links: {g0.number_of_edges()}\n")
        f.write(f"Graph 1: Number of nodes: {g1.number_of_nodes()}, Number of links: {g1.number_of_edges()}\n")
        # summary statics (min, max, avg, std, etc.) information on degree, in_degree, out_degree, and link's weights
        degrees_g0, indegrees_g0, outdegrees_g0 = [d for n, d in g0.degree()], [d for n, d in g0.in_degree()], [d for n, d in g0.out_degree()]
        degrees_g1, indegrees_g1, outdegrees_g1 = [d for n, d in g1.degree()], [d for n, d in g1.in_degree()], [d for n, d in g1.out_degree()]
        weights_g0 = [d['weight'] for u, v, d in g0.edges(data=True)]
        weights_g1 = [d['weight'] for u, v, d in g1.edges(data=True)]
        strengths_g0, in_strengths_g0, out_strengths_g0 = [d for n, d in g0.degree(weight='weight')], [d for n, d in g0.in_degree(weight='weight')], [d for n, d in g0.out_degree(weight='weight')]
        strengths_g1, in_strengths_g1, out_strengths_g1 = [d for n, d in g1.degree(weight='weight')], [d for n, d in g1.in_degree(weight='weight')], [d for n, d in g1.out_degree(weight='weight')]
        f.write(f"Graph 0: Min, Max, Avg, Std of degree: {min(degrees_g0)}, {max(degrees_g0)}, {sum(degrees_g0)/len(degrees_g0)}, {np.std(degrees_g0)}\n")
        f.write(f"Graph 1: Min, Max, Avg, Std of degree: {min(degrees_g1)}, {max(degrees_g1)}, {sum(degrees_g1)/len(degrees_g1)}, {np.std(degrees_g1)}\n")
        f.write(f"Graph 0: Min, Max, Avg, Std of in_degree: {min(indegrees_g0)}, {max(indegrees_g0)}, {sum(indegrees_g0)/len(indegrees_g0)}, {np.std(indegrees_g0)}\n")
        f.write(f"Graph 1: Min, Max, Avg, Std of in_degree: {min(indegrees_g1)}, {max(indegrees_g1)}, {sum(indegrees_g1)/len(indegrees_g1)}, {np.std(indegrees_g1)}\n")
        f.write(f"Graph 0: Min, Max, Avg, Std of out_degree: {min(outdegrees_g0)}, {max(outdegrees_g0)}, {sum(outdegrees_g0)/len(outdegrees_g0)}, {np.std(outdegrees_g0)}\n")
        f.write(f"Graph 1: Min, Max, Avg, Std of out_degree: {min(outdegrees_g1)}, {max(outdegrees_g1)}, {sum(outdegrees_g1)/len(outdegrees_g1)}, {np.std(outdegrees_g1)}\n")
        f.write(f"Graph 0: Min, Max, Avg, Std of strength: {min(strengths_g0)}, {max(strengths_g0)}, {sum(strengths_g0)/len(strengths_g0)}, {np.std(strengths_g0)}\n")
        f.write(f"Graph 1: Min, Max, Avg, Std of strength: {min(strengths_g1)}, {max(strengths_g1)}, {sum(strengths_g1)/len(strengths_g1)}, {np.std(strengths_g1)}\n")
        f.write(f"Graph 0: Min, Max, Avg, Std of in_strength: {min(in_strengths_g0)}, {max(in_strengths_g0)}, {sum(in_strengths_g0)/len(in_strengths_g0)}, {np.std(in_strengths_g0)}\n")
        f.write(f"Graph 1: Min, Max, Avg, Std of in_strength: {min(in_strengths_g1)}, {max(in_strengths_g1)}, {sum(in_strengths_g1)/len(in_strengths_g1)}, {np.std(in_strengths_g1)}\n")
        f.write(f"Graph 0: Min, Max, Avg, Std of out_strength: {min(out_strengths_g0)}, {max(out_strengths_g0)}, {sum(out_strengths_g0)/len(out_strengths_g0)}, {np.std(out_strengths_g0)}\n")
        f.write(f"Graph 1: Min, Max, Avg, Std of out_strength: {min(out_strengths_g1)}, {max(out_strengths_g1)}, {sum(out_strengths_g1)/len(out_strengths_g1)}, {np.std(out_strengths_g1)}\n")
        f.write(f"Graph 1: Min, Max, Avg, Std of edges' weights: {min([d['weight'] for u, v, d in g1.edges(data=True)]), max([d['weight'] for u, v, d in g1.edges(data=True)]), np.mean([d['weight'] for u, v, d in g1.edges(data=True)]), np.std([d['weight'] for u, v, d in g1.edges(data=True)])}\n")
    
        # clustering coefficient, average shortest path length, diameter, and density
        f.write(f"Graph 0: Average clustering: {nx.average_clustering(g0)}\n")
        f.write(f"Graph 1: Average clustering: {nx.average_clustering(g1)}\n")
        f.write(f"Graph 0: Average shortest path length: {nx.average_shortest_path_length(g0)}\n")
        f.write(f"Graph 1: Average shortest path length: {nx.average_shortest_path_length(g1)}\n")
        f.write(f"Graph 0: Diameter: {nx.diameter(g0)}\n")
        f.write(f"Graph 1: Diameter: {nx.diameter(g1)}\n")
        f.write(f"Graph 0: Density: {nx.density(g0)}\n")
        f.write(f"Graph 1: Density: {nx.density(g1)}\n")

    # store degree, indegree, outdegree, strength, in_strength, out_strength, and weight distributions in a file under WORKING_DIRECTORY+'/plots'
    print("Storing degree, indegree, outdegree, strength, in_strength, out_strength, and weight distributions in a file...")
    for g_str in ['g0', 'g1']:
        g = globals()[g_str]
        degrees = [d for n, d in g.degree()]
        indegrees = [d for n, d in g.in_degree()]
        outdegrees = [d for n, d in g.out_degree()]
        strengths = [s for n, s in g.degree(weight='weight')]
        in_strengths = [s for n, s in g.in_degree(weight='weight')]
        out_strengths = [s for n, s in g.out_degree(weight='weight')]
        weights = [d['weight'] for u, v, d in g.edges(data=True)]
        
        fig, axs = plt.subplots(3, 3, figsize=(18, 18))
        
        axs[0, 0].hist(degrees, bins=50, alpha=0.5, label='Degree')
        axs[0, 0].set_title('Degree Distribution')
        axs[0, 0].legend(loc='upper right')
        
        axs[0, 1].hist(indegrees, bins=50, alpha=0.5, label='In-degree')
        axs[0, 1].set_title('In-degree Distribution')
        axs[0, 1].legend(loc='upper right')
        
        axs[0, 2].hist(outdegrees, bins=50, alpha=0.5, label='Out-degree')
        axs[0, 2].set_title('Out-degree Distribution')
        axs[0, 2].legend(loc='upper right')
        
        axs[1, 0].hist(strengths, bins=50, alpha=0.5, label='Strength')
        axs[1, 0].set_title('Strength Distribution')
        axs[1, 0].legend(loc='upper right')
        
        axs[1, 1].hist(in_strengths, bins=50, alpha=0.5, label='In-strength')
        axs[1, 1].set_title('In-strength Distribution')
        axs[1, 1].legend(loc='upper right')
        
        axs[1, 2].hist(out_strengths, bins=50, alpha=0.5, label='Out-strength')
        axs[1, 2].set_title('Out-strength Distribution')
        axs[1, 2].legend(loc='upper right')
        
        axs[2, 0].hist(weights, bins=50, alpha=0.5, label='Edge Weights')
        axs[2, 0].set_title('Edge Weight Distribution')
        axs[2, 0].legend(loc='upper right')
        
        plt.tight_layout()
        plt.savefig(WORKING_DIRECTORY+f'/plots/distributions_{g_str}.png')
        plt.close()
    print("Graphs' degree/strength distributions saved.") 
    
    print("Done.")

    


