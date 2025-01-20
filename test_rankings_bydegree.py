# create test cases for the functions in createRankings.py

import create_rankings as cr
import concordance_check as cc
import net_perturbation as nper
import evaluation as ev
import matplotlib.pyplot as plt
import os
import networkx as nx
import random
import networkx as nx
from scipy.stats import spearmanr
from config import *


if __name__ == "__main__":
    # Generate a random directed and weighted graph with Erdos-Renyi model
    g0 = nx.gnm_random_graph(n=NUM_NODES, m=NUM_LINKS, directed=True)

    for u, v, d in g0.edges(data=True):
        d['weight'] = random.gauss(5.0, 2.0)  # Example: Gaussian distribution with mean=5.0 and std=2.0
       
    # Create the perturbation by nodes 
    print("Perturbing the network by nodes...")
    g1 = nper.perturb_network_by_nodes(g0, NUM_NODES_TO_PERTURB)
    
    print("-----------------------------------")

    # set the centrality measures to be calculated
    centrality_measure = 'degree'

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
        for i in range(1, 31):
            f.write(f"P@{i}: {precisions[i-1]}\n")
    with open(recall_at_k_file_path, "w") as f:
        f.write("Recall at k:\n")
        for i in range(1, 31):
            f.write(f"R@{i}: {recalls[i-1]}\n")
    with open(avg_precision_at_k_file_path, "w") as f:
        f.write("Average precision at k:\n")
        for i in range(1, 31):
            f.write(f"avg P@{i}: {avg_precisions[i-1]}\n")
    # plot the results
    plt.clf()
    plt.plot(range(1, TOP_K+1), precisions, label='Precision at k')
    plt.plot(range(1, TOP_K+1), recalls, label='Recall at k')
    plt.plot(range(1, TOP_K+1), avg_precisions, label='Average precision at k')
    plt.xlabel('k')
    
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

    


