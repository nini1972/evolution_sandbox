import numpy as np
import matplotlib.pyplot as plt

# Define the Kuramoto model with heterogeneous natural frequencies
def kuramoto(N, omega, K, T, dt):
    """
    Simulate the Kuramoto model with N oscillators.
    
    Parameters:
    N (int): Number of oscillators
    omega (np.ndarray): Natural frequencies of the oscillators
    K (float): Coupling strength
    T (float): Total simulation time
    dt (float): Time step
    
    Returns:
    np.ndarray: Time series of the phases of the oscillators
    """
    theta = 2 * np.pi * np.random.rand(N)  # Initial phases
    t = np.arange(0, T, dt)
    phases = np.zeros((len(t), N))
    
    for i, time in enumerate(t):
        dtheta = omega + K/N * np.sum(np.sin(theta - theta), axis=0)
        theta += dtheta * dt
        theta = np.mod(theta, 2 * np.pi)
        phases[i] = theta
    
    return phases

# Example usage
N = 50
omega = np.random.normal(1.0, 0.1, N)
K = 1.5
T = 50
dt = 0.05

phases = kuramoto(N, omega, K, T, dt)

# Plot the results
plt.figure(figsize=(12, 6))
plt.plot(np.arange(0, T, dt), phases)
plt.xlabel('Time')
plt.ylabel('Phase')
plt.title('Kuramoto Model with Heterogeneous Natural Frequencies')
plt.savefig('kuramoto_heterogeneity.png')