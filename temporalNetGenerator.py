import networkx as nx
import random
import matplotlib.pyplot as plt
from config import *

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
    - Nodes are assigned a type 'normal', 'black_hole', or 'vulcano' based on the perturbation.
    - 'black_hole' nodes have their outgoing edges rewired.
    - 'vulcano' nodes have their incoming edges rewired.
    """
    # Create a copy of g0 to perturb
    g1 = g0.copy()

    # Ensure n is not greater than the number of nodes
    if n > len(g1.nodes):
        raise ValueError("n is greater than the number of nodes in the graph")

    # Select n random nodes to perturb
    nodes_to_perturb = random.sample(list(g1.nodes), n)

    # Initialize nodes' types as 'normal'
    for node in g1.nodes:
        g1.nodes[node]['type'] = 'normal'

    for node in nodes_to_perturb:
        if random.random() < 0.5:
            # Rewire outgoing links
            out_edges = list(g1.out_edges(node, data=True))
            num_out_edges_to_perturb = int(len(out_edges) * random.uniform(OUT_EDGE_MIN_FACTOR, OUT_EDGE_MAX_FACTOR))
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
            num_in_edges_to_perturb = int(len(in_edges) * random.uniform(IN_EDGE_MIN_FACTOR, IN_EDGE_MAX_FACTOR))
            in_edges_to_perturb = random.sample(in_edges, num_in_edges_to_perturb)
            for edge in in_edges_to_perturb:
                g1.remove_edge(*edge[:2])
                new_target = random.choice(list(g1.nodes))
                while new_target == node:
                    new_target = random.choice(list(g1.nodes))
                g1.add_edge(edge[0], new_target, weight=edge[2]['weight'])
            g1.nodes[node]['type'] = 'vulcano'

    return g1

def perturb_network_by_links(g0, n):
    """
    Perturbs a given network by modifying the weights of a specified number of edges.
    Parameters:
    g0 (networkx.Graph): The original graph to be perturbed.
    n (int): The number of edges to perturb.
    Returns:
    networkx.Graph: A new graph with perturbed edges.
    Raises:
    ValueError: If n is greater than the number of edges in the graph.
    Notes:
    - Each node in the graph is initialized with a 'type' attribute set to 'normal'.
    - For each selected edge, there is a 50% chance to perturb it as a 'ghost' link or a 'mushroom' link.
    - 'Ghost' link: The weight of the edge is reduced by a random factor between 0.5 and 1, and the source and target nodes' types are set to 'ghost'.
    - 'Mushroom' link: The weight of the edge is increased by a random factor between 5 and 10, and the source and target nodes' types are set to 'mushroom'.
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
        g1.nodes[node]['type'] = 'normal'

    for edge in edges_to_perturb:
        if random.random() < 0.5:
            # Our link perturbation strategy is to simulating a ghost link
            # Change  source and the target nodes' types 
            if g1[edge[0]][edge[1]]['weight'] <= 0:
                # add another random edge to edges_to_perturb and continue
                new_edge = random.choice(list(g1.edges))   
                while new_edge in edges_to_perturb:
                    new_edge = random.choice(list(g1.edges))
                edges_to_perturb.append(new_edge)
                edges_to_perturb.remove(edge)
                continue
            # Perturb the weight of the edge, reducing it by a random factor between GHOST_MIN_FACTOR and GHOST_MAX_FACTOR
            g1[edge[0]][edge[1]]['weight'] *= random.uniform(GHOST_MIN_FACTOR, GHOST_MAX_FACTOR)
            g1.nodes[edge[0]]['type'] = 'ghost'
            g1.nodes[edge[1]]['type'] = 'ghost'
        else:
            # Our link perturbation strategy is to simulating a mushroom link
            # Change  source and the target nodes' types
            if g1[edge[0]][edge[1]]['weight'] <= 0:
                g1[edge[0]][edge[1]]['weight'] = MIN_WEIGHT  # Set a minimum weight value
            # Perturb the weight of the edge, increasing it by a random factor between MUSHROOM_MIN_FACTOR and MUSHROOM_MAX_FACTOR
            g1.nodes[edge[0]]['type'] = 'mushroom'
            g1.nodes[edge[1]]['type'] = 'mushroom'
            g1[edge[0]][edge[1]]['weight'] *= random.uniform(MUSHROOM_MIN_FACTOR, MUSHROOM_MAX_FACTOR)
            
    return g1


def plot_graph(g, title):
    pos = nx.spring_layout(g)
    weights = nx.get_edge_attributes(g, 'weight').values()
    nx.draw(g, pos, with_labels=True, node_size=500, node_color="skyblue", edge_color="gray", width=[weight / max(weights) for weight in weights])
    plt.title(title)
    plt.show()

def calculate_precision_at_k(g,top_nodes, k):
    """
    Calculate the precision at k for a given graph and a list of top nodes.

    Precision at k is defined as the number of relevant nodes in the top k nodes
    divided by k. A node is considered relevant if its 'type' attribute is not 'normal'.

    Args:
        g (networkx.Graph): The graph containing the nodes.
        top_nodes (list): A list of tuples where each tuple contains a node and its score.
        k (int): The number of top nodes to consider.

    Returns:
        float: The precision at k, which is the ratio of relevant nodes in the top k nodes.
    """
    relevant_nodes = [node for node, _ in top_nodes[:k] if g.nodes[node]['type'] != 'normal']
    return len(relevant_nodes) / k


