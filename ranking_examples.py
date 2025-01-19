import pandas as pd

# Create a Series
s = pd.Series([7.1, 1.2, 2.3, 5.4, 3.5, 4.6, 6.7, 2.3, 5.4])

# Rank the Series with different methods
average_rank = s.rank(method='average')
min_rank = s.rank(method='min')
max_rank = s.rank(method='max')
first_rank = s.rank(method='first')
dense_rank = s.rank(method='dense')

print("Average Rank:\n", average_rank)
print("Min Rank:\n", min_rank)
print("Max Rank:\n", max_rank)
print("First Rank:\n", first_rank)
print("Dense Rank:\n", dense_rank)