"""Randomly generate two tables, named alpha and beta"""

import pandas as pd
from numpy.random import rand

num_rows = 13
num_cols_A = 3
num_cols_B = 5

alpha = pd.DataFrame(rand(num_rows, num_cols_A), columns=['A','B','C'])
beta = pd.DataFrame(rand(num_rows, num_cols_B), columns=['D','E','F','G','H'])
alpha.to_csv('alpha.csv', index=False)
beta.to_csv('beta.csv', index=False)
