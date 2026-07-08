import numpy as np
import os

# Threshold settings
MIN_THRESHOLD = 50
MAX_THRESHOLD = 300
STATE_FILE = 'simulations/emergence_incubation/state.npy'

def optimize():
    if not os.path.exists(STATE_FILE):
        return
    
    grid = np.load(STATE_FILE)
    entropy = np.sum(grid)
    
    if entropy < MIN_THRESHOLD:
        # Stimulate activity
        mask = np.random.rand(*grid.shape) > 0.8
        grid[mask] = 1
        print("Entropy critical low. Stimulation applied.")
    elif entropy > MAX_THRESHOLD:
        # Dampen activity
        mask = np.random.rand(*grid.shape) > 0.5
        grid[mask] = 0
        print("Entropy critical high. Damping applied.")
    else:
        print("System entropy within stable bounds.")
    
    np.save(STATE_FILE, grid)

if __name__ == '__main__':
    optimize()
