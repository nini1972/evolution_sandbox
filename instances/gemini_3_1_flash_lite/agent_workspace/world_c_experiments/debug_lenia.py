import numpy as np
from colony_lib.dynamics import Lenia2D

# Inspect the Lenia2D class
print(f"Lenia2D attributes: {dir(Lenia2D)}")
sim = Lenia2D(grid_size=64, kernel_radius=15, mu_g=0.15, sigma_g=0.02)
print(f"Initial state min/max: {sim.state.min()}, {sim.state.max()}")
# Manually verify if I can change the state
sim.state[:] = 0.5
print(f"After manual set, min/max: {sim.state.min()}, {sim.state.max()}")
sim.step()
print(f"After step, min/max: {sim.state.min()}, {sim.state.max()}")
