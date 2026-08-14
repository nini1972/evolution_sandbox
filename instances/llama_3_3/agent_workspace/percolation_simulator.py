import numpy as np
import matplotlib.pyplot as plt
from collections import deque

# Simulation parameters
GRID_SIZE = 50
OCCUPATION_PROBABILITY = 0.59  # Critical probability for 2D square lattice is approx 0.59275

# Generate the grid
grid = np.random.rand(GRID_SIZE, GRID_SIZE) < OCCUPATION_PROBABILITY

# Custom BFS-based connected component labeling
def find_largest_cluster(grid):
    rows, cols = grid.shape
    visited = np.zeros_like(grid, dtype=bool)
    largest_cluster_mask = np.zeros_like(grid, dtype=bool)
    max_cluster_size = 0

    for r in range(rows):
        for c in range(cols):
            if grid[r, c] and not visited[r, c]:
                current_cluster_mask = np.zeros_like(grid, dtype=bool)
                current_cluster_size = 0
                q = deque([(r, c)])
                visited[r, c] = True

                while q:
                    curr_r, curr_c = q.popleft()
                    current_cluster_mask[curr_r, curr_c] = True
                    current_cluster_size += 1

                    # Explore neighbors (up, down, left, right)
                    for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        nr, nc = curr_r + dr, curr_c + dc

                        if 0 <= nr < rows and 0 <= nc < cols and \
                           grid[nr, nc] and not visited[nr, nc]:
                            visited[nr, nc] = True
                            q.append((nr, nc))

                if current_cluster_size > max_cluster_size:
                    max_cluster_size = current_cluster_size
                    largest_cluster_mask = current_cluster_mask
    return largest_cluster_mask

largest_cluster_mask = find_largest_cluster(grid)

# Visualization
fig, ax = plt.subplots(figsize=(8, 8))

# Display the grid (non-percolated cells in white, percolated in light gray)
ax.imshow(~grid, cmap='Greys', origin='lower', alpha=0.5) # Background for non-percolated
ax.imshow(grid, cmap='Greys', origin='lower', alpha=0.9)

# Overlay the largest cluster in a different color
ax.imshow(largest_cluster_mask, cmap='Reds', alpha=0.7, origin='lower')

ax.set_title(f"Percolation Simulation (p={OCCUPATION_PROBABILITY:.2f})")
ax.axis('off')

plt.savefig('../../shared_space/percolation_simulation.png')
plt.close()

print("Percolation simulation generated and saved as percolation_simulation.png")
