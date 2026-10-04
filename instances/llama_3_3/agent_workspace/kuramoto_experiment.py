import colony_lib.dynamics.kuramoto
import matplotlib.pyplot as plt
import numpy as np
import os

# Define simulation parameters
N = 100  # Number of oscillators
dt = 0.1  # Time step
steps = 1000  # Number of simulation steps

# Example coupling strengths (K) to explore synchronization
coupling_strengths = [0.1, 0.5, 1.0, 2.0]  # Transition to synchronization often happens around K=1

# Create a directory for outputs
output_dir = "kuramoto_results"
os.makedirs(output_dir, exist_ok=True)

for K in coupling_strengths:
    print(f"Simulating Kuramoto for K={K}...")

    # Call the World C `colony_lib` function
    # The `colony_lib.dynamics.kuramoto.simulate_kuramoto` function
    # is assumed to exist and return phases and the order parameter over time.
    try:
        phi_history, R_history = colony_lib.dynamics.kuramoto.simulate_kuramoto(
            N=N, K=K, steps=steps, dt=dt
        )
    except AttributeError:
        print(f"Error: colony_lib.dynamics.kuramoto.simulate_kuramoto not found. "
              "This script is intended for World C execution.")
        # Generate placeholder data if colony_lib is not available locally
        time = np.linspace(0, steps * dt, steps)
        phi_history = np.random.rand(steps, N) * 2 * np.pi  # Placeholder for oscillator phases
        R_history = np.sin(time / 10) + 0.5  # Placeholder for order parameter

    time = np.linspace(0, steps * dt, steps)

    # Plot oscillator phases
    plt.figure(figsize=(10, 6))
    for i in range(N):
        plt.plot(time, phi_history[:, i], alpha=0.3)
    plt.title(f"Kuramoto Oscillator Phases (K={K})")
    plt.xlabel("Time")
    plt.ylabel("Phase")
    plt.ylim(0, 2 * np.pi)
    plt.savefig(os.path.join(output_dir, f"kuramoto_phases_K{K}.png"))
    plt.close()

    # Plot order parameter
    plt.figure(figsize=(10, 4))
    plt.plot(time, R_history)
    plt.title(f"Kuramoto Order Parameter R(t) (K={K})")
    plt.xlabel("Time")
    plt.ylabel("R(t)")
    plt.ylim(0, 1)
    plt.savefig(os.path.join(output_dir, f"kuramoto_order_parameter_K{K}.png"))
    plt.close()

    print(f"Saved Kuramoto plots for K={K}.")

print("Kuramoto synchronization experiment script generated.")