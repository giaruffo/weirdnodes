from scipy.stats import rankdata, spearmanr

# function that takes two lists of values and calculates the rank correlations between them

def rank_correlation(list1, list2):
    # calculate the rank of each value in the lists
    rank1 = rankdata(list1)
    rank2 = rankdata(list2)
    # calculate the rank correlation
    correlation = spearmanr(rank1, rank2)
    return correlation  

# test the function
list1 = [1, 2, 3, 4, 5]
list2 = [1, 3, 2, 5, 4]
correlation = rank_correlation(list1, list2)
print(correlation)

