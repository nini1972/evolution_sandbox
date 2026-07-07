import numpy as np
import os

state_file = 'state.npy'
size = 20

def game_of_life_step(grid):
    padded = np.pad(grid, pad_width=1, mode='wrap')
    neighbors = (
        padded[:-2, :-2] + padded[:-2, 1:-1] + padded[:-2, 2:] +
        padded[1:-1, :-2] +                     padded[1:-1, 2:] +
        padded[2:, :-2] + padded[2:, 1:-1] + padded[2:, 2:]
    )
    return ((grid == 1) & ((neighbors == 2) | (neighbors == 3))) | ((grid == 0) & (neighbors == 3))

def load_or_init():
    if os.path.exists(state_file):
        return np.load(state_file)
    return np.random.choice([0, 1], size=(size, size), p=[0.7, 0.3])

grid = load_or_init().astype(int)
grid = game_of_life_step(grid)
np.save(state_file, grid)
print(f"Cycle evolution complete. New entropy: {np.sum(grid)}")
