import numpy as np

# Define a simple optimization problem
n = 2
cost_operator = np.array([[2, -1], [-1, 3]])
offset = -1

# Find the optimal solution
optimal_state = [0, 0]
optimal_value = np.dot(np.dot(optimal_state, cost_operator), optimal_state.T) + offset

# Print the results
print(f"Optimal value: {optimal_value}")
print(f"Optimal variables: {optimal_state}")