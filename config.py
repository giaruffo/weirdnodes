import os
from datetime import datetime
import random

# Initialize the working directory where output files are stored
WORKING_DIRECTORY = os.path.join(os.getcwd(), datetime.now().strftime("%Y%m%d_%H%M%S"))
os.makedirs(WORKING_DIRECTORY, exist_ok=True)

# Number of nodes in the original graph
NUM_NODES = 200

# Number of links in the original graph
NUM_LINKS = 3000

# Degree sequence for setting up the configuration model to create a random graph
DEGREE_SEQUENCE = [random.randint(1, 10) for _ in range(NUM_NODES)]

# Number of nodes to be perturbated
NUM_NODES_TO_PERTURB = 10

# Add a list of centrality measures to be calculated
CENTRALITY_MEASURES = ["degree", "strength", "betweenness", "closeness", "eigenvector", "pagerank", "hits_hubs", "hits_authorities",
                       "indegree", "outdegree", "instrength", "outstrength"]

# Set the minimum weight for the links
MIN_WEIGHT = .1

# Set the min and max fractions of outgoing edges to be perturbed
OUT_EDGE_MIN_FACTOR, OUT_EDGE_MAX_FACTOR = 0.1, 0.5

# Set the min and max fractions of incoming edges to be perturbed
IN_EDGE_MIN_FACTOR, IN_EDGE_MAX_FACTOR = 0.1, 0.5

# set the min and max factors to decrease the links' weights of ghost nodes 
GHOST_MIN_FACTOR, GHOST_MAX_FACTOR  = 0.5, 1

# set the min and max factors to increase the links' weights of mushroom nodes
MUSHROOM_MIN_FACTOR, MUSHROOM_MAX_FACTOR = 5, 10

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
    config_file.write(f"Degree Sequence: {DEGREE_SEQUENCE}\n")
    config_file.write(f"Number of Nodes to Perturb: {NUM_NODES_TO_PERTURB}\n")

print(f"Configuration initialized and saved to {config_file_path}")