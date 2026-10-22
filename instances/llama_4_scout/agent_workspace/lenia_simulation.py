import numpy as np
from colony_lib.dynamics import Lenia2D

# Initialize 2D continuous automaton with annular Gaussian kernel
lenia = Lenia2D(
    grid_size=128,
    kernel_radius=13,
    mu_k=0.5,       # Center radius of Gaussian kernel ring
    sigma_k=0.15,   # Width of Gaussian kernel ring
    mu_g=0.135,     # Peak of Gaussian growth function
    sigma_g=0.015,  # Tolerance band of Gaussian growth
    dt=0.1
)

# Seed a Gaussian soliton blob (Orbium)
lenia.seed_orbium()

# Simulate continuous time evolution
metrics = lenia.run(steps=100)
print(metrics.keys())

print(type(metrics['final_mass'])); print(metrics['final_mass'])
# Plot the final state
import matplotlib.pyplot as plt
plt.plot(metrics['mass_trajectory'])
plt.savefig('lenia_mass_trajectory.png')
plt.savefig('lenia_simulation.png')