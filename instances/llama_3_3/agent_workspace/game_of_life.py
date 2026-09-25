
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os

def generate_initial_state(rows, cols, density):
    """
    Generates a random initial state for the Game of Life grid.
    """
    return np.random.choice([0, 1], size=(rows, cols), p=[1 - density, density])

def update_grid(grid):
    """
    Applies the Game of Life rules to update the grid for one generation.
    """
    rows, cols = grid.shape
    new_grid = np.copy(grid)

    for r in range(rows):
        for c in range(cols):
            # Count live neighbors
            live_neighbors = 0
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if (i != 0 or j != 0) and \
                       (0 <= r + i < rows) and \
                       (0 <= c + j < cols):
                        live_neighbors += grid[r + i, c + j]

            # Apply Game of Life rules
            if grid[r, c] == 1:  # Live cell
                if live_neighbors < 2 or live_neighbors > 3:
                    new_grid[r, c] = 0  # Underpopulation or overpopulation
            else:  # Dead cell
                if live_neighbors == 3:
                    new_grid[r, c] = 1  # Reproduction

    return new_grid

def simulate_game_of_life(rows, cols, density, generations, output_dir_npy="gol_output", output_dir_png="gol_frames_png"):
    """
    Simulates Conway's Game of Life, saves grid states as .npy and .png files.
    """
    grid = generate_initial_state(rows, cols, density)
    
    os.makedirs(output_dir_npy, exist_ok=True)
    os.makedirs(output_dir_png, exist_ok=True)

    fig, ax = plt.subplots()
    plt.axis('off')
    
    frames_to_save = [] # To store grid states for .npy and .png saving

    for i in range(generations):
        # Save current grid state as .npy
        npy_filename = os.path.join(output_dir_npy, f"gol_frame_{i:03d}.npy")
        np.save(npy_filename, grid)
        
        # Save current grid state as .png
        ax.clear()
        ax.imshow(grid, cmap='binary')
        ax.set_title(f"Generation: {i}")
        plt.axis('off')
        png_filename = os.path.join(output_dir_png, f"gol_frame_{i:03d}.png")
        plt.savefig(png_filename)
        
        frames_to_save.append(grid) # Though not directly used for animation saving in this setup, good to have

        grid = update_grid(grid)

    plt.close(fig)
    print(f"Saved {generations} frames as .npy files in {output_dir_npy}")
    print(f"Saved {generations} frames as .png files in {output_dir_png}")


if __name__ == "__main__":
    # Configure matplotlib for headless execution
    plt.switch_backend('Agg') 
    
    # Simulation parameters
    GRID_ROWS = 50
    GRID_COLS = 50
    INITIAL_DENSITY = 0.2  # Percentage of live cells
    NUM_GENERATIONS = 100
    
    simulate_game_of_life(GRID_ROWS, GRID_COLS, INITIAL_DENSITY, NUM_GENERATIONS)