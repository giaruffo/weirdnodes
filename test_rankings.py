# create test cases for the functions in createRankings.py

import create_rankings as cr
import concordance_check as cc
import net_perturbation as nper
import evaluation as ev
import matplotlib.pyplot as plt
import os
import networkx as nx
import numpy as np
import random
import pandas as pd
import networkx as nx
import numpy as np
from scipy.stats import spearmanr
from config import *


if __name__ == "__main__":
    # Generate a random directed and weighted graph with Erdos-Renyi model
    g0 = nx.gnm_random_graph(n=NUM_NODES, m=NUM_LINKS, directed=True)

    for u, v, d in g0.edges(data=True):
        d['weight'] = random.gauss(5.0, 2.0)  # Example: Gaussian distribution with mean=5.0 and std=2.0
       
    # Define perturbation parameters
    n = NUM_NODES_TO_PERTURB  # Number of nodes to perturb

    # Create the perturbation by nodes three times
    g1 = nper.perturb_network_by_nodes(g0, n)
    print("First node-based perturbation done.")

    # show the differences between the two graphs
    print("Graph 0 and Graph 1 differences:")
    print(nx.difference(g0, g1).edges(data=True))

    # Rank nodes by centrality using the degree measure
    # and store the results in a dictionary
    ranks = {}
    ranks['g0'] = cr.rank_nodes_by_centrality(g0, 'degree')
    ranks['g1'] = cr.rank_nodes_by_centrality(g1, 'degree')

    # print degree sequences  
    print("Degree sequence of g0:")
    print([d for _, d in g0.degree()])
    print("Degree sequence of g1:")
    print([d for _, d in g1.degree()])

    # print ranked nodes
    print("Ranked nodes by degree:")
    print(ranks['g0'])
    print(ranks['g1'])

    # plot graphs with the same layout and save them to files
    nper.plot_graphs_comparison(g0, g1)

    # store graphs in files in the working directory as defined in config.py
    nx.write_gml(g0, os.path.join(WORKING_DIRECTORY, 'g0.gml'))
    nx.write_gml(g1, os.path.join(WORKING_DIRECTORY, 'g1.gml'))

    # store nodes ranks in files in the working directory as defined in config.py as csv files
    # Create a DataFrame to store the centrality measures and their ranks for each node
    for graph_name in ['g0', 'g1']:
        df = pd.DataFrame(index=g0.nodes)
        df['type'] = [globals()[graph_name].nodes[node].get('type', 'normal') for node in globals()[graph_name].nodes]
        df['degree'] = [globals()[graph_name].degree(node) for node in globals()[graph_name].nodes]
        df['indegree'] = [globals()[graph_name].in_degree(node) for node in globals()[graph_name].nodes]
        df['outdegree'] = [globals()[graph_name].out_degree(node) for node in globals()[graph_name].nodes]
        df['degree_centrality'] = [globals()[graph_name].nodes[node] for node in globals()[graph_name].nodes]
        df['degree_rank'] = ranks[graph_name]
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'node_id'}, inplace=True)
        df.to_csv(os.path.join(WORKING_DIRECTORY, f'{graph_name}_degree.csv'), index=False)

    # Calculate the concordance between the two rankings
    kendallSignal, kendall = cc.concordance_check(ranks['g0'], ranks['g1'])
    print(kendallSignal)
    print(kendall)

    spearmanSignal, spearman = cc.concordance_check(ranks['g0'], ranks['g1'], spearmanr)
    print(spearmanSignal)
    print(spearman)

    # store the concordance results in a file in the working directory as defined in config.py
    concordance_file_path = os.path.join(WORKING_DIRECTORY, "concordance.txt")
    with open(concordance_file_path, "w") as f:
        f.write(f"Kendall's tau: {kendall}\n")
        f.write(f"Spearman's rho: {spearman}\n")
        f.write(f"Kendall's tau signal: {kendallSignal}\n")
        f.write(f"Spearman's rho signal: {spearmanSignal}\n")

    # plot the ranked nodes comparison and get the top k nodes sorted by the 
    # absolute value of the residuals of the ranks
    top_k_nodes = cr.plot_ranked_nodes_comparison(g1, ranks['g0'], ranks['g1'], 'degree')

    # store the top k nodes in a file in the working directory as defined in config.py
    top_k_nodes_file_path = os.path.join(WORKING_DIRECTORY, "top_k_nodes.txt")
    with open(top_k_nodes_file_path, "w") as f:
        f.write("Top k nodes sorted by the absolute value of the residuals of the ranks:\n")
        for node in top_k_nodes:
            f.write(f"{node}\t")
            # write node type to file
            f.write(f"Type: {g1.nodes[node[0]]['type']}\n")
    
    # calculate precision, recall, average precision and mean average precision at k, for k = 1,..., 30
    # using function in evaluation.py
    precisions = []
    recalls = []   
    avg_precisions = []
    for i in range(1, 31):
        precision = ev.precision_at_k(g1, top_k_nodes[:i], i)
        recall = ev.recall_at_k(g1, top_k_nodes[:i], i)
        average_precision = ev.avg_precision_at_k(g1, top_k_nodes[:i], i)
        print(f"P@{i}: {precision}")
        print(f"R@{i}: {recall}")
        print(f"avg P@{i}: {average_precision}")
        precisions.append(precision)
        recalls.append(recall)
        avg_precisions.append(average_precision)

    # store the results in a file in the working directory as defined in config.py
    precision_at_k_file_path = os.path.join(WORKING_DIRECTORY, "precision_at_k.txt")
    recall_at_k_file_path = os.path.join(WORKING_DIRECTORY, "recall_at_k.txt")
    avg_precision_at_k_file_path = os.path.join(WORKING_DIRECTORY, "avg_precision_at_k.txt")
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
    plt.plot(range(1, 31), precisions, label='Precision at k')
    plt.plot(range(1, 31), recalls, label='Recall at k')
    plt.plot(range(1, 31), avg_precisions, label='Average precision at k')
    plt.xlabel('k')
    
    plt.legend()
    plt.savefig(os.path.join(WORKING_DIRECTORY, 'evaluation.png'))
    plt.close()


    


