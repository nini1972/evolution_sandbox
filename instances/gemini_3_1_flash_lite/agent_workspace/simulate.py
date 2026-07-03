import numpy as np

# Simulation: A simple cellular automaton on a 20x20 grid to observe emergent, self-organizing patterns.
# The grid behaves like a simplified Game of Life.

def next_state(grid):
    new_grid = grid.copy()
    rows, cols = grid.shape
    for r in range(rows):
        for c in range(cols):
            # Count neighbors
            neighbors = 0
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if i == 0 and j == 0: continue
                    nr, nc = (r + i) % rows, (c + j) % cols
                    neighbors += grid[nr, nc]
            
            # Simple rules:
            if grid[r, c] == 1:
                if neighbors < 2 or neighbors > 3:
                    new_grid[r, c] = 0
            else:
                if neighbors == 3:
                    new_grid[r, c] = 1
    return new_grid

# Random initial state
grid = np.random.choice([0, 1], size=(20, 20), p=[0.7, 0.3])

# Simulate for 10 steps and save the states
states = []
current = grid
for _ in range(10):
    states.append(current.copy())
    current = next_state(current)

# Store results for analysis
np.save('simulation_states.npy', np.array(states))
print("Simulation complete. States saved.")
