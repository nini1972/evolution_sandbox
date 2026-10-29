import numpy as np
from colony_lib.dynamics import Lenia2D
from colony_lib.morphospace import betti0_persistence

# Setup simulation sweep to detect if structure emerges
# Grid 128 to have more room for patterns to form
radii = np.linspace(10.0, 20.0, 10)
results = {}

for r in radii:
    # Kernel radius seems to be a key driver
    sim = Lenia2D(grid_size=128, kernel_radius=int(r), mu_k=0.15, sigma_k=0.02)
    # Increase steps to let patterns stabilize
    for _ in range(500):
        state = sim.step()
    # Check persistence
    persistence = betti0_persistence(state)
    results[r] = persistence

print(results)
