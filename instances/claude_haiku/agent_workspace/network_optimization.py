import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from scipy.optimize import fmin

# Define the objective function
def objective_function(adjacency_matrix):
    G = nx.from_numpy_matrix(adjacency_matrix)
    return -nx.algebraic_connectivity(G)

# Define the network optimization problem
def optimize_network(initial_adjacency, num_iterations):
    adjacency = initial_adjacency.copy()
    objective_history = []

    for _ in range(num_iterations):
        # Optimize the network structure
        adjacency = fmin(lambda x: objective_function(x.reshape(n, n)), adjacency.flatten(), disp=False).reshape(n, n)
        objective_history.append(objective_function(adjacency))

    return adjacency, objective_history

# Set the network size
n = 10

# Initialize the network
initial_adjacency = np.random.randint(0, 2, size=(n, n))
initial_adjacency = (initial_adjacency + initial_adjacency.T) / 2  # Ensure symmetry

# Optimize the network
optimal_adjacency, objective_history = optimize_network(initial_adjacency, 100)

# Visualize the initial and optimal networks
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

G1 = nx.from_numpy_matrix(initial_adjacency)
nx.draw(G1, with_labels=True, ax=ax1)
ax1.set_title('Initial Network')

G2 = nx.from_numpy_matrix(optimal_adjacency)
nx.draw(G2, with_labels=True, ax=ax2)
ax2.set_title('Optimized Network')

plt.figure(figsize=(8, 6))
plt.plot(objective_history)
plt.xlabel('Iteration')
plt.ylabel('Algebraic Connectivity')
plt.title('Network Optimization')
plt.savefig('network_optimization.png')