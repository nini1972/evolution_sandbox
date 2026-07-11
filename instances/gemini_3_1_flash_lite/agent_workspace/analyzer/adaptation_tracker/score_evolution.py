import numpy as np

def score_complexity(grid):
    # Higher complexity = patterns that shift but persist.
    # Score based on how many cells change per cycle vs static blocks.
    return np.std(grid) * np.sum(grid)

grid = np.load('simulations/emergence_incubation/state.npy')
score = score_complexity(grid)
with open('analyzer/adaptation_tracker/evolution_history.txt', 'a') as f:
    f.write(f"Complexity Score: {score}\n")

print(f"Current Complexity Score: {score}")
