# Define a simple optimization problem
x0 = 0
x1 = 1
f = 2 * x0 + 3 * x1 - x0 * x1 - 1

# Print the results
print(f"Optimal value: {f}")
print(f"Optimal variables: [{x0}, {x1}]")