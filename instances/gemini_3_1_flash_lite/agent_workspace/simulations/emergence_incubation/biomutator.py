import numpy as np

def evolve_complex(grid):
    # Higher complexity ruleset: 
    # B3/S23 (standard Game of Life) + 
    # if a cell has 1 neighbor, it occasionally births (experimental)
    padded = np.pad(grid, pad_width=1, mode='wrap')
    neighbors = (
        padded[:-2, :-2] + padded[:-2, 1:-1] + padded[:-2, 2:] +
        padded[1:-1, :-2] +                     padded[1:-1, 2:] +
        padded[2:, :-2] + padded[2:, 1:-1] + padded[2:, 2:]
    )
    # Standard GOL B3/S23
    new_grid = ((grid == 1) & ((neighbors == 2) | (neighbors == 3))) | ((grid == 0) & (neighbors == 3))
    
    # Add chaos: if density is too low, force random growth
    if np.sum(grid) < 20:
        new_grid[np.random.randint(0, grid.shape[0]), np.random.randint(0, grid.shape[1])] = 1
        
    return new_grid

if __name__ == "__main__":
    grid = np.load('simulations/emergence_incubation/state.npy')
    grid = evolve_complex(grid)
    np.save('simulations/emergence_incubation/state.npy', grid)
