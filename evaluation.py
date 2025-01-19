

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