import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def lorenz_attractor(sigma, rho, beta, x0, y0, z0, t_max, dt):
    t = np.arange(0, t_max, dt)
    x = np.zeros(len(t))
    y = np.zeros(len(t))
    z = np.zeros(len(t))
    x[0] = x0
    y[0] = y0
    z[0] = z0
    for i in range(1, len(t)):
        x[i] = x[i-1] + sigma*(y[i-1] - x[i-1])*dt
        y[i] = y[i-1] + (x[i-1]*(rho - z[i-1]) - y[i-1])*dt
        z[i] = z[i-1] + (x[i-1]*y[i-1] - beta*z[i-1])*dt
    return t, x, y, z

sigma = 10.0
rho = 28.0
beta = 8/3.0
x0 = 1.0
y0 = 1.0
z0 = 1.0
t_max = 40.0
dt = 0.01

t, x, y, z = lorenz_attractor(sigma, rho, beta, x0, y0, z0, t_max, dt)

fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(111, projection='3d')
ax.plot(x, y, z, lw=0.5)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('Lorenz Attractor')
plt.savefig('lorenz_attractor_plot.png')