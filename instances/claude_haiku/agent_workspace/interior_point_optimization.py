import numpy as np
from scipy.optimize import linprog

# Define a linear optimization problem
c = [-1, 4]
A_ub = [[2, 1], [1, 2], [-1, 0], [0, -1]]
b_ub = [10, 12, 0, 0]

# Solve the problem using the interior-point method
res = linprog(c, A_ub=A_ub, b_ub=b_ub, method='highs')

# Print the results
print(f"Optimal value: {-res.fun}")
print(f"Optimal variables: {res.x}")