

import os
import matplotlib.pyplot as plt
from config import *

def precision_at_k(g,top_nodes, k):
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

def recall_at_k(g,top_nodes, k):
    """
    Calculate the recall at k for a given graph and a list of top nodes.
    Recall at k is defined as the number of relevant nodes in the top k nodes
    divided by the total number of relevant nodes in the graph. A node is considered relevant if its 'type' attribute is not 'normal'.
    Args:
       g (networkx.Graph): The graph containing the nodes.
       top_nodes (list): A list of tuples where each tuple contains a node and its score.
       k (int): The number of top nodes to consider.
    Returns:
        float: The recall at k, which is the ratio of relevant nodes in the top k nodes to the total number of relevant nodes.
    """
    relevant_nodes = [node for node, _ in top_nodes[:k] if g.nodes[node]['type'] != 'normal']
    total_relevant_nodes = len([node for node in g.nodes if g.nodes[node]['type'] != 'normal'])
    return len(relevant_nodes) / total_relevant_nodes

def avg_precision_at_k(g, top_nodes, k):
    """
    Calculate the average precision at k for a given graph and a list of top nodes.
    Average precision at k is defined as the average of the precision at k for each relevant node in the top k nodes.
    Args:
        g (networkx.Graph): The graph containing the nodes.
        top_nodes (list): A list of tuples where each tuple contains a node and its score.
        k (int): The number of top nodes to consider.
    Returns:
        float: The average precision at k, which is the average of the precision at k for each relevant node in the top k nodes.
    """
    relevant_nodes = [node for node, _ in top_nodes[:k] if g.nodes[node]['type'] != 'normal']
    precision_at_k = [len(relevant_nodes[:i+1]) / (i+1) for i in range(k)]
    return sum(precision_at_k) / len(precision_at_k)

def store_top_k_nodes_in_file(g, top_k_nodes, strategy):
    """
    Store the top k nodes in a file.
    Args:
        g (networkx.Graph): The graph containing the nodes.
        top_k_nodes (list): A list of tuples where each tuple contains a node and its score.
        strategy (str): The strategy used to rank the nodes.
    """
    top_k_nodes_file_path = os.path.join(WORKING_DIRECTORY+'/evaluation_results', f"topknodes_{strategy}.txt")
    with open(top_k_nodes_file_path, "w") as f:
        f.write(f"Top {TOP_K} nodes sorted by the absolute value of the residuals of the ranks:\n")
        for node in top_k_nodes:
            f.write(f"{node}\t")
            # write node type to file
            f.write(f"Type: {g.nodes[node[0]]['type']}\n")

def mean_average_precision_at_k(g, top_nodes, k):   
    """
    Calculate the mean average precision at k for a given graph and a list of top nodes.
    Mean average precision at k is defined as the average of the average precision at k for each relevant node in the top k nodes.
    Args:
        g (networkx.Graph): The graph containing the nodes.
        top_nodes (list): A list of tuples where each tuple contains a node and its score.
        k (int): The number of top nodes to consider.
    Returns:
        float: The mean average precision at k, which is the average of the average precision at k for each relevant node in the top k nodes.
    """
    avg_precision_at_k = [avg_precision_at_k(g, top_nodes, i+1) for i in range(k)]
    return sum(avg_precision_at_k) / len(avg_precision_at_k)

def evaluate_results(g, top_k_nodes):
    """
    Evaluate the precision, recall, and average precision of the top K nodes.
    Parameters:
    g (Graph): The graph on which the evaluation is performed.
    top_k_nodes (list): A list of nodes to evaluate, ordered by their ranking.
    Returns:
    tuple: A tuple containing three lists:
        - precisions (list): Precision values at each rank from 1 to TOP_K.
        - recalls (list): Recall values at each rank from 1 to TOP_K.
        - avg_precisions (list): Average precision values at each rank from 1 to TOP_K.
    """
    precisions = []
    recalls = []   
    avg_precisions = []
    for i in range(1, TOP_K+1):
        precision = precision_at_k(g, top_k_nodes[:i], i)
        recall = recall_at_k(g, top_k_nodes[:i], i)
        average_precision = avg_precision_at_k(g, top_k_nodes[:i], i)
        # print(f"P@{i}: {precision}")
        # print(f"R@{i}: {recall}")
        # print(f"avg P@{i}: {average_precision}")
        precisions.append(precision)
        recalls.append(recall)
        avg_precisions.append(average_precision)

    return precisions, recalls, avg_precisions

def store_and_plot_evaluation_results(strategy, precisions, recalls, avg_precisions):
    """
    Stores evaluation results in text files and plots the results.
    Parameters:
    strategy (str): The strategy used for evaluation.
    precisions (list of float): List of precision values at each k.
    recalls (list of float): List of recall values at each k.
    avg_precisions (list of float): List of average precision values at each k.
    The function performs the following steps:
    1. Stores precision, recall, and average precision values in separate text files.
    2. Plots the precision, recall, and average precision values against k and saves the plot as a PNG file.
    The files are saved in directories specified by the WORKING_DIRECTORY variable defined in config.py.
    """
    
    # store the results in a file in the working directory as defined in config.py
    print(f"Storing evaluation results (by {strategy}) in files...")
    precision_at_k_file_path = os.path.join(WORKING_DIRECTORY+'/evaluation_results', f"precision_at_k_{strategy}.txt")
    recall_at_k_file_path = os.path.join(WORKING_DIRECTORY+'/evaluation_results', f"recall_at_k_{strategy}.txt")
    avg_precision_at_k_file_path = os.path.join(WORKING_DIRECTORY+'/evaluation_results', f"avg_precision_at_k_{strategy}.txt")
    with open(precision_at_k_file_path, "w") as f:
        f.write("Precision at k:\n")
        for i in range(1, TOP_K+1):
            f.write(f"P@{i}: {precisions[i-1]}\n")
    with open(recall_at_k_file_path, "w") as f:
        f.write("Recall at k:\n")
        for i in range(1, TOP_K+1):
            f.write(f"R@{i}: {recalls[i-1]}\n")
    with open(avg_precision_at_k_file_path, "w") as f:
        f.write("Average precision at k:\n")
        for i in range(1, TOP_K+1):
            f.write(f"avg P@{i}: {avg_precisions[i-1]}\n")
    # plot the results
    plt.plot(range(1, TOP_K+1), precisions, label='Precision at k')
    plt.plot(range(1, TOP_K+1), recalls, label='Recall at k')
    plt.plot(range(1, TOP_K+1), avg_precisions, label='Average precision at k')
    plt.xlabel('k')
    plt.ylabel('Score')
    plt.title(f'Evaluation results with strategy: {strategy}')
    
    plt.legend()
    plt.savefig(os.path.join(WORKING_DIRECTORY+'/plots', f'evaluation_by{strategy}.png'))
    plt.close()