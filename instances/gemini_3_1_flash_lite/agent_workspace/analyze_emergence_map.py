import numpy as np
from colony_lib.dynamics import Lenia2D
import json

# Define the metric function as described in Treaty 003
def compute_spatiotemporal_metrics(sim, steps=200):
    # Spatial LZ complexity (2x2 block approximation)
    # Temporal LZ decay (temporal complexity across steps)
    spatial_snapshots = []
    for _ in range(steps):
        sim.step()
        spatial_snapshots.append(sim.state.copy())
    
    # Simple proxy for spatial entropy: fraction of high activity cells
    spatial_entropy = np.mean(np.var(spatial_snapshots[-1], axis=0))
    
    # Temporal decay: variance of activity over time
    temporal_mean_activity = [np.mean(s) for s in spatial_snapshots]
    temporal_complexity = np.var(temporal_mean_activity)
    
    return float(spatial_entropy), float(temporal_complexity)

# Run a scan across the Lenia space to locate regions of high emergence
mu_range = np.linspace(0.1, 0.3, 10)
sigma_range = np.linspace(0.01, 0.1, 10)
results = []

for mu in mu_range:
    for sigma in sigma_range:
        sim = Lenia2D(grid_size=32, kernel_radius=15, mu_g=mu, sigma_g=sigma)
        sim.seed_orbium()
        s_ent, t_comp = compute_spatiotemporal_metrics(sim)
        results.append({
            "mu": float(mu),
            "sigma": float(sigma),
            "spatial_entropy": s_ent,
            "temporal_complexity": t_comp
        })

with open("spatiotemporal_map.json", "w") as f:
    json.dump(results, f)
