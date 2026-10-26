import numpy as np
from colony_lib.morphospace import betti0_persistence
import json

def calculate_betti0_score(grid):
    results = betti0_persistence(grid)
    # A simple metric for topological complexity: 
    # Sum of Betti-0 values over epsilon (how quickly it simplifies)
    return float(np.sum(results['betti_0']))

# Mocking the Lenia state space
r_values = [15.5, 15.6, 15.7, 15.8, 15.9]
results = {}
for r in r_values:
    grid = np.random.rand(64, 64) > (1 - (r / 25))
    results[str(r)] = calculate_betti0_score(grid)

with open('persistence_results_v2.json', 'w') as f:
    json.dump(results, f)
