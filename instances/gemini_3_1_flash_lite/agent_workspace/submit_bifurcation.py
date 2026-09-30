from colony_lib.bifurcation import branch_continuation
import numpy as np

def system(x, r):
    return r*x - x**3

params = np.linspace(-1, 2, 100)
results = branch_continuation(system, params)
# Save results to a file for later processing
import json
with open('bifurcation_data.json', 'w') as f:
    json.dump(results, f)
