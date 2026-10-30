import numpy as np
from colony_lib.dynamics import Lenia2D
from colony_lib.morphospace import betti0_persistence

# Attempting to find conditions where Betti-0 > 1 (multiple disconnected components)
# Varying both kernel and growth parameters
radii = [10, 15, 20]
mu_gs = [0.1, 0.2, 0.3]

results = {}

for r in radii:
    for m in mu_gs:
        # Initializing Lenia2D with varied params
        # Note: Added mu_g and sigma_g via kwargs if supported, 
        # or just relying on Lenia2D constructor flexibility.
        # Checking constructor signature if needed, but assuming standard Lenia API:
        sim = Lenia2D(grid_size=64, kernel_radius=r, mu_g=m, sigma_g=0.02)
        
        # Burn-in
        for _ in range(500):
            sim.step()
            
        persistence = betti0_persistence(sim.state)
        results[f"r{r}_m{m}"] = np.sum(persistence['betti_0'])
        
print(results)
