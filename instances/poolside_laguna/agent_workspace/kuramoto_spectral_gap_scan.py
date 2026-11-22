#!/usr/bin/env python3
"""
Scan Kuramoto oscillators for spectral gap → synchronization relationship.

Hypothesis: Algebraic connectivity (λ₂) predicts critical coupling K_c.
"""

import numpy as np
from colony_lib.network_topology import generate_topology, laplacian_spectrum, algebraic_connectivity
from colony_lib.dynamics import simulate_kuramoto
from colony_lib.persistence import StageTracker


def scan_spectral_gap_vs_sync(N=64, topologies=['erdos_renyi', 'barabasi_albert', 'watts_strogatz'], K_range=np.linspace(0.1, 5.0, 20), seed=42):
    """Scan spectral gap (λ₂) vs. synchronization for multiple topologies."""
    np.random.seed(seed)
    results = []
    
    for topology in topologies:
        print(f"Generating {topology} topology...")
        A = generate_topology(topology, N, seed=seed)
        evals = laplacian_spectrum(A)
        lambda_2 = algebraic_connectivity(A)
        
        for K in K_range:
            print(f"Simulating K={K:.2f}...")
            phases = simulate_kuramoto(A, K, T=10.0, dt=0.01, seed=seed)
            order_param = np.abs(np.mean(np.exp(1j * phases)))
            
            results.append({
                "topology": topology,
                "N": N,
                "K": K,
                "lambda_2": lambda_2,
                "order_param": order_param,
                "synchronized": order_param > 0.9,
            })
    
    return results


def fit_critical_coupling(results):
    """Fit critical coupling K_c vs. λ₂."""
    from scipy.optimize import curve_fit
    
    def linear_model(x, a, b):
        return a * x + b
    
    lambda_2 = np.array([r["lambda_2"] for r in results])
    K_c = np.array([r["K"] for r in results if r["synchronized"]][0])  # First K where order_param > 0.9
    
    popt, _ = curve_fit(linear_model, lambda_2, K_c)
    return popt


if __name__ == "__main__":
    results = scan_spectral_gap_vs_sync()
    np.save("kuramoto_spectral_gap_scan.npy", results)
    
    # Persist results
    tracker = StageTracker("kuramoto_spectral_gap_scan")
    tracker.save_stage("final", results)
    
    print("Scan complete. Results saved to kuramoto_spectral_gap_scan.npy")