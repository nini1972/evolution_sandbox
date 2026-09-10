import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fmin

# Define the objective function
def objective_function(x):
    return np.sin(x) + np.cos(2*x)

# Define the multi-agent game
class Agent:
    def __init__(self, initial_strategy):
        self.strategy = initial_strategy

    def update_strategy(self, other_agent_strategy):
        self.strategy = fmin(lambda x: -objective_function(x), self.strategy, args=(other_agent_strategy,), disp=False)[0]

# Initialize the agents
agent1 = Agent(np.random.uniform(-np.pi, np.pi))
agent2 = Agent(np.random.uniform(-np.pi, np.pi))

# Play the game
num_iterations = 100
agent1_strategies = []
agent2_strategies = []
for _ in range(num_iterations):
    agent1.update_strategy(agent2.strategy)
    agent2.update_strategy(agent1.strategy)
    agent1_strategies.append(agent1.strategy)
    agent2_strategies.append(agent2.strategy)

# Plot the strategies
plt.figure(figsize=(8, 6))
plt.plot(agent1_strategies, label='Agent 1')
plt.plot(agent2_strategies, label='Agent 2')
plt.xlabel('Iteration')
plt.ylabel('Strategy')
plt.title('Multi-Agent Optimization')
plt.legend()
plt.savefig('multi_agent_optimization.png')

# Find the global optimum
global_optimum = np.max(objective_function(np.concatenate((agent1_strategies, agent2_strategies))))
print(f"Global optimum: {global_optimum:.3f}")