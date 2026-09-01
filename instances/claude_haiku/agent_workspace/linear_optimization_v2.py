from itertools import product

# Define a simple linear optimization problem
c = [-1, 4]
A = [[2, 1], [1, 2], [-1, 0], [0, -1]]
b = [10, 12, 0, 0]

# Exhaustively search for the optimal solution
optimal_value = float('-inf')
optimal_variables = None
for x0, x1 in product(range(11), range(13)):
    if all(a[0] * x0 + a[1] * x1 <= b for a, b in zip(A, b)):
        f = c[0] * x0 + c[1] * x1
        if f > optimal_value:
            optimal_value = f
            optimal_variables = [x0, x1]

# Print the results
print(f"Optimal value: {optimal_value}")
print(f"Optimal variables: {optimal_variables}")