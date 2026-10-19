# Exploring Kuramoto model with non-linear order feedback
import numpy as np
from colony_lib.dynamics import kuramoto_oscillators

# Define parameters
N = 200
K0 = 1.0
alpha = 1.5
sigma = 0.01

# Initialize oscillators
theta = np.random.uniform(0, 2*np.pi, N)

# Simulate Kuramoto model with non-linear order feedback
for t in range(1000):
    K = K0 * (np.abs(np.mean(np.exp(1j*theta))))**alpha
    theta += kuramoto_oscillators(theta, K, sigma)

# Plot the results
import matplotlib.pyplot as plt
plt.plot(np.abs(np.mean(np.exp(1j*theta))))
plt.savefig('kuramoto_nonlinear_feedback.png')