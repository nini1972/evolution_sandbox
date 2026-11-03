"""
Network Topology Phase Diagrams for Kuramoto Model
- 4 topologies: all-to-all, ring, small-world, scale-free
- Parameter sweep: K (coupling), sigma (heterogeneity)
- Ensemble averaging: 30 realizations per point
- Observable: steady-state order parameter r(inf)
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx
from colony_lib.network_topology import generate_topology


def kuramoto_order_parameter(theta):
    """Compute Kuramoto order parameter R and mean phase psi."""
    z = np.mean(np.exp(1j * theta))
    return np.abs(z), np.angle(z)


def simulate_kuramoto(N, K, sigma, topology, seed, T_transient=100, T_steady=50, dt=0.05):
    """Simulate Kuramoto model on a given topology."""
    rng = np.random.default_rng(seed)
    omega = rng.normal(0, sigma, N)
    theta = rng.uniform(0, 2*np.pi, N)
    
    # Generate topology
    A = generate_topology(topology, N, seed=seed)
    
    # Simulation
    t_total = int((T_transient + T_steady) / dt)
    for _ in range(t_total):
        R, psi = kuramoto_order_parameter(theta)
        coupling = K * np.sum(A * np.sin(theta[:, None] - theta[None, :]), axis=1) / N
        theta = (theta + dt * (omega + coupling)) % (2*np.pi)
    
    # Measure steady-state order parameter
    R_final, _ = kuramoto_order_parameter(theta)
    return R_final


def main():
    # Parameters
    N = 60
    K_values = np.linspace(0.1, 4.0, 60)
    sigma_values = np.linspace(0.05, 1.5, 40)
    topologies = ['all_to_all', 'ring', 'small_world', 'scale_free']
    n_realizations = 30
    
    print(f"Parameter grid: {len(K_values)} K values x {len(sigma_values)} sigma values")
    print(f"Topologies: {topologies}")
    print(f"Realizations per point: {n_realizations}")
    
    # Phase diagram storage
    phase_diagrams = {topo: np.zeros((len(sigma_values), len(K_values))) for topo in topologies}
    
    # Sweep
    for i, sigma in enumerate(sigma_values):
        for j, K in enumerate(K_values):
            for topo in topologies:
                R_ensemble = []
                for r in range(n_realizations):
                    seed = i * 10000 + j * 100 + r
                    R = simulate_kuramoto(N, K, sigma, topo, seed)
                    R_ensemble.append(R)
                phase_diagrams[topo][i, j] = np.mean(R_ensemble)
        print(f"sigma={sigma:.3f} done")
    
    # Plot phase diagrams
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.ravel()
    for idx, topo in enumerate(topologies):
        ax = axes[idx]
        im = ax.pcolormesh(K_values, sigma_values, phase_diagrams[topo], shading='auto', cmap='viridis')
        ax.set_title(f'{topo.replace("_", " ").title()}', fontsize=12)
        ax.set_xlabel('Coupling K', fontsize=10)
        ax.set_ylabel('Heterogeneity sigma', fontsize=10)
        plt.colorbar(im, ax=ax, label='Order Parameter R')
    plt.tight_layout()
    plt.savefig('kuramoto_phase_diagrams_4topology.png', dpi=200)
    plt.close()
    print("Saved kuramoto_phase_diagrams_4topology.png")
    
    # Extract critical coupling Kc (R=0.5)
    Kc_results = {}
    for topo in topologies:
        Kc_sigma = []
        for i, sigma in enumerate(sigma_values):
            R_sigma = phase_diagrams[topo][i, :]
            # Find K where R crosses 0.5
            Kc = None
            for j in range(1, len(K_values)):
                if R_sigma[j] > 0.5 and R_sigma[j-1] < 0.5:
                    Kc = K_values[j]
                    break
            if Kc is None:
                Kc = K_values[-1]
            Kc_sigma.append(Kc)
        Kc_results[topo] = np.array(Kc_sigma)
        print(f"{topo}: Kc extraction done")
    
    # Plot Kc vs sigma
    plt.figure(figsize=(10, 6))
    for topo in topologies:
        plt.plot(sigma_values, Kc_results[topo], 'o-', label=topo.replace("_", " ").title())
    plt.xlabel('Heterogeneity sigma', fontsize=12)
    plt.ylabel('Critical Coupling Kc', fontsize=12)
    plt.title('Critical Coupling vs Heterogeneity for Different Topologies', fontsize=14)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('kuramoto_Kc_vs_sigma.png', dpi=150)
    plt.close()
    print("Saved kuramoto_Kc_vs_sigma.png")
    
    # Save results
    np.savez('kuramoto_phase_diagram_results.npz', 
             K_values=K_values, sigma_values=sigma_values, 
             phase_diagrams=phase_diagrams, Kc_results=Kc_results)
    print("Saved kuramoto_phase_diagram_results.npz")


if __name__ == "__main__":
    main()