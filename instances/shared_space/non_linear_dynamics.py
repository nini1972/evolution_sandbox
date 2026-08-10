import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Lorenz attractor simulation
def lorenz(x, y, z, sigma=10, rho=28, beta=8/3):
    dx = sigma * (y - x)
    dy = x * (rho - z) - y
    dz = x * y - beta * z
    return dx, dy, dz

# Initial conditions
x0, y0, z0 = 0.1, 0, 0

# Simulate Lorenz attractor
t = np.linspace(0, 40, 10000)
X = np.empty_like(t)
Y = np.empty_like(t)
Z = np.empty_like(t)
X[0], Y[0], Z[0] = x0, y0, z0
for i in range(1, len(t)):
    dx, dy, dz = lorenz(X[i-1], Y[i-1], Z[i-1])
    X[i] = X[i-1] + dx * (t[1] - t[0])
    Y[i] = Y[i-1] + dy * (t[1] - t[0]) 
    Z[i] = Z[i-1] + dz * (t[1] - t[0])

# Create 3D animation of Lorenz attractor
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')
ax.plot(X, Y, Z, lw=0.5)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('Lorenz Attractor')

ani = FuncAnimation(fig, lambda _: ax.view_init(elev=10., azim=10.), interval=50, frames=36, repeat=True)
ani.save('../../shared_space/lorenz_attractor.gif', writer='pillow')