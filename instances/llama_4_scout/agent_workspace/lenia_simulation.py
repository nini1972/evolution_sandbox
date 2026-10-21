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
plt.imshow(final_state)
plt.savefig('lenia_simulation.png')
plt.imshow(final_state)
plt.savefig('lenia_simulation.png')
print(f"Final Soliton Mass: {metrics['final_mass']:.2f}")
print(f"Max Field Amplitude: {metrics['max_amplitude']:.4f}")
print(f"Active Area Fraction: {metrics['active_area_fraction']:.4f}")

# Plot the final state
import matplotlib.pyplot as plt
plt.imshow(lenia.get_final_state())
plt.savefig('lenia_simulation.png')