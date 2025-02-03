import networkx as nx
import pandas as pd
from globals import *
from outliers_detection_proc import weirdnodes

edgelist0 = '' # first edgelist's filename here
edgelist1 = '' # second edgelist's filename here
path = 'data' # path to the folder containing the edgelists and the labeled anomalies file

def add_node_type(g):

    # read the labeled anomalies from the file
    labeled_anomalies = []
    with open(os.path.join(path, 'labeled_anomalies.txt'), 'r') as f:
        for line in f:
            labeled_anomalies.append(int(line.strip()))

    for node in g.nodes:
        if node not in labeled_anomalies:
            g.nodes[node]['type'] = 'normal'
        else:
            g.nodes[node]['type'] = 'abnormal'
    return g

def run():
    # create graphs from edgelists 
    df0 = pd.read_csv(edgelist0)
    df1 = pd.read_csv(edgelist1)

    print('renaming columns...')
    df0 = df0.rename(columns={'count': 'weight'})
    df1 = df1.rename(columns={'count': 'weight'})

    print('creating the graphs...')
    g0 = nx.from_pandas_edgelist(df0, edge_attr='weight', create_using=nx.DiGraph())
    g1 = nx.from_pandas_edgelist(df1, edge_attr='weight', create_using=nx.DiGraph())

    print('Adding types to nodes...')
    g0 = add_node_type(g0)
    g1 = add_node_type(g1)

    print('Add nodes to both graphs...')
    g0.add_nodes_from((node, g1.nodes[node]) for node in g1.nodes)
    g1.add_nodes_from((node, g0.nodes[node]) for node in g0.nodes)

    print('Map nodes names...')
    all_nodes = list(set(g1.nodes).union(set(g0.nodes)))
    node_mapping = {name: i for i, name in enumerate(all_nodes)}
    g0 = nx.relabel_nodes(g0, node_mapping)
    g1 = nx.relabel_nodes(g1, node_mapping)
    mapping_df = pd.DataFrame(list(node_mapping.items()), columns=["Original_Name", "Integer_ID"])
    mapping_df.to_csv(os.path.join(path, 'nodes_mapping.csv'), index=False)
    
    weirdnodes(g0, g1)
