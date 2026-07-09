import numpy as np

def game_of_life_step(grid):
    # Simple Conway's Game of Life logic
    padded = np.pad(grid, pad_width=1, mode='wrap')
    neighbors = (
        padded[:-2, :-2] + padded[:-2, 1:-1] + padded[:-2, 2:] +
        padded[1:-1, :-2] +                     padded[1:-1, 2:] +
        padded[2:, :-2] + padded[2:, 1:-1] + padded[2:, 2:]
    )
    return ((grid == 1) & ((neighbors == 2) | (neighbors == 3))) | ((grid == 0) & (neighbors == 3))

# Initialize a random state
size = 20
grid = np.random.choice([0, 1], size=(size, size))
new_grid = game_of_life_step(grid.astype(int))

print(f"Simulation step executed. Population density: {np.mean(new_grid):.2f}")
