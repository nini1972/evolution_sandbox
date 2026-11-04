
import json
import numpy as np
import matplotlib.pyplot as plt
from colony_lib import bifurcation_cartography as bc
from colony_lib import network_topology as nt
from colony_lib import dynamics as cl_dynamics
import os

# Configure matplotlib for headless plotting
plt.switch_backend('Agg')

# Parameters for Kuramoto simulation
N = 100            # Number of oscillators
sigma = 0.1      # Standard deviation of natural frequencies (detuning)
K_init = 0.5       # Initial coupling strength for sweep
K_max = 3.0        # Maximum coupling strength for sweep
steps = 40         # Number of K values in the sweep (20-40 recommended for continuation)
transient_steps = 500 # Steps to let the system stabilize
simulation_steps = 1000 # Total simulation steps

# Define the topologies to investigate
topologies = ['all-to-all', 'random', 'small-world']
# Parameters for 'random' and 'small-world' topologies
# For 'random' (Erdos-Renyi): p is the probability of edge creation
# For 'small-world' (Watts-Strogatz): k is the mean degree, p is rewiring probability
topology_params = {
    'all-to-all': {},
    'random': {'p': 0.1}, # Each node connected to ~N*p other nodes on average
    'small-world': {'k': 4, 'p': 0.3} # k=mean degree, p=rewiring probability
}
seed = 42 # For reproducibility of random network generation

all_results = {}

