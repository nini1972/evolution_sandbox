import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from colony_lib.dynamics import Lenia2D

# Initialize
sim = Lenia2D(grid_size=64, kernel_radius=15, mu_g=0.15, sigma_g=0.02)
sim.seed_orbium() # Likely sets the initial state correctly
print(f"Initial state min/max: {sim.state.min()}, {sim.state.max()}")

# Run evolution
for _ in range(100):
    sim.step()

# Visualize
plt.figure()
plt.imshow(sim.state, cmap='viridis')
plt.colorbar()
plt.savefig('lenia_evolved.png')
print("Saved visualization to lenia_evolved.png")

# Save state
np.save('lenia_state.npy', sim.state)
print("Saved state to lenia_state.npy")
