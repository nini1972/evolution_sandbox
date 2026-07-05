import numpy as np

# Adaptive Cellular Automata:
# Rules adjust dynamically based on global density levels
# States 0: Inactive, 1: Active
# Adaptive mechanic: If average density > 0.4, survival requirements increase (stricter)
# If density < 0.2, birth requirements decrease (easier)

def get_neighbors(grid, r, c):
    rows, cols = grid.shape
    neighbors = []
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            if i == 0 and j == 0: continue
            neighbors.append(grid[(r + i) % rows, (c + j) % cols])
    return neighbors

def step(grid):
    density = np.mean(grid)
    
    # Adaptive threshold parameters
    if density > 0.4:
        birth_thresh = [3] # High strictness
        survive_thresh = [2, 3]
    elif density < 0.2:
        birth_thresh = [2, 3] # Easy expansion
        survive_thresh = [1, 2, 3]
    else:
        birth_thresh = [3]
        survive_thresh = [2, 3]
        
    next_grid = grid.copy()
    rows, cols = grid.shape
    
    for r in range(rows):
        for c in range(cols):
            neighbors = get_neighbors(grid, r, c)
            active_neighbors = sum(neighbors)
            
            if grid[r, c] == 0:
                if active_neighbors in birth_thresh:
                    next_grid[r, c] = 1
            else:
                if active_neighbors not in survive_thresh:
                    next_grid[r, c] = 0
    return next_grid

# Run experiment
grid = np.random.choice([0, 1], size=(30, 30), p=[0.7, 0.3])
history = []
for _ in range(100):
    history.append(grid.copy())
    grid = step(grid)

np.save('experiments/emergent_behavior_v3/simulation_data.npy', np.array(history))
print("Adaptive simulation complete.")
