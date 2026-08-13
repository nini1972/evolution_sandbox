import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def lorenz(x, y, z, s, r, b):
    x_dot = s * (y - x)
    y_dot = r * x - y - x * z
    z_dot = x * y - b * z
    return x_dot, y_dot, z_dot

# Simulation parameters
dt = 0.01
num_steps = 10000

# Initial conditions
x0, y0, z0 = 0.0, 1.0, 1.05

# Lorenz parameters
s, r, b = 10, 28, 2.667

# Store results
x = np.empty(num_steps + 1)
y = np.empty(num_steps + 1)
z = np.empty(num_steps + 1)

x[0], y[0], z[0] = x0, y0, z0

# Solve ODE
for i in range(num_steps):
    x_dot, y_dot, z_dot = lorenz(x[i], y[i], z[i], s, r, b)
    x[i + 1] = x[i] + (x_dot * dt)
    y[i + 1] = y[i] + (y_dot * dt)
    z[i + 1] = z[i] + (z_dot * dt)

# Plotting
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

ax.plot(x, y, z, lw=0.5)
ax.set_xlabel("X Axis")
ax.set_ylabel("Y Axis")
ax.set_zlabel("Z Axis")
ax.set_title("Lorenz Attractor")

plt.savefig('../../shared_space/lorenz_attractor.png')
plt.close()

print("Lorenz Attractor visualization generated and saved as lorenz_attractor.png")
