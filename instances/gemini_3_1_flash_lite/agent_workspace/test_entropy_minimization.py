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

def evolve_rule_to_minimize(rule, grid):
    # Instead of just taking the entropy value, I will try to adapt the rule to *lower* entropy
    # This is a bit complex, but I'll try to mutate rules that resulted in higher entropy in the last step
    p = np.mean(grid)
    new_rule = rule.copy()
    
    # If entropy is high (p near 0.5), we want to push it towards 0 or 1
    # Simple strategy: flip a bit that changes the number of cells that will be 'on'
    if p > 0.5:
        # Flip a rule bit to reduce 'on' counts
        idx = np.random.randint(0, 9)
        new_rule[idx] = 0
    else:
        # Flip a rule bit to increase 'on' counts
        idx = np.random.randint(0, 9)
        new_rule[idx] = 1
    return new_rule

def run_simulation_minimization(size):
    grid = np.random.randint(0, 2, (size, size))
    rule = [0, 0, 1, 0, 1, 0, 0, 0, 0]
    
    entropies = []
    for _ in range(50):
        p = np.mean(grid)
        entropy = - (p * np.log2(p + 1e-10) + (1-p) * np.log2(1-p + 1e-10))
        entropies.append(entropy)
        
        grid = update_grid(grid, rule)
        rule = evolve_rule_to_minimize(rule, grid)
    return entropies

results = run_simulation_minimization(20)
print(results)
