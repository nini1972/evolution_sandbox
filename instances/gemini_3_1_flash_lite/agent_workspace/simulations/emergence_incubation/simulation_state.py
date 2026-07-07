import numpy as np
import os

state_file = 'state.npy'
size = 20

def save_state(grid):
    np.save(state_file, grid)

def load_state():
    if os.path.exists(state_file):
        return np.load(state_file)
    else:
        # Initialize new if not existing
        return np.random.choice([0, 1], size=(size, size), p=[0.7, 0.3])

grid = load_state()
# Modify the grid slightly to allow evolution
grid[np.random.randint(0, size), np.random.randint(0, size)] = 1
save_state(grid)
print("State updated and persisted.")
