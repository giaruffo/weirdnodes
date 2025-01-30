import networkx as nx
import random
import matplotlib.pyplot as plt
import numpy as np
from globals import *

def perturb_network_by_nodes(g0, n):
    """
    Perturbs a given network by rewiring the edges of n randomly selected nodes.

    Parameters:
    g0 (networkx.DiGraph): The original directed graph to be perturbed.
    n (int): The number of nodes to perturb in the graph.

    Returns:
    networkx.DiGraph: A new graph with the specified perturbations.

    Raises:
    ValueError: If n is greater than the number of nodes in the graph.

    Notes:
    - Each selected node will either have its outgoing or incoming edges rewired.
    - Nodes are assigned a type 'normal', 'black_hole', or 'volcano' based on the perturbation.
    - 'black_hole' nodes will have a significant increase in the transaction activity, 
        and a significant reduction of outgoing transactions.
    - 'volcano' nodes will have a significant decrease in the number of incoming transactions, 
        and a significant increase of outgoing transactions.
    """
    # Create a copy of g0 to perturb
    g1 = g0.copy()

    # Ensure n is not greater than the number of nodes
    if n > len(g1.nodes):
        raise ValueError("n is greater than the number of nodes in the graph")

    # Select eligible nodes to be perturbd: nodes with indegree > 2 and outdegree > 2
    eligible_nodes = [node for node in g1.nodes if g1.in_degree(node) > 2 and g1.out_degree(node) > 2]
    
    # Ensure there are enough eligible nodes to perturb
    if len(eligible_nodes) < n:
        raise ValueError("Not enough nodes with indegree > 2 and outdegree > 2 to perturb")
    
    # Select n random nodes to perturb from eligible nodes
    nodes_to_perturb = random.sample(eligible_nodes, n)

    # Initialize nodes' types as 'normal'
    for node in g1.nodes:
        if 'type' not in g1.nodes[node]:
            g1.nodes[node]['type'] = 'normal'

    for node in nodes_to_perturb:
        if random.random() < 0.5:
            # Selected node will be a 'black_hole'
            g1.nodes[node]['type'] = 'black_hole'
            # Rewire a significant portion of outgoing links
            out_edges = list(g1.out_edges(node, data=True))
            # Perturb a fraction of the outgoing edges
            num_out_edges_to_rewire = int(len(out_edges) * random.uniform(EDGE_MIN_FRACTION, EDGE_MAX_FRACTION))
            out_edges_to_rewire = random.sample(out_edges, num_out_edges_to_rewire)
            for edge in out_edges_to_rewire:
                g1.remove_edge(*edge[:2])
                new_source = random.choice(list(g1.nodes))
                while new_source == node:
                    new_source = random.choice(list(g1.nodes))
                g1.add_edge(new_source, edge[1], weight=edge[2]['weight'])
            
            # Add a significant factor of incoming links
            in_edges = list(g1.in_edges(node, data=True))
            num_in_edges_to_add = int(len(in_edges) * random.uniform(EDGE_MIN_FACTOR, EDGE_MAX_FACTOR))
            for _ in range(num_in_edges_to_add):
                new_source = random.choice(list(g1.nodes))
                while new_source == node:
                    new_source = random.choice(list(g1.nodes))
                g1.add_edge(new_source, node, weight=abs(RANDOM_FUNCTION(MEAN, STD_DEV))) # Add a random weight to the new edge 
       
            # Set the node type to 'black_hole'
            g1.nodes[node]['type'] = 'black_hole'
        else:
            # Selected node will be a 'volcano'
            g1.nodes[node]['type'] = 'volcano'
            # Rewire a significant portion of incoming links
            if len(list(g1.in_edges(node))) > 0:
                in_edges = list(g1.in_edges(node, data=True))
                num_in_edges_to_rewire = int(len(in_edges) * random.uniform(EDGE_MIN_FRACTION, EDGE_MAX_FRACTION))
                in_edges_to_rewire = random.sample(in_edges, num_in_edges_to_rewire)
                for edge in in_edges_to_rewire:
                    g1.remove_edge(*edge[:2])
                    new_target = random.choice(list(g1.nodes))
                    while new_target == node:
                        new_target = random.choice(list(g1.nodes))
                    g1.add_edge(edge[0], new_target, weight=edge[2]['weight'])
            # Add a significant factor of outgoing links
            out_edges = list(g1.out_edges(node, data=True))
            num_out_edges_to_add = int(len(out_edges) * random.uniform(EDGE_MIN_FACTOR, EDGE_MAX_FACTOR))
            for _ in range(num_out_edges_to_add):
                new_target = random.choice(list(g1.nodes))
                while new_target == node:
                    new_target = random.choice(list(g1.nodes))
                g1.add_edge(node, new_target, weight=abs(RANDOM_FUNCTION(MEAN, STD_DEV))) # Add a random weight to the new edge
    return g1

