import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# Define the coupled oscillator dynamics
def coupled_oscillators(y, t, omega, k):
    theta1, theta2 = y
    dydt = [omega - k * np.sin(theta1 - theta2),
           omega - k * np.sin(theta2 - theta1)]
    return dydt

# Set up the simulation parameters
omega = 1.0
k = 0.5
initial_conditions = [0.1, 0.2]
t = np.linspace(0, 10, 1000)

# Solve the coupled oscillator equations
y = odeint(coupled_oscillators, initial_conditions, t, args=(omega, k))

# Visualize the phase space
fig, ax = plt.subplots(figsize=(8, 8))
ax.plot(y[:, 0], y[:, 1])
ax.set_xlabel(r'$\theta_1$')
ax.set_ylabel(r'$\theta_2$')
ax.set_title('Phase Space of Coupled Oscillators')
plt.savefig('coupled_oscillator_network.png')