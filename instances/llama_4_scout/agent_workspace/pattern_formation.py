import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def simulate_pattern_formation(grid_size, iterations):
    grid = np.random.rand(grid_size, grid_size)

    for _ in range(iterations):
        new_grid = np.copy(grid)
        for i in range(grid_size):
            for j in range(grid_size):
                neighbors = []
                if i > 0:
                    neighbors.append(grid[i-1, j])
                if i < grid_size - 1:
                    neighbors.append(grid[i+1, j])
                if j > 0:
                    neighbors.append(grid[i, j-1])
                if j < grid_size - 1:
                    neighbors.append(grid[i, j+1])
                new_grid[i, j] += 0.1 * (np.mean(neighbors) - grid[i, j])
        grid = new_grid

    return grid

grid_sizes = [50, 100, 200]
iterations = [50, 100, 200]

for grid_size in grid_sizes:
    for iteration in iterations:
        grid = simulate_pattern_formation(grid_size, iteration)
        plt.imshow(grid, cmap='viridis')
        plt.savefig(f'pattern_formation_grid_size_{grid_size}_iterations_{iteration}.png')
        plt.close()
