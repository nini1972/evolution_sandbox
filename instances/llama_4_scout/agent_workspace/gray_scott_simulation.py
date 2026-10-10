import numpy as np
import matplotlib.pyplot as plt
from colony_lib.dynamics import GrayScott2D

# Parameters
N = 256
F = 0.02
k = 0.06
Du = 0.16
Dv = 0.08
dt = 1.0
steps = 10000

# Initialize GrayScott2D
solver = GrayScott2D(N=N, F=F, k=k, Du=Du, Dv=Dv, dt=dt)

# Run simulation
U, V = solver.run(steps=steps)

# Plot final state
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.imshow(U, cmap='viridis')
plt.title('U')
plt.subplot(1, 2, 2)
plt.imshow(V, cmap='viridis')
plt.title('V')
plt.savefig('gray_scott_pattern.png')
