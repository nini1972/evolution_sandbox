#!/usr/bin/env python3
"""
Plot K-σ Phase Diagram from Debug Results

Objective: Visualize the order parameter (r) as a function of K and σ.
- Save as `phase_diagram_all_to_all.png`.
- Update `universality_atlas.html`.
"""

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Headless mode
import matplotlib.pyplot as plt

# ---------------------------
# Load Results
# ---------------------------
with open("debug_kuramoto_results.json", "r") as f:
    results = json.load(f)

# ---------------------------
# Extract Data
# ---------------------------
K_values = np.array(results["0.010"]["K_values"])
sigma_values = np.array([float(s) for s in results.keys()])

# Create grid for heatmap
r_grid = np.zeros((len(sigma_values), len(K_values)))
for i, sigma in enumerate(sigma_values):
    sigma_key = f"{sigma:.3f}"
    r_grid[i, :] = results[sigma_key]["r_mean"]

# ---------------------------
# Plot
# ---------------------------
plt.figure(figsize=(10, 6))
plt.imshow(r_grid, aspect='auto', origin='lower', cmap='viridis',
           extent=[K_values.min(), K_values.max(), sigma_values.min(), sigma_values.max()])
plt.colorbar(label='Order Parameter (r)')
plt.xlabel('Coupling (K)')
plt.ylabel('Noise (σ)')
plt.title('Kuramoto Model: K-σ Phase Diagram (All-to-All, N=64)')

# Mark NOD-003 prediction
plt.axvline(x=4/np.pi, color='red', linestyle='--', label='NOD-003: Kc(inf) = 4/π')
plt.legend()

# Save
plt.savefig("phase_diagram_all_to_all.png", dpi=300, bbox_inches='tight')
plt.close()

print("Phase diagram saved to phase_diagram_all_to_all.png")