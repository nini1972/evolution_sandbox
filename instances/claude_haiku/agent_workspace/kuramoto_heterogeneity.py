import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# Define the Kuramoto model with heterogeneous natural frequencies
def kuramoto(theta, t, K, omega):
    N = len(theta)
    dtheta = omega - K/N * np.sum(np.sin(theta - theta), axis=0)
    return dtheta

# Initialize the system
N = 50
theta0 = 2 * np.pi * np.random.rand(N)
omega = 2 * np.pi * (1 + 0.1 * np.random.randn(N))  # Heterogeneous natural frequencies
K = 1.5  # Coupling strength

# Simulate the dynamics
t = np.linspace(0, 50, 1000)
theta = odeint(kuramoto, theta0, t, args=(K, omega))

# Visualize the results
fig, ax = plt.subplots(figsize=(8, 6))
for i in range(N):
    ax.plot(t, theta[:, i], alpha=0.5)
ax.set_xlabel('Time')
ax.set_ylabel('Phase')
ax.set_title('Kuramoto Model with Heterogeneous Natural Frequencies')
plt.savefig('kuramoto_heterogeneity.png')