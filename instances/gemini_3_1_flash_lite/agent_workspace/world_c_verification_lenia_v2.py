import numpy as np
from colony_lib.dynamics import Lenia2D
from colony_lib.morphospace import betti0_persistence

# Setup simulation sweep around the suspected critical point R=15.7
radii = np.linspace(14.0, 18.0, 20)
results = {}

for r in radii:
    # Corrected Lenia initialization
    sim = Lenia2D(grid_size=64, kernel_radius=int(r), mu_k=0.15, sigma_k=0.02)
    state = sim.step(steps=200) # Pre-burn
    persistence = betti0_persistence(state)
    results[r] = persistence

print(results)
