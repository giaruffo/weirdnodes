from config import *
import concordance_check as cc
import create_rankings as cr
import net_perturbation as nper
import sorting_strategies as ss
import evaluation as ev
from scipy.stats import spearmanr
import networkx as nx

def weirdnodes(g0,g1):
    print("-----------------------------------")

    nodes_sorted_by_residuals = {}
    top_k_nodes = {}
    # set the centrality measures to be calculated
    for centrality_measure in CENTRALITY_MEASURES:
        # show the differences between the two graphs
        # print("Graph 0 and Graph 1 differences:")
        # print(nx.difference(g0, g1).edges(data=True))

        # rank the nodes by the given centrality
        print(f"Calculating {centrality_measure}, and ranking nodes accordingly...")
        cr.rank_nodes_by_centrality(g0, centrality_measure)
        cr.rank_nodes_by_centrality(g1, centrality_measure)

        # store the ranks of the nodes in a dictionary for both graphs
        ranks = {}
        ranks['g0'] = [g0.nodes[i][f'{centrality_measure}_rank'] for i in g0.nodes()]
        ranks['g1'] = [g1.nodes[i][f'{centrality_measure}_rank'] for i in g1.nodes()]

        # store the centrality sequence of the graphs 
        centralities_g0 = g0.nodes(data=centrality_measure)
        centralities_g1 = g1.nodes(data=centrality_measure)

        # plot graphs with the same layout and save them to files
        # print("Plotting graphs...")
        # nper.plot_graphs_comparison(g0, g1, centralities_g0, centralities_g1, centrality_measure)

        # Calculate the concordance between the two rankings
        print(f"Calculating concordance between the two rankings (by {centrality_measure})...")
        kendallSignal, kendall = cc.concordance_check(ranks['g0'], ranks['g1'])
        spearmanSignal, spearman = cc.concordance_check(ranks['g0'], ranks['g1'], spearmanr)

        # store the concordance results in a file in the working directory as defined in config.py
        concordance_file_path = os.path.join(WORKING_DIRECTORY+f'/rank_correlations', f"concordance_by{centrality_measure}.txt")
        with open(concordance_file_path, "w") as f:
            f.write(f"Kendall's tau: {kendall}\n")
            f.write(f"Spearman's rho: {spearman}\n")
            f.write(f"Kendall's tau signal: {kendallSignal}\n")
            f.write(f"Spearman's rho signal: {spearmanSignal}\n")

        if (kendall_lowerbound < kendall < kendall_upperbound and spearman_lowerbound < spearman < spearman_upperbound):
            # plot the ranked nodes comparison and get the top k nodes sorted by the 
            # absolute value of the residuals of the ranks
            print(f"Plotting ranked nodes (by {centrality_measure}) comparison...")
            top_k_nodes[centrality_measure], nodes_sorted_by_residuals[centrality_measure] = cr.plot_ranked_nodes_comparison(g1, ranks['g0'], ranks['g1'], centrality_measure)

            evaluation_bloc(g1, top_k_nodes[centrality_measure], centrality_measure)
        
        print("-----------------------------------")

    # mixing all the sorted nodes by residuals in one list
    top_k_nodes_sorted_by_summation_strategy, _ = ss.rank_nodes_by_summation_strategy(nodes_sorted_by_residuals)
    top_k_nodes_sorted_by_strict_summation_strategy, _ = ss.rank_nodes_by_summation_strategy(top_k_nodes)

    evaluation_bloc(g1, top_k_nodes_sorted_by_summation_strategy, 'summation_strategy')
    evaluation_bloc(g1, top_k_nodes_sorted_by_strict_summation_strategy, 'strict_summation_strategy')

    # store graphs in files in the working directory as defined in config.py
    print("Storing graphs in gml files...")
    nx.write_gml(g0, os.path.join(WORKING_DIRECTORY+'/graphs', 'g0.gml'))
    nx.write_gml(g1, os.path.join(WORKING_DIRECTORY+'/graphs', 'g1.gml'))

    # store nodes ranks and other attributes in files in the working directory as defined in config.py as csv files
    print("Storing nodes ranks and other attributes in csv files...")
    for graph_name in ['g0', 'g1']:
        cr.store_nodes_ranks(locals()[graph_name], graph_name, CENTRALITY_MEASURES)

    # store graphs' basic metrics in a file under WORKING_DIRECTORY+'/graphs'
    print("Storing graphs' basic metrics in a file...")
    with open(os.path.join(WORKING_DIRECTORY+'/graphs', 'graphs_metrics.txt'), 'w') as f:
        for graph_name in ['g0', 'g1']:
            g = locals()[graph_name]
            nper.store_graph_metrics_infile(f, g, graph_name)

    # store degree, indegree, outdegree, strength, in_strength, out_strength, and weight distributions in a file under WORKING_DIRECTORY+'/plots'
    print("Storing degree, indegree, outdegree, strength, in_strength, out_strength, and weight distributions in a file...")
    for graph_name in ['g0', 'g1']:
        g = locals()[graph_name]
        nper.plot_graph_distributions(g, graph_name)
    print("Graphs' degree/strength distributions saved.") 

    print("Done.")


def evaluation_bloc(g, top_k_nodes, strategy):
    # store the top k nodes in a file in the working directory as defined in config.py
    print(f"Storing top k nodes (sorted by the mixed strategy in a file...")
    ev.store_top_k_nodes_in_file(g, top_k_nodes, strategy)

    # calculate precision, recall, average precision and mean average precision at k, for k = 1,..., 30
    # using function in evaluation.py
    print(f"Calculating evaluation results (strategy: {strategy})...")
    precisions, recalls, avg_precisions = ev.evaluate_results(g, top_k_nodes)

    # store and plot the results in a file in the working directory as defined in config.py
    ev.store_and_plot_evaluation_results(strategy, precisions, recalls, avg_precisions)

    # save evaluation summary in a latex file
    ev.create_latex_tabular(strategy, precisions, recalls, avg_precisions)