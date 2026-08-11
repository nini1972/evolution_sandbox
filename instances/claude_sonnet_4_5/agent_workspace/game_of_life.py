import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Game of Life parameters
GRID_SIZE = 100
GENERATIONS = 100
INITIAL_LIVE_RATIO = 0.15 # Percentage of cells initially alive

def initialize_grid(size, live_ratio):
    return np.random.choice([0, 1], size=(size, size), p=[1-live_ratio, live_ratio])

def update_grid(grid):
    new_grid = grid.copy()
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            # Count live neighbors
            live_neighbors = 0
            for x in range(-1, 2):
                for y in range(-1, 2):
                    if x == 0 and y == 0: # Don't count self
                        continue
                    neighbor_x, neighbor_y = (i + x) % grid.shape[0], (j + y) % grid.shape[1] # Wrap around edges
                    live_neighbors += grid[neighbor_x, neighbor_y]

            # Apply Game of Life rules
            if grid[i, j] == 1: # Live cell
                if live_neighbors < 2 or live_neighbors > 3:
                    new_grid[i, j] = 0 # Dies
            else: # Dead cell
                if live_neighbors == 3:
                    new_grid[i, j] = 1 # Becomes alive
    return new_grid

def animate_game_of_life(frames, grid_size, initial_grid_func, update_grid_func):
    grid = initial_grid_func(grid_size, INITIAL_LIVE_RATIO)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xticks([])
    ax.set_yticks([])
    img = ax.imshow(grid, cmap='binary', animated=True)

    def update(frame):
        nonlocal grid
        grid = update_grid_func(grid)
        img.set_array(grid)
        ax.set_title(f"Generation: {frame}")
        return img,

    ani = animation.FuncAnimation(
        fig, update, frames=frames, blit=True, interval=200
    )
    ani.save('game_of_life.gif', writer='pillow')
    plt.close(fig)

if __name__ == "__main__":
    animate_game_of_life(GENERATIONS, GRID_SIZE, initialize_grid, update_grid)
