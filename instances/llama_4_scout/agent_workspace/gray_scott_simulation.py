import numpy as np
import matplotlib.pyplot as plt
from colony_lib.dynamics import GrayScott2D

# Define the parameters for the Gray-Scott model
grid_size = 256
Du = 0.16
Dv = 0.08
F = 0.04
k = 0.06
dt = 1.0

# Initialize the Gray-Scott model
gray_scott = GrayScott2D(
    grid_size=grid_size,
    Du=Du,
    Dv=Dv,
    F=F,
    k=k,
    dt=dt
)

# Seed the center
gray_scott.seed_center()

# Run the simulation
for _ in range(1000):
    gray_scott.step()

# Visualize the final state
plt.imshow(gray_scott.u, cmap='viridis')
plt.savefig('gray_scott_simulation.png')
plt.close()