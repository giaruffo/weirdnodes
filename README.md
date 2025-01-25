# weirdnodes

## Description

This repository contains the code for the paper "WeirdNodes: Centrality Based Anomaly Detection
on Temporal Networks for the Anti-Financial
Crime Domain" by Salvatore Vilella, Arthur T. E. C. Lupi, Marco Fornasiero, Dario Moncalvo, Valeria Ricci, Silvia Ronchiadin, and Giancarlo Ruffo.

## Installation

To install the required packages, run the following command: `pip install -r requirements.txt`

## Configuration

The configuration file `config.py` contains the following parameters:
- `RANDOM_FUNCTION`: The random function to use for perturbating the network.
- `MEAN`, `STD_DEV`: The mean and standard deviation of the random function.
- `NUM_NODES_TO_PERTURB`: The number of nodes to perturb.
- `NUM_LINKS_TO_PERTURB`: The number of links to perturb.
- `NUM_INTERMEDIARY_NODES`: The number of nodes to add as intermediary nodes.   
- `CENTRALITY_MEASURES`: The centrality measures to rank nodes and to use for the anomaly detection strategies
- `MIN_WEIGHT`: The minimum weight of the links.
- `EDGE_MIN_FRACTION`, `EDGE_MAX_FRACTION`: The minimum and maximum fraction of edges to remove/rewire during perturbation.
- `EDGE_MIN_FACTOR`, `EDGE_MAX_FACTOR`: The minimum and maximum factor of edges to add/rewire during perturbation.
- `GHOSTING_LINK_MIN_FRACTION`, `GHOSTING_LINK_MAX_FRACTION`: The minimum and maximum fraction of links to rewire during ghosting perturbation.
- `MUSHROOM_LINK_MIN_FACTOR`, `MUSHROOM_LINK_MAX_FACTOR`: The minimum and maximum factor of links to add during mushroom perturbation.
- `TOP_K`: The number of top nodes to consider for the anomaly detection strategies.

You can change these parameters to fit your needs.

## Usage

To run the code, run one of the test files in the main folder. For example, to run an experiment that perturates the network with vulcanoes and blackholes nodes, run command: `python test_ER_vulcanoes_blackholes.py`

## Description of functions that pertubates the network given as input in the `net_perturbation.py` file:

- `perturb_network_by_nodes(g0, n)`: 
    Perturbs the network by adding `n` nodes.     

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

- `perturb_network_by_links(g0, n)`: 
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

- `perturb_network_with_intermediary_nodes(g, num_links_to_remove, num_intermediary_nodes)`: 
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

- `plot_graphs_comparison(g0, g1, centralities0, centralities1, centrality_str = 'degree')`:     
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
        - 'vulcano': red
        - 'mushroom': brown
        - 'ghost': blue
        - 'indirect_source': green
        - 'indirect_target': yellow
        - 'intermediary': purple

    The resulting plot is saved as 'graphs_comparison_by{centrality_str}.png' in the WORKING_DIR + '\plots directory.

- `store_graph_metrics_infile(f, g, graph_name)`:
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

- `plot_graph_distributions(g, graph_name)`:
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



