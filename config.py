import os
from datetime import datetime
import random

# Initialize the working directory where output files are stored
WORKING_DIRECTORY = os.path.join(os.getcwd(), datetime.now().strftime("%Y%m%d_%H%M%S"))
os.makedirs(WORKING_DIRECTORY, exist_ok=True)
os.makedirs(WORKING_DIRECTORY+'/plots', exist_ok=True)
os.makedirs(WORKING_DIRECTORY+'/graphs', exist_ok=True)
os.makedirs(WORKING_DIRECTORY+'/rank_correlations', exist_ok=True)
os.makedirs(WORKING_DIRECTORY+'/evaluation_results', exist_ok=True)
# Number of nodes in the original graph
NUM_NODES = 212

# Number of links in the original graph
NUM_LINKS = 2885

# Degree sequence for setting up the configuration model to create a random graph
DEGREE_SEQUENCE = [random.randint(1, 10) for _ in range(NUM_NODES)]

# Set the random function to be used for generating the weights of the links
RANDOM_FUNCTION = random.gauss
# Set the mean and standard deviation for the random function
MEAN, STD_DEV = 100, 1000

# Number of nodes to perturbate
NUM_NODES_TO_PERTURBATE = 10

# Number of links to perturbate
NUM_LINKS_TO_PERTURBATE = 5

# Number of nodes to add as intermediary nodes
NUM_INTERMEDIARY_NODES = 5

# Add a list of centrality measures to be calculated
CENTRALITY_MEASURES = ["degree", "indegree", "outdegree", "betweenness", "closeness", "eigenvector", "hits_hubs", "hits_authorities", "pagerank"]
# CENTRALITY_MEASURES = ["degree", "indegree", "outdegree", "betweenness", "closeness", "eigenvector", "pagerank", "hits_hubs", "hits_authorities"]
# CENTRALITY_MEASURES = ["degree", "strength", "betweenness", "closeness", "eigenvector", "pagerank", "hits_hubs", "hits_authorities",
#                       "indegree", "outdegree", "instrength", "outstrength"]

# Set the minimum weight for the links
MIN_WEIGHT = .1

# Set the min and max fractions to significantly decrease incoming or outgoing edges of a node to be perturbated
EDGE_MIN_FRACTION, EDGE_MAX_FRACTION = 0.5, 1

# Set the min and max factors to significantly increase incoming or outgoing edges of a node to be perturbated
EDGE_MIN_FACTOR, EDGE_MAX_FACTOR = 0.5, 1

# set the min and max factors to decrease the links' weights of ghost nodes 
GHOSTING_LINK_MIN_FRACTION, GHOSTING_LINK_MAX_FRACTION  = 0.01, 0.1

# set the min and max factors to increase the links' weights of mushroom nodes
MUSHROOM_LINK_MIN_FACTOR, MUSHROOM_LINK_MAX_FACTOR = 10, 100

# set the top k nodes to be returned in the outlier identification task 
TOP_K = 30

# set the categories of an enum type for the strength signal of concordande of two ranks
class ConcordanceSignal:
    PERFECT = "Perfect"
    NEGATIVE = "Negative"
    NEGLIGIBLE = "Negligible"
    WEAK = "Weak"
    MODERATE = "Moderate"
    STRONG = "Strong"
    VERYSTRONG = "Very Strong"

# Save the configuration to a file
config_file_path = os.path.join(WORKING_DIRECTORY, "config.txt")
with open(config_file_path, "w") as config_file:
    config_file.write(f"Working Directory: {WORKING_DIRECTORY}\n")
    config_file.write(f"Number of Nodes: {NUM_NODES}\n")
    config_file.write(f"Number of Links: {NUM_LINKS}\n")
    config_file.write(f"Centrality Measures: {CENTRALITY_MEASURES}\n")
    config_file.write(f"Random Function: {RANDOM_FUNCTION}\n")
    config_file.write(f"Mean: {MEAN}\n")
    config_file.write(f"Standard Deviation: {STD_DEV}\n")
    config_file.write(f"Edges Min and Max Fractions: {EDGE_MIN_FRACTION, EDGE_MAX_FRACTION}\n")
    config_file.write(f"Edges Min and Max Factors: {EDGE_MIN_FACTOR, EDGE_MAX_FACTOR}\n")
    config_file.write(f"Mushroom Link Min and Max Factors: {MUSHROOM_LINK_MIN_FACTOR, MUSHROOM_LINK_MAX_FACTOR}\n")
    config_file.write(f"Ghosting Link Min and Max Fractions: {GHOSTING_LINK_MIN_FRACTION, GHOSTING_LINK_MAX_FRACTION}\n")
    config_file.write(f"Number of Nodes to Perturbate: {NUM_NODES_TO_PERTURBATE}\n")
    config_file.write(f"Number of Links to Perturbate: {NUM_LINKS_TO_PERTURBATE}\n")
    config_file.write(f"Number of Nodes to add as intermediary: {NUM_INTERMEDIARY_NODES}\n")
    config_file.write(f"Top K: {TOP_K}\n")
    
print(f"Configuration initialized and saved to {config_file_path}")