import networkx as nx
import random
import pandas as pd
from config import *
from scipy.stats import spearmanr, kendalltau
import csv
from net_perturbation import perturb_network_by_nodes, perturb_network_by_links
from create_rankings import  plot_ranked_nodes_comparison, rank_nodes_by_centrality
from concordance_check import concordance_check
from evaluation import precision_at_k, recall_at_k, avg_precision_at_k, mean_average_precision_at_k

# Test the library
if __name__ == "__main__":

    # Generate a random directed and weighted graph with Erdos-Renyi model
    g0 = nx.gnm_random_graph(n=NUM_NODES, m=NUM_LINKS, directed=True)

    for u, v, d in g0.edges(data=True):
        d['weight'] = random.gauss(5.0, 2.0)  # Example: Gaussian distribution with mean=5.0 and std=2.0
       
    # Define perturbation parameters
    n = NUM_NODES_TO_PERTURB  # Number of nodes to perturb

    # Create the perturbation by nodes three times
    g1 = perturb_network_by_nodes(g0, n)
    print("First node-based perturbation done.")
    g2 = perturb_network_by_nodes(g1, n)
    print("Second node-based perturbation done.")
    g3 = perturb_network_by_nodes(g2, n)
    print("Third node-based perturbation done.")
    print("All perturbations done.")
    
    # rank nodes, for each centrality measures, for g0, g1 and g2
   
    ranked_nodes = {}
    for measure in CENTRALITY_MEASURES:
        ranked_nodes[measure] = {}
        ranked_nodes[measure]['g0'] = rank_nodes_by_centrality(g0, measure)
        ranked_nodes[measure]['g1'] = rank_nodes_by_centrality(g1, measure)
        ranked_nodes[measure]['g2'] = rank_nodes_by_centrality(g2, measure)
        ranked_nodes[measure]['g3'] = rank_nodes_by_centrality(g3, measure)

    # store graphs in files in the working directory as defined in config.py
    nx.write_gml(g0, os.path.join(WORKING_DIRECTORY, 'g0.gml'))
    nx.write_gml(g1, os.path.join(WORKING_DIRECTORY, 'g1.gml'))
    nx.write_gml(g2, os.path.join(WORKING_DIRECTORY, 'g2.gml'))
    nx.write_gml(g3, os.path.join(WORKING_DIRECTORY, 'g3.gml'))

    # store nodes ranks in files in the working directory as defined in config.py as csv files
    # Create a DataFrame to store the centrality measures and their ranks for each node
    for graph_name in ['g0', 'g1', 'g2', 'g3']:
        df = pd.DataFrame(index=g0.nodes)
        df['type'] = [globals()[graph_name].nodes[node].get('type', 'normal') for node in globals()[graph_name].nodes]
        for measure in CENTRALITY_MEASURES:
            df[measure] = [globals()[graph_name].nodes[node][measure] for node in globals()[graph_name].nodes]
            df[f'{measure}_rank'] = [ranked_nodes[measure][graph_name].index(node) + 1 for node in globals()[graph_name].nodes]
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'node_id'}, inplace=True)
        df.to_csv(os.path.join(WORKING_DIRECTORY, f'{graph_name}_centrality_measures.csv'), index=False)

    correlations = {}
    for measure in CENTRALITY_MEASURES:
        correlations[measure] = {}
        correlations[measure]['g0_g1'] = {}
        correlations[measure]['g1_g2'] = {}
        correlations[measure]['g2_g3'] = {}

        correlations[measure]['g0_g1']['kendallSignal'], correlations[measure]['g0_g1']['kendall'] = concordance_check(ranked_nodes[measure]['g0'], ranked_nodes[measure]['g1'])
        correlations[measure]['g1_g2']['kendallSignal'], correlations[measure]['g1_g2']['kendall'] = concordance_check(ranked_nodes[measure]['g1'], ranked_nodes[measure]['g2'])
        correlations[measure]['g2_g3']['kendallSignal'], correlations[measure]['g2_g3']['kendall'] = concordance_check(ranked_nodes[measure]['g2'], ranked_nodes[measure]['g3'])

        correlations[measure]['g0_g1']['spearmanSignal'], correlations[measure]['g0_g1']['spearman'] = concordance_check(ranked_nodes[measure]['g0'], ranked_nodes[measure]['g1'], spearmanr)
        correlations[measure]['g1_g2']['spearmanSignal'], correlations[measure]['g1_g2']['spearman'] = concordance_check(ranked_nodes[measure]['g1'], ranked_nodes[measure]['g2'], spearmanr)
        correlations[measure]['g2_g3']['spearmanSignal'], correlations[measure]['g2_g3']['spearman'] = concordance_check(ranked_nodes[measure]['g2'], ranked_nodes[measure]['g3'], spearmanr)

        print(f"Correlation coefficients for **{measure}** centrality measure:")
        print(f"Spearman correlation between g0 and g1: {correlations[measure]['g0_g1']['spearman']:.4f}, Signal: {correlations[measure]['g0_g1']['spearmanSignal']}")
        print(f"Kendall correlation between g0 and g1: {correlations[measure]['g0_g1']['kendall']:.4f}, Signal: {correlations[measure]['g0_g1']['kendallSignal']}")
        print(f"Spearman correlation between g1 and g2: {correlations[measure]['g1_g2']['spearman']:.4f}, Signal: {correlations[measure]['g1_g2']['spearmanSignal']}")
        print(f"Kendall correlation between g1 and g2: {correlations[measure]['g1_g2']['kendall']:.4f}, Signal: {correlations[measure]['g1_g2']['kendallSignal']}")
        print(f"Spearman correlation between g2 and g3: {correlations[measure]['g2_g3']['spearman']:.4f}, Signal: {correlations[measure]['g2_g3']['spearmanSignal']}")
        print(f"Kendall correlation between g2 and g3: {correlations[measure]['g2_g3']['kendall']:.4f}, Signal: {correlations[measure]['g2_g3']['kendallSignal']}")
        print()

    # store in two different csv files in the working directory the confusion matrices 
    # one for Spearman and one for Kendall's tau coefficients  
    with open(os.path.join(WORKING_DIRECTORY, 'spearman_correlations.csv'), 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['Measure', 'g0_g1', 'signal g0_g1', 'g1_g2', 'signal g1_g2', 'g2_g3', 'signal g2_g3',])
        for measure in CENTRALITY_MEASURES:
            writer.writerow([measure, 
                            correlations[measure]['g0_g1']['spearman'], 
                            correlations[measure]['g0_g1']['spearmanSignal'], 
                            correlations[measure]['g1_g2']['spearman'], 
                            correlations[measure]['g1_g2']['spearmanSignal'], 
                            correlations[measure]['g2_g3']['spearman'],
                            correlations[measure]['g1_g2']['spearmanSignal'], ])
        f.close()
    with open(os.path.join(WORKING_DIRECTORY, 'kendall_correlations.csv'), 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['Measure', 'g0_g1', 'g1_g2', 'g2_g3'])
        for measure in CENTRALITY_MEASURES:
            writer.writerow([measure, 
                            correlations[measure]['g0_g1']['kendall'], 
                            correlations[measure]['g0_g1']['kendallSignal'], 
                            correlations[measure]['g1_g2']['kendall'], 
                            correlations[measure]['g1_g2']['kendallSignal'], 
                            correlations[measure]['g2_g3']['kendall'],
                            correlations[measure]['g2_g3']['kendallSignal'],])
        f.close()

    top_nodes = {}
    for measure in CENTRALITY_MEASURES:
        # for each centrality measure, and for each graph from g1 to g3, print the list of nodes whose types is not normal
        print(f"Nodes whose type is not normal for **{measure}**:")
        for graph in ['g1', 'g2', 'g3']:
            print(f"{graph}:")
            for node in globals()[graph].nodes:
                if globals()[graph].nodes[node]['type'] != 'normal':
                    prev_graph = 'g0' if graph == 'g1' else 'g1' if graph == 'g2' else 'g2'
                    prev_rank = ranked_nodes[measure][prev_graph].index(node) + 1
                    curr_rank = ranked_nodes[measure][graph].index(node) + 1
                    print(f"Node {node} is of type {globals()[graph].nodes[node]['type']}, rank in {prev_graph}: {prev_rank}, rank in {graph}: {curr_rank}")

        # plot the comparison between the ranked nodes for each pair of consecutive graphs and
        # for each pair of consecutive graphs, and for each centrality measure, create a list with the top n nodes with the highest residual between ranks 
        for i in range(1, 4):
            plot_ranked_nodes_comparison(globals()[f'g{i}'], ranked_nodes[measure][f'g{i-1}'], ranked_nodes[measure][f'g{i}'], f"{measure} (g{i})")    
            
            g0_ranks = ranked_nodes[measure][f'g{i-1}']
            g1_ranks = ranked_nodes[measure][f'g{i}']
            residuals = []
            for node in g0_ranks:
                if node in g1_ranks:
                    residual = abs(g0_ranks.index(node) - g1_ranks.index(node))
                residuals.append((node, residual))
            residuals.sort(key=lambda x: x[1], reverse=True)
            top_nodes[f'g{i-1}_g{i}'] = residuals[:30]
            print(f"Top 30 nodes with the highest residual between ranks in g{i-1} and g{i} for **{measure}**: {top_nodes[f'g{i-1}_g{i}']}")

            # for each pair of consecutive graphs, and for each centrality measure, calculate the 
            # precision@1, precision@2, precision@5, precision@10, precision@20, precision@30 
            # considering the type of the nodes, and print the results
            for j in (1, 2, 5, 10, 20, 30):
                precision = precision_at_k(globals()[f'g{i}'], top_nodes[f'g{i-1}_g{i}'], j)
                recall = recall_at_k(globals()[f'g{i}'], top_nodes[f'g{i-1}_g{i}'], j)
                print(f"Precision@{j}: {precision}")
            print()

            # for each pair of consecutive graphs, and for each centrality measure, calculate the 
            # recall@10, recall@20, recall@30 
            # considering the type of the nodes, and print the results
            for j in (10, 20, 30):
                recall = recall_at_k(globals()[f'g{i}'], top_nodes[f'g{i-1}_g{i}'], j)
                print(f"Recall@{j}: {precision}")
            print()
    
    # store in a csv file in the working directory the top nodes, using the pair of consecutive graphs as the columns and 
    # the centrality measures as the rows; also add the information for each node of their type, and their residual value

    for measure in CENTRALITY_MEASURES:
        with open(os.path.join(WORKING_DIRECTORY, f'{measure}_top_nodes.csv'), 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['Pair of consecutive graphs', 'Node', 'Type', 'Residual value'])
            for pair in top_nodes:
                for node, residual in top_nodes[pair]:
                    writer.writerow([pair, node, globals()[pair.split('_')[1]].nodes[node]['type'], residual])
        f.close()
        # store in a csv file in the working directory the precision@k values, using the pair of consecutive graphs as the columns and  the k values as the rows    
        with open(os.path.join(WORKING_DIRECTORY, f'{measure}_evaluation.csv'), 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['Pair of consecutive graphs', 
                             'P@1', 'P@2', 'P@5', 'P@10', 'P@20', 'P@30', 
                             'avg P@10', 'avg P@20', 'avg P@30',
                             'R@10', 'R@20', 'R@30', 
                             ])
            for pair in top_nodes:
                precisions = [precision_at_k(globals()[pair.split('_')[1]], top_nodes[pair], k) for k in (1, 2, 5, 10, 20, 30)]
                avg_precisions = [avg_precision_at_k(globals()[pair.split('_')[1]], top_nodes[pair], k) for k in (10, 20, 30)]
                recalls = [recall_at_k(globals()[pair.split('_')[1]], top_nodes[pair], k) for k in (10, 20, 30)]
                writer.writerow([pair] + precisions+avg_precisions+recalls)
            print(f'Finished writing {measure}_precision_at_k.csv')
        f.close()
