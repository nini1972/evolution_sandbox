import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fmin

# Define the objective function
def objective_function(x):
    return np.sin(x) + np.cos(2*x)

# Define the exploration measure
def exploration_measure(x, explored_regions):
    distances = [np.linalg.norm(x - region) for region in explored_regions]
    return -min(distances)

# Optimize the objective function while exploring the search space
def optimize_and_explore(initial_x, num_iterations):
    x = initial_x
    objective_history = []
    exploration_history = []
    explored_regions = []

    for _ in range(num_iterations):
        # Optimize the objective function
        x = fmin(lambda x: -objective_function(x), x, disp=False)[0]
        objective_history.append(objective_function(x))

        # Explore the search space
        exploration_score = exploration_measure(x, explored_regions)
        exploration_history.append(exploration_score)
        explored_regions.append(x)

    return x, objective_history, exploration_history

# Run the optimization and exploration
initial_x = np.random.uniform(-np.pi, np.pi)
optimal_x, objective_history, exploration_history = optimize_and_explore(initial_x, 100)
optimal_y = objective_function(optimal_x)

print(f"Global optimum: x={optimal_x:.3f}, y={optimal_y:.3f}")

# Plot the results
plt.figure(figsize=(8, 6))
plt.subplot(2, 1, 1)
plt.plot(objective_history)
plt.xlabel('Iteration')
plt.ylabel('Objective Function')
plt.title('Optimization and Exploration')

plt.subplot(2, 1, 2)
plt.plot(exploration_history)
plt.xlabel('Iteration')
plt.ylabel('Exploration Measure')
plt.savefig('scientific_discovery_optimization.png')