def perturb_network_by_links(g0, n):
    """
    Perturbs a given network by modifying the weights of a specified number of edges.
    Parameters:
    g0 (networkx.Graph): The original graph to be perturbd.
    n (int): The number of edges to perturb.
    Returns:
    networkx.Graph: A new graph with perturbd edges.
    Raises:
    ValueError: If n is greater than the number of edges in the graph.
    Notes:
    - Each node in the graph is initialized with a 'type' attribute set to 'normal'.
    - For each selected edge, there is a 50% chance to perturb it as a 'ghost' link or a 'mushroom' link.
    - 'Ghost' link: The weight of the edge is reduced of a random fraction between GHOSTING_LINK_MIN_FRACTION and 
        GHOSTING_LINK_MAX_FRACTION, and the source and target nodes' types are set to 'ghost'.
    - 'Mushroom' link: The weight of the edge is increased by a random factor between MUSHROOM_LINK_MIN_FACTOR and 
        MUSHROOM_LINK_MAX_FACTOR, and the source and target nodes' types are set to 'mushroom'.
    - If an edge's weight is non-positive, it is either replaced with another random edge or set to a minimum weight value of 0.1.
    """
    g1 = g0.copy()
    
    # Ensure n is not greater than the number of edges
    if n > len(g1.edges):
        raise ValueError("n is greater than the number of edges in the graph")
    
    # Select n random links to perturb
    edges_to_perturb = random.sample(list(g1.edges), n)

    # Initialize nodes' types as 'normal'
    for node in g1.nodes:
        if 'type' not in g1.nodes[node]:
            g1.nodes[node]['type'] = 'normal'

    for edge in edges_to_perturb:
        if random.random() < 0.5:
            # Our link perturbation strategy is to simulating a GHOST link
            # Change  source and the target nodes' types 
            g1.nodes[edge[0]]['type'] = 'ghost'
            g1.nodes[edge[1]]['type'] = 'ghost'
            # Check if the edge's weight is non-positive
            if g1[edge[0]][edge[1]]['weight'] <= 0:
                # add another random edge to edges_to_perturb and continue
                new_edge = random.choice(list(g1.edges))   
                while new_edge in edges_to_perturb:
                    new_edge = random.choice(list(g1.edges))
                edges_to_perturb.append(new_edge)
                edges_to_perturb.remove(edge)
                continue
            # Perturbs the weight of the edge, multiplying it by a random fraction between 
            # GHOSTING_LINK_MIN_FRACTION and GHOSTING_LINK_MAX_FRACTION
            g1[edge[0]][edge[1]]['weight'] *= random.uniform(GHOSTING_LINK_MIN_FRACTION, GHOSTING_LINK_MAX_FRACTION)

        else:
            # Our link perturbation strategy is to simulating a MUSHROOM link
            # Change  source and the target nodes' types
            if g1[edge[0]][edge[1]]['weight'] <= 0:
                g1[edge[0]][edge[1]]['weight'] = MIN_WEIGHT  # Set a minimum weight value
            # Perturb the weight of the edge, increasing it by a random factor between 
            # MUSHROOM_LINK_MIN_FACTOR and MUSHROOM_LINK_MAX_FACTOR
            g1.nodes[edge[0]]['type'] = 'mushroom'
            g1.nodes[edge[1]]['type'] = 'mushroom'
            g1[edge[0]][edge[1]]['weight'] *= random.uniform(MUSHROOM_LINK_MIN_FACTOR, MUSHROOM_LINK_MAX_FACTOR)         
    return g1

