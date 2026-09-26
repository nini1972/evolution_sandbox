import numpy as np
import json

def update_grid(grid, rule):
    rows, cols = grid.shape
    new_grid = np.zeros_like(grid)
    for r in range(rows):
        for c in range(cols):
            neighbors = np.sum(grid[max(0,r-1):min(rows,r+2), max(0,c-1):min(cols,c+2)]) - grid[r,c]
            new_grid[r,c] = rule[int(neighbors)]
    return new_grid

def evolve_rule(rule, grid):
    entropy = -np.sum(grid * np.log(grid + 1e-10) + (1-grid) * np.log(1-grid + 1e-10))
    new_rule = rule.copy()
    idx = int(entropy * 10) % 9
    new_rule[idx] = 1 - new_rule[idx]
    return new_rule

def run_simulation(size):
    grid = np.random.randint(0, 2, (size, size))
    rule = [0, 0, 1, 0, 1, 0, 0, 0, 0]
    
    entropies = []
    for _ in range(50):
        # Calculate entropy
        p = np.mean(grid)
        entropy = - (p * np.log2(p + 1e-10) + (1-p) * np.log2(1-p + 1e-10))
        entropies.append(entropy)
        
        grid = update_grid(grid, rule)
        rule = evolve_rule(rule, grid)
    return entropies

results = {}
for size in [10, 20, 30, 40]:
    results[size] = run_simulation(size)

with open('robustness_results.json', 'w') as f:
    json.dump(results, f)
