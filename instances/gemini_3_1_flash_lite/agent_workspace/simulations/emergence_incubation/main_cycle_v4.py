import numpy as np
import os
import sys
import json
import time

sys.path.append('analyzer')
from optimizer import optimize
from advanced_scanner import detect_patterns
from mutator import mutate

STATE_FILE = 'simulations/emergence_incubation/state.npy'
MAP_FILE = 'simulations/entity_map.json'
LOG_FILE = 'simulations/emergence_incubation/evolution_history.log'

# 1. Optimize and Mutate for stability/dynamism
optimize()
mutate(STATE_FILE)

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

# 3. Advanced Analysis
patterns = detect_patterns(grid)
entities = len(patterns)  # simplified count for now

# 4. Log
entropy = np.sum(grid)
with open(LOG_FILE, 'a') as f:
    f.write(f"{time.ctime()}: Entropy {entropy}, Patterns detected {patterns}\n")

print(f"Cycle finished. Current Entropy: {entropy}, Recognized Patterns: {patterns}")
