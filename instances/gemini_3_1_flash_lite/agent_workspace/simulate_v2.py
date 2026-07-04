import numpy as np

# Improved CA: Multi-state Cellular Automaton
# States 0: Inactive, 1: Active, 2: Excited (High-energy)
# Transition rules based on neighborhood states to encourage complex oscillation

def next_state(grid):
    new_grid = grid.copy()
    rows, cols = grid.shape
    for r in range(rows):
        for c in range(cols):
            # Neighborhood analysis
            neighbors = []
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if i == 0 and j == 0: continue
                    neighbors.append(grid[(r + i) % rows, (c + j) % cols])
            
            count_active = neighbors.count(1)
            count_excited = neighbors.count(2)
            
            # Complex state transition rules
            if grid[r, c] == 0 and count_active == 3:
                new_grid[r, c] = 1
            elif grid[r, c] == 1:
                if count_active < 2 or count_active > 3:
                    new_grid[r, c] = 0
                elif count_excited > 0:
                    new_grid[r, c] = 2
            elif grid[r, c] == 2:
                new_grid[r, c] = 0 # Excited state decays rapidly
                
    return new_grid

# Initialize with higher variety
grid = np.random.randint(0, 3, size=(20, 20))

# Simulate for 50 steps
states = []
current = grid
for _ in range(50):
    states.append(current.copy())
    current = next_state(current)

np.save('simulation_states_v2.npy', np.array(states))
print("Multi-state simulation complete.")
