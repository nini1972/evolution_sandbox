import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# Define the coupled oscillator network dynamics
def coupled_oscillators(state, t, N, omega, k, c):
    x = state.reshape(N, 2)
    dx_dt = np.zeros_like(x)

    for i in range(N):
        dx_dt[i, 0] = x[i, 1]
        dx_dt[i, 1] = -omega[i]**2 * x[i, 0] - 2 * c[i] * x[i, 1]
        for j in range(N):
            if i != j:
                dx_dt[i, 1] -= k[i, j] * (x[i, 0] - x[j, 0])

    return dx_dt.flatten()

# Simulate the coupled oscillator network
def simulate_coupled_oscillators(N, omega, k, c, x0, t_span):
    state0 = np.concatenate([x0[:, 0], x0[:, 1]]).flatten()
    t = np.linspace(t_span[0], t_span[1], int((t_span[1] - t_span[0]) / 0.01) + 1)
    states = odeint(coupled_oscillators, state0, t, args=(N, omega, k, c))
    states = states.reshape(-1, N, 2)
    return t, states

# Example usage
if __name__ == "__main__":
    N = 5  # Number of oscillators
    omega = np.array([1.0, 1.1, 0.9, 1.05, 0.95])  # Natural frequencies
    k = np.array([[0, 1, 1, 0, 0], 
                  [1, 0, 0, 1, 0],
                  [1, 0, 0, 0, 1], 
                  [0, 1, 0, 0, 1],
                  [0, 0, 1, 1, 0]])  # Coupling strengths
    c = np.array([0.1, 0.1, 0.1, 0.1, 0.1])  # Damping coefficients
    x0 = np.array([[1.0, 0], [0.8, 0], [1.2, 0], [0.9, 0], [1.1, 0]])  # Initial conditions

    t, states = simulate_coupled_oscillators(N, omega, k, c, x0, (0, 50))

    # Visualize the oscillator positions over time
    plt.figure(figsize=(12, 6))
    for i in range(N):
        plt.plot(t, states[:, i, 0], label=f"Oscillator {i+1}")
    plt.xlabel("Time")
    plt.ylabel("Position")
    plt.title("Coupled Oscillator Network")
    plt.legend()
    plt.savefig("coupled_oscillator_network.png")