
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Define the grid size
N = 50
grid = np.random.choice([0, 1], N*N, p=[0.8, 0.2]).reshape(N, N)

def update(frameNum, img, grid, N):
    newGrid = grid.copy()
    for i in range(N):
        for j in range(N):
            # Compute sum of 8 neighbors
            total = int((grid[i, (j-1)%N] + grid[i, (j+1)%N] + 
                         grid[(i-1)%N, j] + grid[(i+1)%N, j] + 
                         grid[(i-1)%N, (j-1)%N] + grid[(i-1)%N, (j+1)%N] + 
                         grid[(i+1)%N, (j-1)%N] + grid[(i+1)%N, (j+1)%N]))
            
            # Apply Conway's rules
            if grid[i, j] == 1:
                if (total < 2) or (total > 3):
                    newGrid[i, j] = 0
            else:
                if total == 3:
                    newGrid[i, j] = 1
    
    img.set_data(newGrid)
    grid[:] = newGrid[:]
    return img,

# Visualize
fig, ax = plt.subplots()
img = ax.imshow(grid, interpolation='nearest', cmap='binary')
plt.title("Baseline Environment Test: Conway's Game of Life")
plt.axis('off')

# Save initial state as evidence
plt.savefig('automata_start.png')
print("Simulation setup complete. Initial state saved to automata_start.png")
