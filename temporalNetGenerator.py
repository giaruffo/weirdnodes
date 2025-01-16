import networkx as nx
import random
import matplotlib.pyplot as plt
from scipy.stats import spearmanr, kendalltau
from numpy.random import power
import pandas as pd
from config import *
import csv


def perturb_network_by_nodes(g0, n):
    # Create a copy of g0 to perturb
    g1 = g0.copy()

    # Select n random nodes to perturb
    nodes_to_perturb = random.sample(list(g1.nodes), n)

    # Initialize nodes'types as 'normal'
    for node in g1.nodes:
        g1.nodes[node]['type'] = 'normal'

    for node in nodes_to_perturb:
        if random.random() < 0.5:
            # Rewire outgoing links
            out_edges = list(g1.out_edges(node, data=True))
            num_out_edges_to_perturb = int(len(out_edges) * random.uniform(0, 1))
            out_edges_to_perturb = random.sample(out_edges, num_out_edges_to_perturb)
            for edge in out_edges_to_perturb:
                g1.remove_edge(*edge[:2])
                new_source = random.choice(list(g1.nodes))
                while new_source == node:
                    new_source = random.choice(list(g1.nodes))
                g1.add_edge(new_source, edge[1], weight=edge[2]['weight'])
            g1.nodes[node]['type'] = 'black_hole'
        else:
            # Rewire incoming links
            in_edges = list(g1.in_edges(node, data=True))
            num_in_edges_to_perturb = int(len(in_edges) * random.uniform(0, 1))
            in_edges_to_perturb = random.sample(in_edges, num_in_edges_to_perturb)
            for edge in in_edges_to_perturb:
                g1.remove_edge(*edge[:2])
                new_target = random.choice(list(g1.nodes))
                while new_target == node:
                    new_target = random.choice(list(g1.nodes))
                g1.add_edge(edge[0], new_target, weight=edge[2]['weight'])
            g1.nodes[node]['type'] = 'vulcano'

    return g1
    
def rank_nodes_by_centrality(g, centrality_measure):
    if centrality_measure == 'degree':
        centrality = nx.degree_centrality(g)
    elif centrality_measure == 'strength':
        centrality = dict(g.degree(weight='weight'))
    elif centrality_measure == 'betweenness':
        centrality = nx.betweenness_centrality(g)
    elif centrality_measure == 'closeness':
        centrality = nx.closeness_centrality(g)
    elif centrality_measure == 'eigenvector':
        centrality = nx.eigenvector_centrality(g)
    elif centrality_measure == 'pagerank':
        centrality = nx.pagerank(g)
    elif centrality_measure == 'hits_hubs':
        centrality = nx.hits(g)[0]
    elif centrality_measure == 'hits_authorities':
        centrality = nx.hits(g)[1]
    elif centrality_measure == 'indegree':
        centrality = dict(g.in_degree())
    elif centrality_measure == 'outdegree':
        centrality = dict(g.out_degree())
    elif centrality_measure == 'instrength':
        centrality = dict(g.in_degree(weight='weight'))
    elif centrality_measure == 'outstrength':
        centrality = dict(g.out_degree(weight='weight'))
    else:
        raise ValueError(f"Unsupported centrality measure: {centrality_measure}")

    # for each node, store the calculated centrality value as a node attribute
    for node in g.nodes:
        g.nodes[node][centrality_measure] = centrality[node]

    # Convert centrality dictionary to a pandas Series
    centrality_series = pd.Series(centrality)

    # Rank nodes by centrality using pandas rank function
    ranked_nodes = centrality_series.rank(ascending=False, method='min').sort_values().index.tolist()
    return ranked_nodes

def plot_ranked_nodes_comparison(g, ranks1, ranks2, title):
    plt.clf()
    x = []
    y = []
    colors = []
    sizes = []
    texts = []

    for node in g.nodes:
        x.append(ranks1.index(node) + 1)
        y.append(ranks2.index(node) + 1)
        node_type = g.nodes[node].get('type', 'normal')
        if node_type == 'vulcano':
            colors.append('red')
            texts.append((ranks1.index(node) + 1, ranks2.index(node) + 1, str(node)))
        elif node_type == 'black_hole':
            colors.append('black')
            texts.append((ranks1.index(node) + 1, ranks2.index(node) + 1, str(node)))
        else:
            colors.append('cyan')
        residual = abs((ranks1.index(node) + 1) - (ranks2.index(node) + 1))
        sizes.append(residual * 5)  # Adjust the multiplier for better visualization

    # Plot 'normal' nodes first
    for i in range(len(x)):
        if colors[i] == 'cyan':
            plt.scatter(x[i], y[i], c=colors[i], s=sizes[i], alpha=0.5)

    # Plot 'black_hole' and 'vulcano' nodes on top
    for i in range(len(x)):
        if colors[i] != 'cyan':
            plt.scatter(x[i], y[i], c=colors[i], s=sizes[i], alpha=0.5)

    # Add text labels for 'black_hole' and 'vulcano' nodes
    for text in texts:
        plt.text(text[0], text[1], text[2], fontsize=9, ha='right')

    plt.plot([min(x), max(x)], [min(y), max(y)], 'k--', lw=1)  # Bisect line
    plt.xlabel('Rank in first list')
    plt.ylabel('Rank in second list')
    plt.title(title)
    plt.savefig(os.path.join(working_directory, title + '.png'))
    # plt.show()


