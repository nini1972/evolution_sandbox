import numpy as np
import os

def mutate(state_file):
    grid = np.load(state_file)
    # Check for stagnation
    if np.sum(grid) < 50:
        # Increase complexity - add random noise to edges
        grid[np.random.randint(0, grid.shape[0], 10), np.random.randint(0, grid.shape[1], 10)] = 1
        print("Stagnation detected. System mutated.")
    np.save(state_file, grid)

if __name__ == "__main__":
    mutate('simulations/emergence_incubation/state.npy')
