import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from colony_lib.dynamics import Lenia2D

# Explore the parameter space of Lenia to see how it affects structure formation
# Parameters: mu_g (growth mean), sigma_g (growth variance)

mu_values = [0.1, 0.15, 0.2]
sigma_values = [0.01, 0.02, 0.05]

fig, axes = plt.subplots(len(mu_values), len(sigma_values), figsize=(15, 15))

for i, mu in enumerate(mu_values):
    for j, sigma in enumerate(sigma_values):
        sim = Lenia2D(grid_size=64, kernel_radius=15, mu_g=mu, sigma_g=sigma)
        sim.seed_orbium()
        for _ in range(50):
            sim.step()
        
        ax = axes[i, j]
        ax.imshow(sim.state, cmap='inferno')
        ax.set_title(f"mu={mu}, sigma={sigma}")
        ax.axis('off')

plt.tight_layout()
plt.savefig('lenia_morphospace_exploration.png')
print("Morphospace exploration complete. Saved to lenia_morphospace_exploration.png")
