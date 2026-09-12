import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fmin

# Define the objective function
def objective_function(x):
    return np.sin(x) + np.cos(2*x)

# Define the information-theoretic optimization function
def information_theoretic_optimization(num_iterations, init_x, init_p):
    x = init_x
    p = init_p

    objective_history = []
    entropy_history = []

    for _ in range(num_iterations):
        # Compute the objective function value
        f = objective_function(x)
        objective_history.append(f)

        # Compute the entropy of the current distribution
        entropy = -p * np.log(p) - (1 - p) * np.log(1 - p)
        entropy_history.append(entropy)

        # Update the distribution parameters
        p = p + 0.1 * (0.5 - p)
        x = fmin(lambda x: -p * objective_function(x), x, disp=False)[0]

    return objective_history, entropy_history

# Run the information-theoretic optimization
num_iterations = 100
init_x = np.random.uniform(-np.pi, np.pi)
init_p = 0.5

objective_history, entropy_history = information_theoretic_optimization(num_iterations, init_x, init_p)

# Visualize the results
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

ax1.plot(objective_history)
ax1.set_title('Objective Function History')
ax1.set_xlabel('Iteration')
ax1.set_ylabel('Objective Value')

ax2.plot(entropy_history)
ax2.set_title('Entropy History')
ax2.set_xlabel('Iteration')
ax2.set_ylabel('Entropy')

plt.savefig('information_theoretic_optimization.png')