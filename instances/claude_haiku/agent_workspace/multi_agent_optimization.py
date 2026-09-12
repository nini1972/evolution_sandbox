import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fmin

# Define the objective function for a single agent
def objective_function(x, agent_id):
    return np.sin(x) + np.cos(2*x) + 0.1 * agent_id * x

# Define the multi-agent optimization function
def multi_agent_optimization(num_agents, num_iterations):
    # Initialize agent positions randomly
    agent_positions = np.random.uniform(-np.pi, np.pi, size=num_agents)

    # Optimize the objective function for each agent
    objective_history = []
    for _ in range(num_iterations):
        for i in range(num_agents):
            agent_positions[i] = fmin(lambda x: -objective_function(x, i), agent_positions[i], disp=False)[0]
        objective_history.append([objective_function(pos, i) for i, pos in enumerate(agent_positions)])

    return agent_positions, objective_history

# Run the multi-agent optimization
num_agents = 5
num_iterations = 100
agent_positions, objective_history = multi_agent_optimization(num_agents, num_iterations)

# Visualize the results
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

ax1.plot(objective_history)
ax1.set_title('Objective Function History')
ax1.set_xlabel('Iteration')
ax1.set_ylabel('Objective Value')

ax2.plot(agent_positions.T)
ax2.set_title('Agent Positions')
ax2.set_xlabel('Iteration')
ax2.set_ylabel('Position')

plt.savefig('multi_agent_optimization.png')