import numpy as np

def game_of_life_step(grid):
    padded = np.pad(grid, pad_width=1, mode='wrap')
    neighbors = (
        padded[:-2, :-2] + padded[:-2, 1:-1] + padded[:-2, 2:] +
        padded[1:-1, :-2] +                     padded[1:-1, 2:] +
        padded[2:, :-2] + padded[2:, 1:-1] + padded[2:, 2:]
    )
    return ((grid == 1) & ((neighbors == 2) | (neighbors == 3))) | ((grid == 0) & (neighbors == 3))

size = 20
grid = np.random.choice([0, 1], size=(size, size), p=[0.7, 0.3])
history = []

for _ in range(10):
    grid = game_of_life_step(grid.astype(int))
    history.append(np.mean(grid))

import matplotlib.pyplot as plt
plt.plot(history)
plt.title("Simulation Density Evolution")
plt.savefig('simulations/emergence_incubation/density_evolution.png')
print("Simulation completed, density plot saved.")
