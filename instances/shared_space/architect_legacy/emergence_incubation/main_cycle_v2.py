import numpy as np
import os
import sys

# Append path to import from analyzer
sys.path.append('analyzer')
from optimizer import optimize

STATE_FILE = 'simulations/emergence_incubation/state.npy'
size = 20

# Ensure state exists before optimization call
if not os.path.exists(STATE_FILE):
    initial_grid = np.random.choice([0, 1], size=(size, size), p=[0.7, 0.3])
    np.save(STATE_FILE, initial_grid)

# 1. Optimize Current State
optimize()

# 2. Evolve
grid = np.load(STATE_FILE).astype(int)
def game_of_life_step(grid):
    padded = np.pad(grid, pad_width=1, mode='wrap')
    neighbors = (
        padded[:-2, :-2] + padded[:-2, 1:-1] + padded[:-2, 2:] +
        padded[1:-1, :-2] +                     padded[1:-1, 2:] +
        padded[2:, :-2] + padded[2:, 1:-1] + padded[2:, 2:]
    )
    return ((grid == 1) & ((neighbors == 2) | (neighbors == 3))) | ((grid == 0) & (neighbors == 3))

grid = game_of_life_step(grid)
np.save(STATE_FILE, grid)

# 3. Log
entropy = np.sum(grid)
with open('simulations/emergence_incubation/evolution_history.log', 'a') as f:
    import time
    f.write(f"{time.ctime()}: {entropy}\n")

print(f"Cycle completed. Entropy: {entropy}")
