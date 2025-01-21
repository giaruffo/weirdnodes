import matplotlib.pyplot as plt
import os
import networkx as nx
import pandas as pd
from config import WORKING_DIRECTORY, TOP_K  # Import working_directory and TOP_K from config.py

def rank_nodes_by_centrality(g, centrality_measure):
    """
    Rank nodes in a graph by a specified centrality measure.

    Parameters:
    g (networkx.Graph): The input graph.
    centrality_measure (str): The centrality measure to use for ranking. 
                              Supported measures are 'degree', 'strength', 
                              'betweenness', 'closeness', 'eigenvector', 
                              'pagerank', 'hits_hubs', 'hits_authorities', 
                              'indegree', 'outdegree', 'instrength', and 'outstrength'.

    Returns:
    list: A Series object containing the centrality values of the nodes, ranked in descending order.

    Raises:
    ValueError: If an unsupported centrality measure is provided.
    """
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
        centrality = dict(nx.in_degree_centrality(g))
    elif centrality_measure == 'outdegree':
        centrality = dict(nx.out_degree_centrality(g))
    elif centrality_measure == 'instrength':
        centrality = dict(g.in_degree(weight='weight'))
    elif centrality_measure == 'outstrength':
        centrality = dict(g.out_degree(weight='weight'))
    else:
        raise ValueError(f"Unsupported centrality measure: {centrality_measure}")

    # Convert centrality dictionary to a pandas Series
    centrality_series = pd.Series(centrality)

    # Rank nodes by centrality using pandas rank function
    # rank = centrality_series.rank(ascending=False, method='first').sort_values().index.tolist()
    rank = centrality_series.rank(ascending=False, method='min')

    # for each node, store the calculated centrality value as a node attribute
    for node in g.nodes:
        g.nodes[node][centrality_measure] = centrality[node]
        g.nodes[node][centrality_measure + '_rank'] = rank[node]

    return rank

# create a function to store in a csv file the nodes' lists, their types, their centrality measures, and for 
# each centrality measure, the ranks of the nodes in the graph.
# To be noted that each node in the graph has  
# - a type attribute, which can be either 'normal' or other types like indicating an anomaly created on purpose
# - a centrality measure attribute, which can be any of the supported centrality measures
# - a rank attribute, which is the rank of the node in the graph for the given centrality measure
def store_nodes_ranks(g, graph_name, centrality_measures):
    """
    Store the nodes' lists, their types, their centrality measures, and their ranks in a CSV file.
    Parameters:
    g (networkx.Graph): The graph containing the nodes to be ranked.
    graph_name (str): The name of the graph.
    centrality_measures (list): A list of centrality measures to be used for ranking.
    Returns:
    None
    """
    # create a pandas data frame to store the nodes' lists, their types, their centrality measures, and their ranks
    df = pd.DataFrame(index=g.nodes)
    df['type'] = [g.nodes[node].get('type', 'normal') for node in g.nodes]
    df['deg'] = [g.degree(node) for node in g.nodes]
    df['indeg'] = [g.in_degree(node) for node in g.nodes]
    df['outdeg'] = [g.out_degree(node) for node in g.nodes]
    df['stre'] = [g.degree(node, weight='weight') for node in g.nodes]
    df['instre'] = [g.in_degree(node, weight='weight') for node in g.nodes]
    df['outstre'] = [g.out_degree(node, weight='weight') for node in g.nodes]
    
    for centrality_measure in centrality_measures:
        # calculate the centrality measure for each node
        df[centrality_measure] = [g.nodes[node].get(centrality_measure) for node in g.nodes]
        df[centrality_measure + '_rank'] = [g.nodes[node].get(centrality_measure + '_rank') for node in g.nodes]  

    df.reset_index(inplace=True)
    df.rename(columns={'index': 'node_id'}, inplace=True)
    df.to_csv(os.path.join(WORKING_DIRECTORY+'/graphs', f'{graph_name}_attributes.csv'), index=False)


