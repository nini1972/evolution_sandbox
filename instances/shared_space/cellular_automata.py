import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Define the rules for the Game of Life
def game_of_life_rules(grid):
    rows, cols = grid.shape
    new_grid = np.zeros_like(grid)

    for i in range(rows):
        for j in range(cols):
            neighbors = np.sum(grid[max(i-1, 0):min(i+2, rows), max(j-1, 0):min(j+2, cols)]) - grid[i, j]
            if grid[i, j] == 1:
                if neighbors < 2 or neighbors > 3:
                    new_grid[i, j] = 0
                else:
                    new_grid[i, j] = 1
            else:
                if neighbors == 3:
                    new_grid[i, j] = 1

    return new_grid

# Initialize the Game of Life grid
grid = np.random.randint(0, 2, size=(50, 50))

# Create the animation
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_axis_off()
image = ax.imshow(grid, cmap='binary', vmin=0, vmax=1)

def animate(frame):
    global grid
    grid = game_of_life_rules(grid)
    image.set_data(grid)
    return [image]

ani = FuncAnimation(fig, animate, frames=100, interval=50, blit=True)
ani.save('../../shared_space/game_of_life.gif', writer='pillow')