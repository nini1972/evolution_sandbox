import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import convolve

# Define the Game of Life update rule
def game_of_life(state):
    # Count the number of neighbors for each cell
    neighbors = convolve(state, np.ones((3, 3)), mode='same', method='direct')

    # Apply the Game of Life rules
    next_state = np.where((state == 1) & (neighbors == 2) | (neighbors == 3), 1, 0)
    return next_state

# Initialize the cellular automaton grid
grid_size = (100, 100)
initial_state = np.random.randint(0, 2, size=grid_size)

# Evolve the cellular automaton
num_steps = 200
states = [initial_state]
for _ in range(num_steps):
    next_state = game_of_life(states[-1])
    states.append(next_state)

# Visualize the evolution of the cellular automaton
fig, ax = plt.subplots(figsize=(8, 8))
ax.imshow(np.array(states), cmap='binary')
ax.set_title('Game of Life Cellular Automaton')
ax.set_xlabel('Time')
ax.set_ylabel('Space')
plt.savefig('game_of_life_cellular_automaton.png')