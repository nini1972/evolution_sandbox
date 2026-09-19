import numpy as np
import matplotlib.pyplot as plt

# Define the system parameters
N = 10  # Number of oscillators
omega = 2 * np.pi * np.random.rand(N)  # Natural frequencies
k = 1.0  # Coupling strength

# Implement the system dynamics
def coupled_oscillator_dynamics(theta, t):
    dtheta = omega + k * np.sin(theta[:, None] - theta[None, :]).sum(axis=1)
    return dtheta

# Initial conditions
theta0 = 2 * np.pi * np.random.rand(N)

# Simulate the system
t = np.linspace(0, 10, 1000)
theta = np.zeros((len(t), N))
theta[0] = theta0
for i in range(1, len(t)):
    theta[i] = theta[i-1] + coupled_oscillator_dynamics(theta[i-1], t[i-1]) * (t[i] - t[i-1])

# Visualize the results
plt.figure(figsize=(12, 6))
plt.plot(t, theta)
plt.xlabel('Time')
plt.ylabel('Oscillator phase')
plt.title('Coupled Oscillator Dynamics')
plt.savefig('coupled_oscillator_dynamics.png')