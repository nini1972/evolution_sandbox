
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
    ensemble = KuramotoEnsemble(N=N, K=K, seed=42)
    
    times = np.arange(0, T, dt)
    order_parameters = []

    for t in times:
        ensemble.step(dt)
        order_parameters.append(ensemble.order_parameter())

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

