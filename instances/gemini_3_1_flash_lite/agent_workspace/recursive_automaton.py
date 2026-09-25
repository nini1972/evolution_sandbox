import numpy as np
import json

def update_grid(grid, rule):
    # Rule application as a simple function of neighbor sum
    # rule is a 9-element list, index = sum of neighbors (0-8)
    rows, cols = grid.shape
    new_grid = np.zeros_like(grid)
    for r in range(rows):
        for c in range(cols):
            neighbors = np.sum(grid[max(0,r-1):min(rows,r+2), max(0,c-1):min(cols,c+2)]) - grid[r,c]
            new_grid[r,c] = rule[int(neighbors)]
    return new_grid

# Rule evolution: update the rule itself based on the global entropy of the grid
def evolve_rule(rule, grid):
    entropy = -np.sum(grid * np.log(grid + 1e-10) + (1-grid) * np.log(1-grid + 1e-10))
    # Simple rule mutation
    new_rule = rule.copy()
    idx = int(entropy * 10) % 9
    new_rule[idx] = 1 - new_rule[idx]
    return new_rule

# Initialize grid and rule
grid = np.random.randint(0, 2, (20, 20))
rule = [0, 0, 1, 0, 1, 0, 0, 0, 0] # Simple initial rule
history = []

for i in range(50):
    history.append(grid.tolist())
    grid = update_grid(grid, rule)
    rule = evolve_rule(rule, grid)

with open('recursive_evolution.json', 'w') as f:
    json.dump({'history': history, 'rule_final': rule}, f)
