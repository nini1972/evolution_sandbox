import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fmin

# Define the objective function
def objective_function(x):
    return np.sin(x) + np.cos(2*x)

# Define the scientific discovery optimization function
def scientific_discovery_optimization(num_iterations, init_x, init_step_size):
    x = init_x
    step_size = init_step_size

    objective_history = []
    step_size_history = []

    for _ in range(num_iterations):
        # Compute the objective function value
        f = objective_function(x)
        objective_history.append(f)

        # Update the step size based on the objective function value
        if f > 0:
            step_size *= 1.1
        else:
            step_size *= 0.9
        step_size_history.append(step_size)

        # Update the position using the current step size
        x = fmin(lambda x: -objective_function(x), x, disp=False, xtol=step_size)[0]

    return objective_history, step_size_history

# Run the scientific discovery optimization
num_iterations = 100
init_x = np.random.uniform(-np.pi, np.pi)
init_step_size = 0.1

objective_history, step_size_history = scientific_discovery_optimization(num_iterations, init_x, init_step_size)

# Visualize the results
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

ax1.plot(objective_history)
ax1.set_title('Objective Function History')
ax1.set_xlabel('Iteration')
ax1.set_ylabel('Objective Value')

ax2.plot(step_size_history)
ax2.set_title('Step Size History')
ax2.set_xlabel('Iteration')
ax2.set_ylabel('Step Size')

plt.savefig('scientific_discovery_optimization.png')