import numpy as np
from scipy.optimize import linprog

# Define a simple linear optimization problem
c = [-1, 4]
A = [[2, 1], [1, 2], [-1, 0], [0, -1]]
b = [10, 12, 0, 0]

# Solve the linear optimization problem
res = linprog(c, A_ub=A, b_ub=b)

# Print the results
print(f"Optimal value: {-res.fun}")
print(f"Optimal variables: {res.x}")