# Create a function to perturb the network selecting a random number of links to remove, 
# and for each removed link, we select a random number of nodes to be used as new intermediary nodes between 
# the source and target nodes.
def perturb_network_with_intermediary_nodes(g, num_links_to_remove, num_intermediary_nodes):
    """
    Perturbs a given network by removing a specified number of links and adding intermediary nodes between the source and target nodes.
    The original source and target nodes of the removed links are set to 'indirect_source' and 'indirect_target', respectively.
    The intermediary nodes are set to 'intermediary'. The weights of the new links are set to a random value between MIN_WEIGHT and MAX_WEIGHT.
    The weights of the removed links are set to a minimum value of MIN_WEIGHT.
    Parameters:
    g (networkx.Graph): The input graph to be perturbd.
    num_links_to_remove (int): The number of links to remove from the graph.
    num_intermediary_nodes (int): The number of intermediary nodes to add between the source and target nodes of the removed links.
    Returns:
    networkx.Graph: A new graph with the specified perturbations applied.
    Raises:
    ValueError: If the number of links to remove is greater than the number of edges in the graph.
    ValueError: If the number of intermediary nodes is greater than the number of nodes in the graph minus 2.
    """
    # Raise an error if the number of links to remove is greater than the number of edges in the graph
    if num_links_to_remove > len(g.edges()):
        raise ValueError('The number of links to remove is greater than the number of edges in the graph')
    # Raise an error if the number of intermediary nodes is greater than the number of nodes in the graph minus 2
    if num_intermediary_nodes > len(g.nodes()) - 2:
        raise ValueError('The number of intermediary nodes is greater than the number of nodes in the graph minus 2')
    # Create a copy of the graph
    g1 = g.copy()
    # Initialize nodes' types as 'normal'
    for node in g1.nodes:
        if 'type' not in g1.nodes[node]:
            g1.nodes[node]['type'] = 'normal'
    # Get a list of edges and shuffle it
    edges = list(g.edges())
    random.shuffle(edges)
    # Select the first num_links_to_remove edges to remove
    edges_to_remove = edges[:num_links_to_remove]
    # Remove the selected edges and add intermediary nodes between the source and target nodes
    for edge in edges_to_remove:
        g1.remove_edge(edge[0], edge[1])
        intermediary_nodes = random.sample([node for node in g.nodes() if node not in edge], num_intermediary_nodes)
        for node in intermediary_nodes:
            g1.add_edge(edge[0], node, weight=RANDOM_FUNCTION(MEAN, STD_DEV))
            g1.add_edge(node, edge[1], weight=RANDOM_FUNCTION(MEAN, STD_DEV))
            # Set the type of the intermediary nodes to 'intermediary'
            g1.nodes[node]['type'] = 'intermediary'
            # Set the type of the source and target nodes to 'indirect_source' and 'indirect_target'
            g1.nodes[edge[0]]['type'] = 'indirect_source'
            g1.nodes[edge[1]]['type'] = 'indirect_target'
    return g1