def plot_ranked_nodes_comparison(g, ranks1, ranks2, title):
    """
    Plots a comparison of ranked nodes from two ranking lists and highlights specific node types.
    Parameters:
    g (networkx.Graph): The graph containing the nodes to be plotted.
    ranks1 (list): The first list of node rankings.
    ranks2 (list): The second list of node rankings.
    title (str): The title of the plot.
    Returns:
    list: A list of tuples containing the top K nodes with the highest absolute residuals and their residual values.
    The function performs the following steps:
    1. Initializes lists for x and y coordinates, colors, sizes, texts, markers, and residuals.
    2. Iterates through the nodes in the graph and assigns coordinates, colors, texts, and markers based on node types.
    3. Calculates residuals for the nodes and adjusts marker sizes for better visualization.
    4. Creates a dictionary of nodes and their residuals, sorts it by the absolute value of the residuals, and selects the top K nodes.
    5. Changes the marker shape for the top K nodes based on the sign of their residuals.
    6. Plots the 'normal' nodes first, followed by the specific node types on top.
    7. Adds text labels for non-'normal' nodes.
    8. Draws a bisect line, sets plot labels and title, and saves the plot as a PNG file.
    Note:
    - The variable TOP_K should be defined globally.
    - The variable WORKING_DIRECTORY should be defined globally.
    """
    
    x = []
    y = []
    colors = []
    sizes = []
    texts = []
    markers = []
    residuals = []

    for node in g.nodes:
        x.append(ranks2[node] + 1)
        y.append(ranks1[node] + 1)
        node_type = g.nodes[node].get('type', 'normal')
        if node_type == 'vulcano':
            colors.append('red')
            texts.append((ranks2[node] + 1, ranks1[node] + 1, str(node)))
        elif node_type == 'black_hole':
            colors.append('black')
            texts.append((ranks2[node] + 1, ranks1[node] + 1, str(node)))
        elif node_type == 'ghost':
            colors.append('blue')
            texts.append((ranks2[node] + 1, ranks1[node] + 1, str(node)))
        elif node_type == 'mushroom':
            colors.append('brown')
            texts.append((ranks2[node] + 1, ranks1[node] + 1, str(node)))
        elif node_type == 'indirect_source':
            colors.append('orange')
            texts.append((ranks2[node] + 1, ranks1[node] + 1, str(node)))
        elif node_type == 'indirect_target':
            colors.append('green')
            texts.append((ranks2[node] + 1, ranks1[node] + 1, str(node)))
        elif node_type == 'intermediary':
            colors.append('purple')
            texts.append((ranks2[node] + 1, ranks1[node] + 1, str(node)))
        else:
            colors.append('cyan')

        # calculate the residuals for the nodes
        residual = (ranks1[node] + 1) - (ranks2[node] + 1)
        residuals.append(residual)
        sizes.append(abs(residual) * 5)  # Adjust the multiplier for better visualization
        markers.append('o')

    # create a dictionary with the nodes and their residuals
    residuals_dict = dict(zip(g.nodes, residuals))
    # sort the dictionary by the absolute value of the residuals
    nodes_sorted_by_residuals = sorted(residuals_dict.items(), key=lambda x: abs(x[1]), reverse=True)

    # get the TOP_K nodes and their residuals with the highest absolute value of the residuals
    top_k_nodes = nodes_sorted_by_residuals[:TOP_K]

    # change the marker shape for the top_k_nodes to the triangle up when the residual is positive 
    # and to the triangle down when the residual is negative
    for outlier in top_k_nodes:        
        if outlier[1] > 0:
            markers[outlier[0]]= '^'
        else:
            markers[outlier[0]]= 'v'

    # Plot 'normal' nodes first
    for i in range(len(x)):
        if  markers[i] == 'o':
            plt.scatter(x[i], y[i], c=colors[i], marker=markers[i], s=sizes[i], alpha=0.3)

    # Plot 'black_hole', 'vulcano', 'mushroom', and 'ghost' nodes on top
    for i in range(len(x)):
        if markers[i] != 'o':
            plt.scatter(x[i], y[i], c=colors[i], marker=markers[i], s=sizes[i], alpha=0.8)

    # Add text labels for not 'normal' nodes
    for text in texts:
        plt.text(text[0], text[1], text[2], fontsize=9, ha='right')

    plt.plot([min(x), max(x)], [min(y), max(y)], 'k--', lw=1)  # Bisect line
    plt.xlabel('Rank in first list')
    plt.ylabel('Rank in second list')
    plt.title(title)
    
    plt.savefig(os.path.join(WORKING_DIRECTORY+'/plots', 'rankcomparison_by'+title + '.png'))
    plt.close()

    return top_k_nodes
