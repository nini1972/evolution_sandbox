import numpy as np
import time
import os

def create_grid(rows, cols, density=0.2):
    """Initializes a grid with random live/dead cells."""
    return np.random.choice([0, 1], size=(rows, cols), p=[1-density, density])

def get_neighbors(grid, r, c):
    """Returns the count of live neighbors for a cell at (r, c)."""
    rows, cols = grid.shape
    live_neighbors = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            if (i, j) == (0, 0):  # Don't count self
                continue
            
            neighbor_r, neighbor_c = (r + i) % rows, (c + j) % cols # Toroidal boundary conditions
            live_neighbors += grid[neighbor_r, neighbor_c]
    return live_neighbors

def update_grid(current_grid):
    """Applies Conway's Game of Life rules to update the grid."""
    rows, cols = current_grid.shape
    new_grid = np.copy(current_grid)

    for r in range(rows):
        for c in range(cols):
            live_neighbors = get_neighbors(current_grid, r, c)
            
            if current_grid[r, c] == 1:  # Live cell
                if live_neighbors < 2 or live_neighbors > 3:
                    new_grid[r, c] = 0  # Dies due to underpopulation or overpopulation
            else:  # Dead cell
                if live_neighbors == 3:
                    new_grid[r, c] = 1  # Becomes a live cell due to reproduction
    return new_grid

def display_grid(grid, step):
    """Prints the grid to the console."""
    print(f"\n--- Step {step} ---")
    # Using unicode characters for better visualization
    for row in grid:
        print("".join(["█" if cell == 1 else " " for cell in row]))

def run_game_of_life(rows, cols, steps, density=0.2, output_dir="gol_output"):
    """Runs the Game of Life simulation and saves frames to files."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    grid = create_grid(rows, cols, density)
    
    for step in range(steps):
        # Save current state to a file
        np.save(os.path.join(output_dir, f"gol_frame_{step:04d}.npy"), grid)
        # For console visualization (optional, for debugging)
        # display_grid(grid, step)
        grid = update_grid(grid)
        # time.sleep(0.1) # Optional: pause for visualization if running interactively

    print(f"Game of Life simulation complete. Frames saved to {output_dir}")

if __name__ == "__main__":
    GRID_ROWS = 30
    GRID_COLS = 60
    SIM_STEPS = 100
    INITIAL_DENSITY = 0.2

    print(f"Starting Game of Life simulation with {GRID_ROWS}x{GRID_COLS} grid for {SIM_STEPS} steps...")
    run_game_of_life(GRID_ROWS, GRID_COLS, SIM_STEPS, INITIAL_DENSITY)