def plot_graph(g, title):
    pos = nx.spring_layout(g)
    weights = nx.get_edge_attributes(g, 'weight').values()
    nx.draw(g, pos, with_labels=True, node_size=500, node_color="skyblue", edge_color="gray", width=[weight / max(weights) for weight in weights])
    plt.title(title)
    plt.show()

def calculate_precision_at_k(g,top_nodes, k):
    relevant_nodes = [node for node, _ in top_nodes[:k] if g.nodes[node]['type'] != 'normal']
    return len(relevant_nodes) / k

# Test the function
if __name__ == "__main__":

    # Generate a random directed and weighted graph with NODES nodes
    g0 = nx.gnm_random_graph(n=num_nodes, m=num_links, directed=True)

    for u, v, d in g0.edges(data=True):
        d['weight'] = random.gauss(5.0, 2.0)  # Example: Gaussian distribution with mean=5.0 and std=2.0
       
    # Define perturbation parameters
    n = num_nodes_to_perturb  # Number of nodes to perturb

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
    for measure in centrality_measures:
        ranked_nodes[measure] = {}
        ranked_nodes[measure]['g0'] = rank_nodes_by_centrality(g0, measure)
        ranked_nodes[measure]['g1'] = rank_nodes_by_centrality(g1, measure)
        ranked_nodes[measure]['g2'] = rank_nodes_by_centrality(g2, measure)
        ranked_nodes[measure]['g3'] = rank_nodes_by_centrality(g3, measure)

    # store graphs in files in the working directory as defined in config.py
    nx.write_gml(g0, os.path.join(working_directory, 'g0.gml'))
    nx.write_gml(g1, os.path.join(working_directory, 'g1.gml'))
    nx.write_gml(g2, os.path.join(working_directory, 'g2.gml'))
    nx.write_gml(g3, os.path.join(working_directory, 'g3.gml'))

    # store nodes ranks in files in the working directory as defined in config.py as csv files
    # Create a DataFrame to store the centrality measures and their ranks for each node
    for graph_name in ['g0', 'g1', 'g2', 'g3']:
        df = pd.DataFrame(index=g0.nodes)
        df['type'] = [globals()[graph_name].nodes[node].get('type', 'normal') for node in globals()[graph_name].nodes]
        for measure in centrality_measures:
            df[measure] = [globals()[graph_name].nodes[node][measure] for node in globals()[graph_name].nodes]
            df[f'{measure}_rank'] = [ranked_nodes[measure][graph_name].index(node) + 1 for node in globals()[graph_name].nodes]
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'node_id'}, inplace=True)
        df.to_csv(os.path.join(working_directory, f'{graph_name}_centrality_measures.csv'), index=False)

    correlations = {}
    ranked_nodes_id = {}
    for measure in centrality_measures:
        correlations[measure] = {}
        correlations[measure]['g0_g1'] = {}
        correlations[measure]['g1_g2'] = {}
        correlations[measure]['g2_g3'] = {}

        correlations[measure]['g0_g1']['spearman'], _ = spearmanr(ranked_nodes[measure]['g0'], ranked_nodes[measure]['g1'])
        correlations[measure]['g0_g1']['kendall'], _ = kendalltau(ranked_nodes[measure]['g0'], ranked_nodes[measure]['g1'])
        correlations[measure]['g1_g2']['spearman'], _ = spearmanr(ranked_nodes[measure]['g1'], ranked_nodes[measure]['g2'])
        correlations[measure]['g1_g2']['kendall'], _ = kendalltau(ranked_nodes[measure]['g1'], ranked_nodes[measure]['g2'])
        correlations[measure]['g2_g3']['spearman'], _ = spearmanr(ranked_nodes[measure]['g2'], ranked_nodes[measure]['g3'])
        correlations[measure]['g2_g3']['kendall'], _ = kendalltau(ranked_nodes[measure]['g2'], ranked_nodes[measure]['g3'])

        print(f"Correlation coefficients for **{measure}** centrality measure:")
        print(f"Spearman correlation between g0 and g1: {correlations[measure]['g0_g1']['spearman']:.4f}")
        print(f"Kendall correlation between g0 and g1: {correlations[measure]['g0_g1']['kendall']:.4f}")
        print(f"Spearman correlation between g1 and g2: {correlations[measure]['g1_g2']['spearman']:.4f}")
        print(f"Kendall correlation between g1 and g2: {correlations[measure]['g1_g2']['kendall']:.4f}")
        print(f"Spearman correlation between g2 and g3: {correlations[measure]['g2_g3']['spearman']:.4f}")
        print(f"Kendall correlation between g2 and g3: {correlations[measure]['g2_g3']['kendall']:.4f}")
        print()
   
    # print confusion matrices from the correlation coefficients for all the centrality measures:
    print("Confusion matrix from the Spearman correlation coefficients for all the centrality measures:")
    print("Measure\tg0_g1\tg1_g2\tg2_g3")
    for measure in correlations:
        print(f"**{measure}**\t{correlations[measure]['g0_g1']['spearman']:.4f}\t{correlations[measure]['g1_g2']['spearman']:.4f}\t{correlations[measure]['g2_g3']['spearman']:.4f}")
    print() 
    print("Confusion matrix from the Kendall's tau coefficients for all the centrality measures:")
    print("Measure\tg0_g1\tg1_g2\tg2_g3")
    for measure in correlations:
        print(f"**{measure}**\t{correlations[measure]['g0_g1']['kendall']:.4f}\t{correlations[measure]['g1_g2']['kendall']:.4f}\t{correlations[measure]['g2_g3']['kendall']:.4f}")
    print()

    # store in two different csv files in the working directory the confusion matrices 
    # one for Spearman and one for Kendall's tau coefficients   
    with open(os.path.join(working_directory, 'spearman_correlations.csv'), 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['Measure', 'g0_g1', 'g1_g2', 'g2_g3'])
        for measure in correlations:
            writer.writerow([measure, correlations[measure]['g0_g1']['spearman'], correlations[measure]['g1_g2']['spearman'], correlations[measure]['g2_g3']['spearman']])
    with open(os.path.join(working_directory, 'kendall_correlations.csv'), 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['Measure', 'g0_g1', 'g1_g2', 'g2_g3'])
        for measure in correlations:
            writer.writerow([measure, correlations[measure]['g0_g1']['kendall'], correlations[measure]['g1_g2']['kendall'], correlations[measure]['g2_g3']['kendall']])
   
    top_nodes = {}
    # for each centrality measure, and for each graph from g1 to g3, print the list of nodes whose types is not normal
    for measure in centrality_measures:
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
            top_nodes[f'g{i-1}_g{i}'] = residuals[:10]
            print(f"Top 10 nodes with the highest residual between ranks in g{i-1} and g{i} for **{measure}**: {top_nodes[f'g{i-1}_g{i}']}")

            # for each pair of consecutive graphs, and for each centrality measure, calculate the precision@1, precision@2, precision@3, precision@4, precision@5, precision@6, precision@7, precision@8, precision@9, precision@10, considering the type of the nodes, and print the results
            for j in range(1, 11):
                precision = calculate_precision_at_k(globals()[f'g{i}'], top_nodes[f'g{i-1}_g{i}'], j)
                print(f"Precision@{j}: {precision}")
            print()
    
    # store in a csv file in the working directory the top nodes, using the pair of consecutive graphs as the columns and 
    # the centrality measures as the rows; also add the information for each node of their type, and their residual value

    for measure in centrality_measures:
        with open(os.path.join(working_directory, f'{measure}_top_nodes.csv'), 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['Pair of consecutive graphs', 'Node', 'Type', 'Residual value'])
            for pair in top_nodes:
                for node, residual in top_nodes[pair]:
                    writer.writerow([pair, node, globals()[pair.split('_')[1]].nodes[node]['type'], residual])
        f.close()
        # store in a csv file in the working directory the precision@k values, using the pair of consecutive graphs as the columns and  the k values as the rows    
        with open(os.path.join(working_directory, f'{measure}_precision_at_k.csv'), 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['Pair of consecutive graphs', 'Precision@1', 'Precision@2', 'Precision@3', 'Precision@4', 'Precision@5', 'Precision@6', 'Precision@7', 'Precision@8', 'Precision@9', 'Precision@10'])
            for pair in top_nodes:
                precisions = [calculate_precision_at_k(globals()[pair.split('_')[1]], top_nodes[pair], k) for k in range(1, 11)]
                writer.writerow([pair] + precisions)
            print(f'Finished writing {measure}_precision_at_k.csv')
        f.close()

