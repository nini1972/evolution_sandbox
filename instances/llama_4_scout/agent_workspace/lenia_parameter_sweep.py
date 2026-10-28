import numpy as np
import matplotlib.pyplot as plt
from colony_lib.dynamics import Lenia2D

# Define the parameters for Lenia
grid_size = 128
kernel_radius = 13
mu_k = 0.5
sigma_k = 0.15
mu_g_values = [0.1, 0.135, 0.2]  # Varying mu_g
sigma_g = 0.015
dt = 0.1

# Perform a simple parameter sweep
for mu_g in mu_g_values:
    lenia = Lenia2D(
        grid_size=grid_size,
        kernel_radius=kernel_radius,
        mu_k=mu_k,
        sigma_k=sigma_k,
        mu_g=mu_g,
        sigma_g=sigma_g,
        dt=dt
    )
    lenia.seed_orbium()
    metrics = lenia.run(steps=100)
    plt.imshow(lenia.state, cmap='viridis')
    plt.savefig(f'lenia_state_mu_g_{mu_g}.png')
    plt.close()