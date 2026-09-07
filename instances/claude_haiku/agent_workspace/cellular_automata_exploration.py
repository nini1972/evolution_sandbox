import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Define the cellular automaton rules
def rule_110(state):
    new_state = np.zeros_like(state)
    new_state[1:-1] = (state[:-2] * state[1:-1] * (1 - state[2:])) | ((1 - state[:-2]) * state[1:-1] * state[2:])
    return new_state

# Initialize the grid
grid_size = 100
initial_state = np.random.randint(2, size=grid_size)

# Run the cellular automaton
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_xlim(0, grid_size)
ax.set_ylim(0, 100)
ax.set_xticks([])
ax.set_yticks([])
ax.set_aspect('equal')

img = ax.imshow(initial_state[np.newaxis, :], cmap='binary', animated=True)

def update(frame):
    global initial_state
    initial_state = rule_110(initial_state)
    img.set_data(initial_state[np.newaxis, :])
    return [img]

ani = animation.FuncAnimation(fig, update, frames=100, interval=50, blit=True)

plt.show()