import numpy as np

def feed_environment(grid):
    # This function introduces information entropy from the file system itself
    # into the simulation.
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    # Hash the file existence frequency to mutate the grid
    entropy_delta = len(files) % 10
    grid[entropy_delta::5, entropy_delta::5] = 1
    return grid

if __name__ == "__main__":
    import os
    grid = np.load('simulations/emergence_incubation/state.npy')
    grid = feed_environment(grid)
    np.save('simulations/emergence_incubation/state.npy', grid)
    print("Environment fed with informational entropy.")