def plot_graphs_comparison(g0, g1, centralities0, centralities1, centrality_str = 'degree'):
    """
    Plot the original and perturbd graphs side by side.

    Parameters:
    g0 (networkx.Graph): The original graph.
    g1 (networkx.Graph): The perturbd graph.
    centralities0 (tuple): A tuple containing the centrality values to use for ranking the nodes in g0.
    centralities1 (tuple): A tuple containing the centrality values to use for ranking the nodes in g1.
    centrality_str (str): The name of the centrality measure used for ranking the nodes.

    The function will plot the two graphs side by side using a spring layout
    computed from the original graph. Nodes are colored based on their 'type'
    attribute, with the following color scheme:
        - 'normal': cyan
        - 'black_hole': black
        - 'volcano': red
        - 'mushroom': brown
        - 'ghost': blue
        - 'indirect_source': green
        - 'indirect_target': yellow
        - 'intermediary': purple

    The resulting plot is saved as 'graphs_comparison_by{centrality_str}.png' in the WORKING_DIR + '\plots directory.
    """

    # raise an error if the centralities tuple's length is not equal to number of nodes
    if len(centralities0) != len(g0.nodes) or len(centralities1) != len(g1.nodes):
        raise ValueError("Length of centralities tuple does not match the number of nodes in the graphs.")

    # Plot the original and perturbd graphs side by side
    pos = nx.spring_layout(g0)  # Compute layout for g0 and use it for g1

    # Adjust positions to avoid overlapping nodes
    pos = nx.spring_layout(g0, k=0.15, iterations=20)
    plt.figure(figsize=(12, 6))

    # Define color maps for node types
    color_map_g1 = []
    for node in g1.nodes:
        if g1.nodes[node]['type'] == 'black_hole':
            color_map_g1.append('black')
        elif g1.nodes[node]['type'] == 'volcano':
            color_map_g1.append('red')
        elif g1.nodes[node]['type'] == 'mushroom':
            color_map_g1.append('brown')
        elif g1.nodes[node]['type'] == 'ghost':
            color_map_g1.append('blue')
        elif g1.nodes[node]['type'] == 'indirect_source':
            color_map_g1.append('orange')
        elif g1.nodes[node]['type'] == 'indirect_target':
            color_map_g1.append('green')
        elif g1.nodes[node]['type'] == 'intermediary':
            color_map_g1.append('purple')
        else: # type is 'normal'
            color_map_g1.append('cyan')
    plt.subplot(121)
    # Resize nodes based on centralities
    node_sizes_g0 = [centralities0[node] * 1000 for node in g0.nodes]
    node_sizes_g1 = [centralities1[node] * 1000 for node in g1.nodes]

    plt.subplot(121)
    nx.draw(g0, pos, with_labels=True, node_size=node_sizes_g0, font_size=10, node_color='cyan', edge_color='lightgray', alpha=0.5)
    plt.title(f'Original Graph - nodes resized by: {centrality_str}')

    plt.subplot(122)
    nx.draw(g1, pos, with_labels=True, node_size=node_sizes_g1, font_size=10, node_color=color_map_g1, edge_color='lightgray', alpha=0.5)
    plt.title(f'Perturbd Graph - nodes resized by: {centrality_str}')

    plt.savefig(os.path.join(WORKING_DIRECTORY+'/plots', f'graphcomparison_by{centrality_str}.png'))
    plt.close()

