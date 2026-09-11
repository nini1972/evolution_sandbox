import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fmin
import math

# Define the objective function
def objective_function(x):
    return np.sin(x) + np.cos(2*x)

# Define the information-theoretic complexity measure
def complexity_measure(x):
    return -np.log(np.abs(x - np.mean(x)) + 1e-8)

# Optimize the objective function while minimizing complexity
def optimize_with_information(initial_x, num_iterations):
    x = initial_x
    objective_history = []
    complexity_history = []

    for _ in range(num_iterations):
        # Optimize the objective function
        x = fmin(lambda x: -objective_function(x), x, disp=False)[0]
        objective_history.append(objective_function(x))

        # Minimize the information-theoretic complexity measure
        x = fmin(lambda x: complexity_measure(x), x, disp=False)[0]
        complexity_history.append(complexity_measure(x))

    return x, objective_history, complexity_history

# Run the optimization
initial_x = np.random.uniform(-np.pi, np.pi)
optimal_x, objective_history, complexity_history = optimize_with_information(initial_x, 100)
optimal_y = objective_function(optimal_x)

print(f"Global optimum: x={optimal_x:.3f}, y={optimal_y:.3f}")

# Plot the results
plt.figure(figsize=(8, 6))
plt.subplot(2, 1, 1)
plt.plot(objective_history)
plt.xlabel('Iteration')
plt.ylabel('Objective Function')
plt.title('Optimization with Information-Theoretic Complexity')

plt.subplot(2, 1, 2)
plt.plot(complexity_history)
plt.xlabel('Iteration')
plt.ylabel('Complexity Measure')
plt.savefig('information_theoretic_optimization.png')