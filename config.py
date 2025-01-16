import os
from datetime import datetime
import random

# Initialize the working directory where output files are stored
working_directory = os.path.join(os.getcwd(), datetime.now().strftime("%Y%m%d_%H%M%S"))
os.makedirs(working_directory, exist_ok=True)

# Number of nodes in the original graph
num_nodes = 200

# Number of links in the original graph
num_links = 3000

# Degree sequence for setting up the configuration model to create a random graph
degree_sequence = [random.randint(1, 10) for _ in range(num_nodes)]

# Number of nodes to be perturbated
num_nodes_to_perturb = 10

# Add a list of centrality measures to be calculated
centrality_measures = ["degree", "strength", "betweenness", "closeness", "eigenvector", "pagerank", "hits_hubs", "hits_authorities",
                       "indegree", "outdegree", "instrength", "outstrength"]

# Save the configuration to a file
config_file_path = os.path.join(working_directory, "config.txt")
with open(config_file_path, "w") as config_file:
    config_file.write(f"Working Directory: {working_directory}\n")
    config_file.write(f"Number of Nodes: {num_nodes}\n")
    config_file.write(f"Number of Links: {num_links}\n")
    config_file.write(f"Degree Sequence: {degree_sequence}\n")
    config_file.write(f"Number of Nodes to Perturb: {num_nodes_to_perturb}\n")

print(f"Configuration initialized and saved to {config_file_path}")