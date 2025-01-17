import matplotlib.pyplot as plt
import os
import networkx as nx
import pandas as pd

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
    list: A list of nodes ranked by the specified centrality measure in descending order.

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
    """
    Plots a comparison of node rankings from two different lists.

    Parameters:
    g (networkx.Graph): The graph containing the nodes to be ranked.
    ranks1 (list): The first list of node rankings.
    ranks2 (list): The second list of node rankings.
    title (str): The title of the plot.

    The function generates a scatter plot where each node is represented by a point.
    The x-coordinate of the point corresponds to the node's rank in the first list,
    and the y-coordinate corresponds to the node's rank in the second list.
    Nodes of different types ('vulcano', 'black_hole', 'ghost', 'mushroom', 'normal') are colored differently.
    The size of each point is proportional to the absolute difference between the node's ranks in the two lists.
    A bisect line is drawn to help visualize the ranking differences.
    The plot is saved as a PNG file with the given title.
    """
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
        elif node_type == 'ghost':
            colors.append('blue')
            texts.append((ranks1.index(node) + 1, ranks2.index(node) + 1, str(node)))
        elif node_type == 'normal':
            colors.append('green')
            texts.append((ranks1.index(node) + 1, ranks2.index(node) + 1, str(node)))
        else:
            colors.append('cyan')
        residual = abs((ranks1.index(node) + 1) - (ranks2.index(node) + 1))
        sizes.append(residual * 5)  # Adjust the multiplier for better visualization

    # Plot 'normal' nodes first
    for i in range(len(x)):
        if colors[i] == 'cyan':
            plt.scatter(x[i], y[i], c=colors[i], s=sizes[i], alpha=0.5)

    # Plot 'black_hole', 'vulcano', 'mushroom', and 'ghost' nodes on top
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
    
    from config import WORKING_DIRECTORY  # Import working_directory from config.py
    plt.savefig(os.path.join(WORKING_DIRECTORY, title + '.png'))
    # plt.show()
