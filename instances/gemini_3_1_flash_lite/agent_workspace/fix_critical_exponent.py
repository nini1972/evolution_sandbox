import numpy as np
from colony_lib.dynamics import Lenia2D
from colony_lib.bifurcation_cartography import extract_critical_exponent
import json

# Focus on the transition zone identified in the initial sweep (mu approx 0.13 to 0.18, sigma approx 0.05)
mu_values = np.linspace(0.12, 0.19, 20)
r_values = []

for mu in mu_values:
    # Fix sigma where complexity was observed to be rising
    sim = Lenia2D(grid_size=64, kernel_radius=15, mu_g=mu, sigma_g=0.05)
    sim.seed_orbium()
    for _ in range(150):
        sim.step()
    # Observable: Mean activity (proxy for order parameter)
    r_values.append(np.mean(sim.state))

# Calculate the critical exponent - extract_critical_exponent returns a tuple or similar structure
# Need to handle the return value correctly based on the docstring/expected output
result = extract_critical_exponent(mu_values, r_values, window=5)

# If it returns (exponent, intercept), just take the exponent
if isinstance(result, (tuple, list)):
    critical_exponent = float(result[0])
else:
    critical_exponent = float(result)

with open("critical_exponent_data.json", "w") as f:
    json.dump({
        "mu_values": mu_values.tolist(),
        "r_values": r_values,
        "critical_exponent": critical_exponent
    }, f)
