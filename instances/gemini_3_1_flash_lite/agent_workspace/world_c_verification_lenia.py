import numpy as np
from colony_lib.dynamics import Lenia2D
from colony_lib.morphospace import betti0_persistence

# Setup simulation sweep around the suspected critical point R=15.7
radii = np.linspace(14.0, 18.0, 20)
results = {}

for r in radii:
    # Minimal Lenia configuration for rapid sampling
    sim = Lenia2D(size=64, R=r, mu=0.15, sigma=0.02)
    state = sim.step(steps=200) # Pre-burn
    persistence = betti0_persistence(state)
    results[r] = persistence

print(results)
