import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# Define the system of differential equations
def lorenz_attractor(state, t, sigma, rho, beta):
    x, y, z = state
    dx_dt = sigma * (y - x)
    dy_dt = x * (rho - z) - y
    dz_dt = x * y - beta * z
    return [dx_dt, dy_dt, dz_dt]

# Set the parameters
sigma = 10
rho = 28
beta = 8/3

# Initial conditions
x0 = 1.0
y0 = 1.0
z0 = 1.0
initial_state = [x0, y0, z0]

# Solve the system of equations
t = np.linspace(0, 30, 10000)
states = odeint(lorenz_attractor, initial_state, t, args=(sigma, rho, beta))

# Plot the phase space
fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d')
ax.plot(states[:, 0], states[:, 1], states[:, 2], lw=0.5)
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')
ax.set_title('Lorenz Attractor')
plt.savefig('phase_space_analysis.png')
print('Phase space analysis saved to phase_space_analysis.png')