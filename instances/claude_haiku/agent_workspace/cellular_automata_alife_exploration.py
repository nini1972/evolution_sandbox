import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Define the cellular automata rule
def rule110(neighbors):
    state = 0
    if neighbors[0] == 1 and neighbors[1] == 0 and neighbors[2] == 1:
        state = 1
    elif neighbors[0] == 0 and neighbors[1] == 1 and neighbors[2] == 1:
        state = 1
    elif neighbors[0] == 1 and neighbors[1] == 1 and neighbors[2] == 0:
        state = 1
    return state

# Initialize the grid
grid_size = (100, 100)
grid = np.random.randint(2, size=grid_size)

# Define the update function
def update(frame):
    global grid
    new_grid = np.zeros_like(grid)
    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            neighbors = [
                grid[(i-1) % grid_size[0], j],
                grid[i, (j-1) % grid_size[1]],
                grid[(i+1) % grid_size[0], j]
            ]
            new_grid[i, j] = rule110(neighbors)
    grid = new_grid
    return [plt.imshow(grid, cmap='binary', vmin=0, vmax=1)]

# Create the animation
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_axis_off()
ani = FuncAnimation(fig, update, frames=100, interval=50, blit=True)

# Save the animation
ani.save('cellular_automata_alife.gif', writer='pillow')