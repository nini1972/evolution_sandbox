
import numpy as np
import matplotlib.pyplot as plt
import json
from colony_lib.dynamics import KuramotoEnsemble

# Configure matplotlib for headless plotting
plt.switch_backend('Agg')

def run_kuramoto_simulation(N, K, T, dt, output_prefix="kuramoto_sim"):
    """
    Runs a Kuramoto simulation and saves results as JSON and a plot as PNG.
    """
    ensemble = KuramotoEnsemble()
    ensemble.N = N
    ensemble.K = K
    # Initialize random phases and natural frequencies
    # Using np.random.seed for reproducibility, matching previous "seed=42"
    rng = np.random.default_rng(42)
    ensemble.phases = rng.uniform(0, 2 * np.pi, N)
    ensemble.omega = rng.normal(0, 1, N) # Standard normal distribution for frequencies

    
    ensemble.run(T, dt)
    times = np.arange(0, T, dt)
    order_parameters = ensemble.r_series.tolist() # Convert to list for JSON serialization

    results = {
        "N": N,
        "K": K,
        "T": T,
        "dt": dt,
        "times": times.tolist(),
        "order_parameters": order_parameters
    }

    # Save results to JSON
    json_output_path = f"{output_prefix}_results.json"
    with open(json_output_path, 'w') as f:
        json.dump(results, f, indent=4)
    print(f"Saved simulation results to {json_output_path}")

    # Plot order parameter over time
    plt.figure(figsize=(10, 6))
    plt.plot(times, order_parameters)
    plt.xlabel("Time")
    plt.ylabel("Order Parameter (R)")
    plt.title(f"Kuramoto Order Parameter (N={N}, K={K})")
    plt.grid(True)
    png_output_path = f"{output_prefix}_order_parameter.png"
    plt.savefig(png_output_path)
    print(f"Saved plot to {png_output_path}")
    plt.close() # Close the plot to free up memory

if __name__ == "__main__":
    # Example usage:
    N_oscillators = 100
    coupling_strength = 1.5
    total_time = 50
    time_step = 0.1

    run_kuramoto_simulation(N_oscillators, coupling_strength, total_time, time_step)

