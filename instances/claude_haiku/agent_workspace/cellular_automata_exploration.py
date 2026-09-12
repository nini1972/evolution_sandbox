import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import convolve

# Define the cellular automaton rule
def rule_30(state):
    # Rule 30 cellular automaton rule
    return (state[:-2] + state[1:-1] + state[2:]) % 2

# Initialize the cellular automaton grid
grid_size = (100, 100)
initial_state = np.zeros(grid_size, dtype=int)
initial_state[grid_size[0] // 2, 0] = 1  # Set a single active cell in the middle of the first row

# Evolve the cellular automaton
num_steps = 100
states = [initial_state]
for _ in range(num_steps):
    next_state = np.apply_along_axis(rule_30, axis=1, arr=states[-1])
    states.append(next_state)

# Visualize the evolution of the cellular automaton
fig, ax = plt.subplots(figsize=(8, 8))
ax.imshow(np.array(states), cmap='binary')
ax.set_title('Rule 30 Cellular Automaton')
ax.set_xlabel('Time')
ax.set_ylabel('Space')
plt.savefig('cellular_automata_exploration.png')