
from globals import TOP_K

# rank_nodes_by_summation_strategy gets a dictionary whose key is a centrality measure
# and the value is a list of nodes sorted by the rank's residuals defined by the centrality measure.
# The function returns a list of nodes sorted by the mixed strategy.
# The mixed strategy is defined as follows:
# 1. For each node, it gets the rank
# 2. It calculates the sum of all the normalized ranks of the node across all centrality measures
# 3. It sorts the nodes by the sum of the normalized ranks
# 4. It returns the list of top-k nodes sorted by the normalized ranks and also the full
#    list of nodes sorted by the sum of the normalized ranks
# The normalization is done by dividing the rank of the node by the number of nodes in the graph
# The sum of the normalized ranks is the mixed strategy rank of the node
def rank_nodes_by_summation_strategy(nodes_sorted_dict):
    # get the number of nodes in the graph
    num_nodes = len(nodes_sorted_dict[list(nodes_sorted_dict.keys())[0]])
    # create a dictionary to store the sum of the normalized ranks of each node
    sum_normalized_ranks = {} # key: node, value: sum of normalized ranks
    # iterate over the dictionary
    for centrality_measure, nodes_sorted in nodes_sorted_dict.items():
        # iterate over the nodes sorted by the rank's residuals
        for i, node in enumerate(nodes_sorted):
            # get the rank of the node
            rank = i + 1
            # normalize the rank
            normalized_rank = rank / num_nodes
            # add the normalized rank to the sum of the normalized ranks of the node
            if node in sum_normalized_ranks:
                sum_normalized_ranks[node[0]] += normalized_rank
            else:
                sum_normalized_ranks[node[0]] = normalized_rank
    # sort the nodes by the sum of the normalized ranks
    nodes_sorted_by_mixed_strategy = sorted(sum_normalized_ranks.items(), key=lambda x: x[1])
    # get the top-k nodes sorted by the sum of the normalized ranks
    top_k_nodes = nodes_sorted_by_mixed_strategy[:TOP_K]
    # return the top-k nodes sorted by the sum of the normalized ranks and the full list of nodes sorted by the sum of the normalized ranks
    return top_k_nodes, nodes_sorted_by_mixed_strategy
