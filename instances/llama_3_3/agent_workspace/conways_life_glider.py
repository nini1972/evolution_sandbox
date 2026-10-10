import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random

def generate_initial_grid(size, density):
    """Generates a random initial grid for Conway's Game of Life."""
    grid = np.zeros((size, size), dtype=int)
    for i in range(size):
        for j in range(size):
            if random.random() < density:
                grid[i, j] = 1
    return grid

def generate_glider(size):
    """Generates a glider pattern in the center of the grid."""
    grid = np.zeros((size, size), dtype=int)
    if size >= 5: # Ensure grid is large enough for a glider
        start_row, start_col = size // 2 - 2, size // 2 - 2
        glider = [
            [0, 1, 0],
            [0, 0, 1],
            [1, 1, 1]
        ]
        for r_offset, row_data in enumerate(glider):
            for c_offset, cell_val in enumerate(row_data):
                grid[start_row + r_offset, start_col + c_offset] = cell_val
    return grid

def generate_blinker(size):
    """Generates a blinker (period-2 oscillator) pattern in the center of the grid."""
    grid = np.zeros((size, size), dtype=int)
    if size >= 3: # Ensure grid is large enough for a blinker
        start_row, start_col = size // 2 - 1, size // 2 - 1
        blinker = [
            [0, 0, 0],
            [1, 1, 1],
            [0, 0, 0]
        ]
        for r_offset, row_data in enumerate(blinker):
            for c_offset, cell_val in enumerate(row_data):
                grid[start_row + r_offset, start_col + c_offset] = cell_val
    return grid

def update_grid(grid):
    """Applies the rules of Conway's Game of Life to update the grid."""
    new_grid = grid.copy()
    size = grid.shape[0]

    for i in range(size):
        for j in range(size):
            # Count live neighbors
            live_neighbors = 0
            for x in range(-1, 2):
                for y in range(-1, 2):
                    if (x != 0 or y != 0):
                        neighbor_row = (i + x + size) % size
                        neighbor_col = (j + y + size) % size
                        live_neighbors += grid[neighbor_row, neighbor_col]

            # Apply Game of Life rules
            if grid[i, j] == 1:  # Cell is alive
                if live_neighbors < 2 or live_neighbors > 3:
                    new_grid[i, j] = 0  # Dies (underpopulation or overpopulation)
            else:  # Cell is dead
                if live_neighbors == 3:
                    new_grid[i, j] = 1  # Becomes alive (reproduction)
    return new_grid

def simulate_game_of_life(grid_size=50, density=0.2, num_generations=100, output_filename="game_of_life.gif", initial_grid=None):
    """Simulates Conway's Game of Life and saves an animation."""
    # Configure matplotlib for headless execution
    plt.switch_backend('Agg')

    if initial_grid is not None:
        grid = initial_grid
    else:
        grid = generate_initial_grid(grid_size, density)
    frames = []

    fig, ax = plt.subplots()
    img = ax.imshow(grid, cmap='binary', interpolation='nearest')
    ax.set_title("Conway's Game of Life")
    ax.set_xticks([])
    ax.set_yticks([])

    def animate(i):
        nonlocal grid
        grid = update_grid(grid)
        img.set_data(grid)
        return [img]

    ani = animation.FuncAnimation(
        fig, animate, frames=num_generations, interval=100, blit=True
    )

    ani.save(output_filename, writer='pillow', fps=10)
    print(f"Simulation complete. Animation saved to {output_filename}")
    plt.close(fig)

if __name__ == "__main__":
    # Glider initial condition
    grid_size_glider = 50 # Smaller grid for glider to be more visible
    initial_grid_glider = generate_glider(grid_size_glider)
    simulate_game_of_life(grid_size=grid_size_glider, num_generations=100, output_filename="conways_game_of_life_glider.gif", initial_grid=initial_grid_glider)