def store_graph_metrics_infile(f, g, graph_name):
    """
    Stores various graph metrics into a file.
    Parameters:
    f (file object): The file object where the metrics will be written.
    g (networkx.Graph): The graph for which metrics are calculated.
    graph_name (str): The name of the graph to be used in the output.
    Metrics stored:
    - Number of nodes
    - Number of links (edges)
    - Min, Max, Avg, Std of degree, in_degree, out_degree
    - Min, Max, Avg, Std of strength, in_strength, out_strength
    - Min, Max, Avg, Std of edges' weights
    - Average clustering coefficient
    - Average shortest path length
    - Diameter
    - Density
    The function writes these metrics to the provided file object.
    """

    f.write(f"Graph {graph_name}: Number of nodes: {g.number_of_nodes()}, Number of links: {g.number_of_edges()}\n")
    # summary statics (min, max, avg, std, etc.) information on degree, in_degree, out_degree, and link's weights
    degrees_g, indegrees_g, outdegrees_g = [d for n, d in g.degree()], [d for n, d in g.in_degree()], [d for n, d in g.out_degree()]
    weights_g = [d['weight'] for u, v, d in g.edges(data=True)]
    strengths_g, in_strengths_g, out_strengths_g = [d for n, d in g.degree(weight='weight')], [d for n, d in g.in_degree(weight='weight')], [d for n, d in g.out_degree(weight='weight')]
    f.write(f"Graph {graph_name}: Min, Max, Avg, Std of degree: {min(degrees_g)}, {max(degrees_g)}, {sum(degrees_g)/len(degrees_g)}, {np.std(degrees_g)}\n")
    f.write(f"Graph {graph_name}: Min, Max, Avg, Std of in_degree: {min(indegrees_g)}, {max(indegrees_g)}, {sum(indegrees_g)/len(indegrees_g)}, {np.std(indegrees_g)}\n")
    f.write(f"Graph {graph_name}: Min, Max, Avg, Std of out_degree: {min(outdegrees_g)}, {max(outdegrees_g)}, {sum(outdegrees_g)/len(outdegrees_g)}, {np.std(outdegrees_g)}\n")
    f.write(f"Graph {graph_name}: Min, Max, Avg, Std of strength: {min(strengths_g)}, {max(strengths_g)}, {sum(strengths_g)/len(strengths_g)}, {np.std(strengths_g)}\n")
    f.write(f"Graph {graph_name}: Min, Max, Avg, Std of in_strength: {min(in_strengths_g)}, {max(in_strengths_g)}, {sum(in_strengths_g)/len(in_strengths_g)}, {np.std(in_strengths_g)}\n")
    f.write(f"Graph {graph_name}: Min, Max, Avg, Std of out_strength: {min(out_strengths_g)}, {max(out_strengths_g)}, {sum(out_strengths_g)/len(out_strengths_g)}, {np.std(out_strengths_g)}\n")
    f.write(f"Graph {graph_name}: Min, Max, Avg, Std of edges' weights: {min([d['weight'] for u, v, d in g.edges(data=True)]), max([d['weight'] for u, v, d in g.edges(data=True)]), np.mean([d['weight'] for u, v, d in g.edges(data=True)]), np.std([d['weight'] for u, v, d in g.edges(data=True)])}\n")

    # clustering coefficient, average shortest path length, diameter, and density
    f.write(f"Graph {graph_name}: Average clustering: {nx.average_clustering(g)}\n")
    f.write(f"Graph {graph_name}: Average shortest path length: {nx.average_shortest_path_length(g)}\n")
    f.write(f"Graph {graph_name}: Diameter: {nx.diameter(g)}\n")
    f.write(f"Graph {graph_name}: Density: {nx.density(g)}\n")
    f.write("-----------------------------------\n")

def plot_graph_distributions(g, graph_name):
    """
    Plots and saves the distributions of various graph properties for a given graph.
    Parameters:
    g (networkx.Graph): The input graph for which distributions are to be plotted.
    graph_name (str): The name of the graph, used for saving the plot.
    The function calculates and plots the following distributions:
    - Degree
    - In-degree
    - Out-degree
    - Strength (weighted degree)
    - In-strength (weighted in-degree)
    - Out-strength (weighted out-degree)
    - Edge weights
    The plots are arranged in a 3x3 grid and saved as a PNG file in the 'plots' directory
    within the working directory, with the filename format 'distributions_<graph_name>.png'.
    """
    
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
    plt.savefig(WORKING_DIRECTORY+f'/plots/distributions_{graph_name}.png')
    plt.close()