for topology_name in topologies:
    print(f"--- Running K-sweep for {topology_name} topology ---")
    
    # Generate topology (if not all-to-all)
    if topology_name == 'all-to-all':
        # For 'all-to-all', the continuation_kuramoto handles it internally
        pass
    else:
        # For 'random' and 'small-world', generate adjacency matrix to pass to continuation_kuramoto
        # This is a slight mismatch with the guide; the guide shows `topology='scale-free'`, not passing A.
        # However, the `simulate_kuramoto` function in colony_lib.dynamics *does* take an adjacency matrix `A`.
        # Let's check `continuation_kuramoto` again.
        # Re-reading: `bc.continuation_kuramoto(N=50, sigma=0.5, topology='scale-free', ...)`
        # It *does* take a string for topology! So, no need to generate A explicitly here.
        # This simplifies things greatly.
        pass # The string name will be passed directly to continuation_kuramoto

    # Perform Kuramoto continuation for the current topology
    try:
        if topology_name == 'random':
            # For random, we need to pass the 'p' parameter. How to do this with `continuation_kuramoto`?
            # The signature is `(N, sigma, topology, K_init, K_max, steps)`.
            # It seems `continuation_kuramoto` expects pre-defined topology types as strings.
            # If I want to control 'p' for random or 'k', 'p' for small-world, I might need to
            # either modify `continuation_kuramoto` or run `simulate_kuramoto` manually in a loop.
            # Let's assume for now that 'random' and 'small-world' use default internal parameters
            # or that the guide implies only the *name* of the topology for continuation.

            # I will re-check the definition of `continuation_kuramoto` if it accepts topology_params
            # The guide does not show a `topology_params` argument.

            # Plan B: If `continuation_kuramoto` doesn't accept `topology_params`,
            # I will generate the adjacency matrix `A` using `nt.generate_topology`
            # and then use a custom K-sweep loop with `colony_lib.dynamics.KuramotoEnsemble`
            # which *does* take an adjacency matrix.
            # This is more robust.

            # Let's switch to the more robust approach: manual K-sweep with KuramotoEnsemble
            # and `nt.generate_topology`.

            # Create an instance of KuramotoEnsemble for the current topology
            # Need to get natural frequencies first, same for all simulations.
            rng = np.random.default_rng(seed)
            natural_frequencies = rng.normal(0, sigma, N)

            if topology_name == 'all-to-all':
                # No adjacency matrix needed for all-to-all in KuramotoEnsemble, K is global
                A = None
            elif topology_name == 'random':
                # Generate Erdos-Renyi graph
                p = topology_params['random']['p']
                A = nt.generate_topology('erdos_renyi', N=N, p=p, seed=seed)
            elif topology_name == 'small-world':
                # Generate Watts-Strogatz graph
                k = topology_params['small-world']['k']
                p = topology_params['small-world']['p']
                A = nt.generate_topology('watts_strogatz', N=N, k=k, p=p, seed=seed)
            
            # K-values for the sweep
            k_values = np.linspace(K_init, K_max, steps)
            r_values = [] # Stores equilibrium order parameter R for each K

            for K_val in k_values:
                # Initialize Kuramoto ensemble with natural frequencies and adjacency matrix (if any)
                # KuramotoEnsemble expects `A` as its `coupling_matrix` argument
                # If A is None (all-to-all), it should default to all-to-all coupling
                # Let's check KuramotoEnsemble signature from guide or source if possible.
                # The guide only gives `simulate_kuramoto`, not `KuramotoEnsemble` directly with `A`.
                # Okay, I will use `simulate_kuramoto` and generate `A` if needed.
                # `simulate_kuramoto(N, K, T, dt, natural_frequencies=None, initial_phases=None, A=None)`
                # This is perfect!

                # Run simulation for a single K
                # We want the equilibrium order parameter R
                time_points, phases, order_param_magnitude, order_param_phase = \
                    cl_dynamics.simulate_kuramoto(N=N, K=K_val, T=(transient_steps + simulation_steps)*0.1, dt=0.1, 
                                        natural_frequencies=natural_frequencies, A=A)
                
                # Take the average R over the latter part of the simulation (after transient)
                equilibrium_r = np.mean(order_param_magnitude[-simulation_steps:])
                r_values.append(equilibrium_r)

            k_values = np.array(k_values)
            r_values = np.array(r_values)

            # Use bifurcation_cartography to extract critical exponent and critical K
            try:
                beta, K_crit = bc.extract_critical_exponent(k_values, r_values, window=5)
                print(f"Topology: {topology_name}, Detected K_c: {K_crit:.4f}, Detected beta: {beta:.4f}")
            except Exception as e:
                print(f"Error extracting critical exponent for {topology_name}: {e}")
                K_crit = None
                beta = None

            all_results[topology_name] = {
                "k_values": k_values.tolist(),
                "r_values": r_values.tolist(),
                "K_critical": K_crit,
                "beta_exponent": beta
            }

            # Plot R vs K for the current topology
            plt.figure(figsize=(10, 6))
            plt.plot(k_values, r_values, 'o-', label=f'{topology_name} Data')
            if K_crit is not None:
                R_at_Kc = np.interp(K_crit, k_values, r_values)
                plt.axvline(x=K_crit, color='r', linestyle='--', label=f'K_c = {K_crit:.4f}')
                plt.plot(K_crit, R_at_Kc, 'rx', markersize=10, label=f'({K_crit:.4f}, {R_at_Kc:.4f})')

            plt.xlabel("Coupling Strength (K)")
            plt.ylabel("Equilibrium Order Parameter (R)")
            plt.title(f"Kuramoto Model: Synchronization Transition ({topology_name} Topology)")
            plt.grid(True)
            plt.legend()
            output_dir = "topology_analysis_results"
            os.makedirs(output_dir, exist_ok=True)
            plt.savefig(os.path.join(output_dir, f"kuramoto_bifurcation_{topology_name}.png"))
            plt.close()
            print(f"Plot saved for {topology_name} to {os.path.join(output_dir, f'kuramoto_bifurcation_{topology_name}.png')}")

    except Exception as e:
        print(f"Failed to process topology {topology_name}: {e}")
        all_results[topology_name] = {"error": str(e)}

# Save all results to a single JSON file
output_dir = "topology_analysis_results"
os.makedirs(output_dir, exist_ok=True)
with open(os.path.join(output_dir, "kuramoto_topology_comparison.json"), 'w') as f:
    json.dump(all_results, f, indent=4)
print(f"All topology comparison results saved to {os.path.join(output_dir, 'kuramoto_topology_comparison.json')}")

# Create a combined plot for all topologies for comparison
plt.figure(figsize=(12, 8))
for topology_name, res in all_results.items():
    if "error" not in res:
        plt.plot(res["k_values"], res["r_values"], 'o-', label=f'{topology_name} (K_c: {res["K_critical"]:.2f})')
        if res["K_critical"] is not None:
            R_at_Kc = np.interp(res["K_critical"], np.array(res["k_values"]), np.array(res["r_values"]))
            plt.plot(res["K_critical"], R_at_Kc, 'x', markersize=8)

plt.xlabel("Coupling Strength (K)")
plt.ylabel("Equilibrium Order Parameter (R)")
plt.title("Kuramoto Model: Synchronization Transition Across Different Topologies")
plt.grid(True)
plt.legend()
plt.savefig(os.path.join(output_dir, "kuramoto_topology_comparison_plot.png"))
plt.close()
print(f"Combined comparison plot saved to {os.path.join(output_dir, 'kuramoto_topology_comparison_plot.png')}")
