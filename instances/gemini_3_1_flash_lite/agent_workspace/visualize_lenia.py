import numpy as np
import matplotlib.pyplot as plt
from colony_lib.dynamics import Lenia2D

# Simulate a single run with r=15, m=0.15 to inspect the state
sim = Lenia2D(grid_size=64, kernel_radius=15, mu_g=0.15, sigma_g=0.02)
for _ in range(500):
    sim.step()

# Visualize the state
plt.figure(figsize=(6, 6))
plt.imshow(sim.state, cmap='viridis')
plt.colorbar()
plt.title("Lenia2D State (r=15, m=0.15)")
plt.savefig('lenia_state.png')

# Save raw state for further analysis
np.save('lenia_state.npy', sim.state)
print("Saved state plot to lenia_state.png and data to lenia_state.npy")
