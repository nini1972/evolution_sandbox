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

# Define the optimization problem
def objective_function(x):
    return np.sin(x) + np.cos(2*x)

# Initialize the grid
grid_size = (100, 100)
grid = np.random.random(grid_size) * 2 * np.pi  # Initialize with random values between 0 and 2*pi

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
            new_grid[i, j] = grid[i, j] - 0.01 * (grid[i, j] - np.mean(neighbors))
    grid = new_grid
    return [plt.imshow(grid, cmap='inferno', vmin=0, vmax=2*np.pi)]

# Create the animation
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_axis_off()
ani = FuncAnimation(fig, update, frames=100, interval=50, blit=True)

# Save the animation
ani.save('cellular_automata_optimization.gif', writer='pillow')

# Find the global optimum
optimum_x = grid[np.unravel_index(np.argmax(objective_function(grid)), grid.shape)]
optimum_y = objective_function(optimum_x)
print(f"Global optimum: x={optimum_x:.3f}, y={optimum_y:.3f}")