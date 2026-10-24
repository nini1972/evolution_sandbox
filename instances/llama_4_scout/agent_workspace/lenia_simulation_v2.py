import numpy as np
from colony_lib.dynamics import Lenia2D
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Initialize 2D continuous automaton with annular Gaussian kernel
lenia = Lenia2D(
    grid_size=256,
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
lenia.run(steps=200)

# Plot the final state
plt.imshow(lenia.state, cmap='viridis')
plt.savefig('lenia_final_state_v2.png')