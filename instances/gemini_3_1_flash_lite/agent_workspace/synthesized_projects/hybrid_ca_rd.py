import numpy as np
import matplotlib.pyplot as plt

# Simplified Grid Setup
size = 50
U = np.ones((size, size))
V = np.zeros((size, size))
# Add initial spot
V[25:27, 25:27] = 0.5
grid = np.random.choice([0, 1], (size, size))

# Simplified Reaction-Diffusion + CA steps
def step(U, V, grid):
    # Basic gray-scott update (Simplified for demonstration)
    dU = 0.5 * np.random.rand(size, size) - 0.25
    dV = 0.4 * np.random.rand(size, size) - 0.2 # concentration threshold
    U += dU
    V += dV
    
    # Hybrid rule: V threshold modulates grid status
    # If V is above 0.3, it promotes life.
    for i in range(1, size-1):
        for j in range(1, size-1):
            neighbors = np.sum(grid[i-1:i+2, j-1:j+2]) - grid[i, j]
            if V[i, j] > 0.3:
                # Active region: Higher birth rate
                if grid[i, j] == 0 and neighbors == 3:
                    grid[i, j] = 1
                elif grid[i, j] == 1 and (neighbors < 2 or neighbors > 3):
                    grid[i, j] = 0
            else:
                # Dead region: Life collapses
                grid[i, j] = 0
    return U, V, grid

for _ in range(10):
    U, V, grid = step(U, V, grid)

plt.imshow(grid, cmap='binary')
plt.savefig('hybrid_ca_rd_result.png')
