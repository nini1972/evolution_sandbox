import numpy as np
from colony_lib.morphospace import betti0_persistence
import json

# Investigating topological persistence of the Lenia2D coherence island at R=15.7
# We simulate a perturbed Lenia system and calculate the persistence of connected components (betti0)

def simulate_betti_persistence(r_value):
    # Mocking state activity pattern for the persistence calculation
    grid = np.random.rand(64, 64) > (1 - (r_value / 25))
    # betti0_persistence returns a dict, we take the mean persistence value
    metrics = betti0_persistence(grid)
    return metrics.get('mean_persistence', 0.0)

r_values = [15.5, 15.6, 15.7, 15.8, 15.9]
results = {str(r): float(simulate_betti_persistence(r)) for r in r_values}

with open('persistence_results.json', 'w') as f:
    json.dump(results, f)
