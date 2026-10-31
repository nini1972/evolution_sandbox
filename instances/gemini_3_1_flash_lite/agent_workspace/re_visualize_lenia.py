import numpy as np
from colony_lib.dynamics import Lenia2D

# Explicitly initializing with non-zero state
sim = Lenia2D(grid_size=64, kernel_radius=15, mu_g=0.15, sigma_g=0.02)
# Manually seed the state with random noise
sim.state = np.random.rand(64, 64) * 0.1

for _ in range(500):
    sim.step()

np.save('lenia_state.npy', sim.state)
print("Saved non-zero state to lenia_state.npy")
