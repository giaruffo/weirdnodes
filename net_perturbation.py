import networkx as nx
import random
import matplotlib.pyplot as plt
from config import *

def perturbate_network_by_nodes(g0, n):
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
    - Nodes are assigned a type 'normal', 'black_hole', or 'vulcano' based on the perturbation.
    - 'black_hole' nodes will have a significant increase in the transaction activity, 
        and a significant reduction of outgoing transactions.
    - 'vulcano' nodes will have a significant decrease in the number of incoming transactions, 
        and a significant increase of outgoing transactions.
    """
    # Create a copy of g0 to perturb
    g1 = g0.copy()

    # Ensure n is not greater than the number of nodes
    if n > len(g1.nodes):
        raise ValueError("n is greater than the number of nodes in the graph")

    # Select eligible nodes to be perturbated: nodes with indegree > 2 and outdegree > 2
    eligible_nodes = [node for node in g1.nodes if g1.in_degree(node) > 2 and g1.out_degree(node) > 2]
    
    # Ensure there are enough eligible nodes to perturbate
    if len(eligible_nodes) < n:
        raise ValueError("Not enough nodes with indegree > 2 and outdegree > 2 to perturbate")
    
    # Select n random nodes to perturbate from eligible nodes
    nodes_to_perturbate = random.sample(eligible_nodes, n)

    # Initialize nodes' types as 'normal'
    for node in g1.nodes:
        g1.nodes[node]['type'] = 'normal'

    for node in nodes_to_perturbate:
        if random.random() < 0.5:
            # Selected node will be a 'black_hole'
            g1.nodes[node]['type'] = 'black_hole'
            # Rewire a significant portion of outgoing links
            out_edges = list(g1.out_edges(node, data=True))
            # Perturbate a fraction of the outgoing edges
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
            # Selected node will be a 'vulcano'
            g1.nodes[node]['type'] = 'vulcano'
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

def perturbate_network_by_links(g0, n):
    """
    Perturbates a given network by modifying the weights of a specified number of edges.
    Parameters:
    g0 (networkx.Graph): The original graph to be perturbated.
    n (int): The number of edges to perturbate.
    Returns:
    networkx.Graph: A new graph with perturbated edges.
    Raises:
    ValueError: If n is greater than the number of edges in the graph.
    Notes:
    - Each node in the graph is initialized with a 'type' attribute set to 'normal'.
    - For each selected edge, there is a 50% chance to perturbate it as a 'ghost' link or a 'mushroom' link.
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
    
    # Select n random links to perturbate
    edges_to_perturbate = random.sample(list(g1.edges), n)

    # Initialize nodes' types as 'normal'
    for node in g1.nodes:
        g1.nodes[node]['type'] = 'normal'

    for edge in edges_to_perturbate:
        if random.random() < 0.5:
            # Our link perturbation strategy is to simulating a GHOST link
            # Change  source and the target nodes' types 
            g1.nodes[edge[0]]['type'] = 'ghost'
            g1.nodes[edge[1]]['type'] = 'ghost'
            # Check if the edge's weight is non-positive
            if g1[edge[0]][edge[1]]['weight'] <= 0:
                # add another random edge to edges_to_perturbate and continue
                new_edge = random.choice(list(g1.edges))   
                while new_edge in edges_to_perturbate:
                    new_edge = random.choice(list(g1.edges))
                edges_to_perturbate.append(new_edge)
                edges_to_perturbate.remove(edge)
                continue
            # Perturbates the weight of the edge, multiplying it by a random fraction between 
            # GHOSTING_LINK_MIN_FRACTION and GHOSTING_LINK_MAX_FRACTION
            g1[edge[0]][edge[1]]['weight'] *= random.uniform(GHOSTING_LINK_MIN_FRACTION, GHOSTING_LINK_MAX_FRACTION)

        else:
            # Our link perturbation strategy is to simulating a MUSHROOM link
            # Change  source and the target nodes' types
            if g1[edge[0]][edge[1]]['weight'] <= 0:
                g1[edge[0]][edge[1]]['weight'] = MIN_WEIGHT  # Set a minimum weight value
            # Perturbate the weight of the edge, increasing it by a random factor between 
            # MUSHROOM_LINK_MIN_FACTOR and MUSHROOM_LINK_MAX_FACTOR
            g1.nodes[edge[0]]['type'] = 'mushroom'
            g1.nodes[edge[1]]['type'] = 'mushroom'
            g1[edge[0]][edge[1]]['weight'] *= random.uniform(MUSHROOM_LINK_MIN_FACTOR, MUSHROOM_LINK_MAX_FACTOR)         
    return g1

# Create a function to perturbate the network selecting a random number of links to remove, 
# and for each removed link, we select a random number of nodes to be used as new intermediary nodes between 
# the source and target nodes.
def perturbate_network_with_intermediary_nodes(g, num_links_to_remove, num_intermediary_nodes):
    """
    Perturbates a given network by removing a specified number of links and adding intermediary nodes between the source and target nodes.
    Parameters:
    g (networkx.Graph): The input graph to be perturbated.
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
    Plot the original and perturbated graphs side by side.

    Parameters:
    g0 (networkx.Graph): The original graph.
    g1 (networkx.Graph): The perturbated graph.
    centralities0 (tuple): A tuple containing the centrality values to use for ranking the nodes in g0.
    centralities1 (tuple): A tuple containing the centrality values to use for ranking the nodes in g1.
    centrality_str (str): The name of the centrality measure used for ranking the nodes.

    The function will plot the two graphs side by side using a spring layout
    computed from the original graph. Nodes are colored based on their 'type'
    attribute, with the following color scheme:
        - 'normal': cyan
        - 'black_hole': black
        - 'vulcano': red
        - 'mushroom': brown
        - 'ghost': blue

    The resulting plot is saved as 'graph_comparison.png' in the working directory.
    """

    # raise an error if the centralities tuple's length is not equal to number of nodes
    if len(centralities0) != len(g0.nodes) or len(centralities1) != len(g1.nodes):
        raise ValueError("Length of centralities tuple does not match the number of nodes in the graphs.")

    plt.clf()
    # Plot the original and perturbated graphs side by side
    pos = nx.spring_layout(g0)  # Compute layout for g0 and use it for g1

    # Adjust positions to avoid overlapping nodes
    pos = nx.spring_layout(g0, k=0.15, iterations=20)
    plt.figure(figsize=(12, 6))

    # Define color maps for node types
    color_map_g1 = []
    for node in g1.nodes:
        if g1.nodes[node]['type'] == 'black_hole':
            color_map_g1.append('black')
        elif g1.nodes[node]['type'] == 'vulcano':
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
    plt.title(f'Perturbated Graph - nodes resized by: {centrality_str}')

    plt.savefig(os.path.join(WORKING_DIRECTORY+'/plots', f'graphcomparison_by{centrality_str}.png'))
    plt.close()
