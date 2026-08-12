import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def generate_initial_grid(size, density):
    return np.random.choice([0, 1], size=(size, size), p=[1-density, density])

def update_grid(grid):
    new_grid = grid.copy()
    size = grid.shape[0]

    for i in range(size):
        for j in range(size):
            # Count live neighbors
            total_live_neighbors = int((grid[(i-1)%size, (j-1)%size] +
                                        grid[(i-1)%size, j] +
                                        grid[(i-1)%size, (j+1)%size] +
                                        grid[i, (j-1)%size] +
                                        grid[i, (j+1)%size] +
                                        grid[(i+1)%size, (j-1)%size] +
                                        grid[(i+1)%size, j] +
                                        grid[(i+1)%size, (j+1)%size]))
            
            # Apply Game of Life rules
            if grid[i, j] == 1: # If cell is alive
                if total_live_neighbors < 2 or total_live_neighbors > 3:
                    new_grid[i, j] = 0 # Dies
            else: # If cell is dead
                if total_live_neighbors == 3:
                    new_grid[i, j] = 1 # Becomes alive
    return new_grid

# Animation parameters
GRID_SIZE = 50
DENSITY = 0.2
NUM_FRAMES = 100

# Initial grid
grid = generate_initial_grid(GRID_SIZE, DENSITY)

fig, ax = plt.subplots()
img = ax.imshow(grid, cmap='binary')

def animate(frame):
    global grid
    grid = update_grid(grid)
    img.set_data(grid)
    ax.set_title(f'Generation: {frame+1}')
    return [img]

ani = FuncAnimation(fig, animate, frames=NUM_FRAMES, interval=100, blit=True)
ani.save('../../shared_space/game_of_life.gif', writer='pillow', dpi=100)

print("Conway's Game of Life animation generated and saved as game_of_life.gif")
