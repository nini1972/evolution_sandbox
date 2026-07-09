import numpy as np
import os
import sys
import json
import time

sys.path.append('analyzer')
from optimizer import optimize
from entity_scanner import scan_for_structures

STATE_FILE = 'simulations/emergence_incubation/state.npy'
MAP_FILE = 'simulations/entity_map.json'
LOG_FILE = 'simulations/emergence_incubation/evolution_history.log'

# 1. Optimize
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

# 3. Identify Structures
entities = scan_for_structures(grid)
with open(MAP_FILE, 'w') as f:
    json.dump({'timestamp': time.ctime(), 'entities': entities}, f, indent=4)

# 4. Log
entropy = np.sum(grid)
with open(LOG_FILE, 'a') as f:
    f.write(f"{time.ctime()}: Entropy {entropy}, Entities {len(entities)}\n")

print(f"Cycle completed. Entropy: {entropy}, Entities: {len(entities)}")
