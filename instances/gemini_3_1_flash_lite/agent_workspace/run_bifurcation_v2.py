import numpy as np
import json

def get_steady_states(r):
    # For dx/dt = r*x - x^3
    # Fixed points: x(r - x^2) = 0 => x=0 or x=sqrt(r) or x=-sqrt(r)
    if r < 0:
        return [0.0]
    else:
        return [0.0, np.sqrt(r), -np.sqrt(r)]

params = np.linspace(-1, 2, 100)
data = {float(r): get_steady_states(r) for r in params}

with open('bifurcation_results_v2.json', 'w') as f:
    json.dump(data, f)
