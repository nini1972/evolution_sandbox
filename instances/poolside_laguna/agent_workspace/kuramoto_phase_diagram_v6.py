#!/usr/bin/env python3
"""
Kuramoto Phase Diagram: K-sigma Scan with Network Topology

Objective: Map the synchronization transition in (K, sigma) space for 4 topologies.
- Topologies: all_to_all, ring, small_world, scale_free
- For each topology, compute Laplacian spectral gap (lambda_2)
- Use ratified Kc(inf) = 4/pi (NOD-003)
- Resume from partial results if available
"""

import numpy as np
import networkx as nx
from scipy.sparse.linalg import eigsh
from scipy.sparse import csr_matrix
import time
import os
import json
from colony_lib.persistence import StageTracker

# ---------------------------
# Parameters
# ---------------------------
N = 128
K_values = np.linspace(0.5, 2.0, 60)  # Refined around 4/pi ≈ 1.2732
sigma_values = np.linspace(0.01, 1.0, 40)
realizations = 30
transient = 2000
measurement = 1000
dt = 0.05
seed = 42

# Topologies to scan
topologies = [
    ("all_to_all", None),
    ("ring", None),
    ("small_world", {"k": 4, "p": 0.1}),
    ("scale_free", {"alpha": 0.41, "beta": 0.54, "gamma": 0.05, "delta_in": 0.2, "delta_out": 0.0})
]

# Ratified Kc(inf) from NOD-003
Kc_inf = 4.0 / np.pi  # ≈ 1.2732

# ---------------------------
# Helper: Generate Topology
# ---------------------------
def generate_topology(name, params, N):
    if name == "all_to_all":
        G = nx.complete_graph(N)
    elif name == "ring":
        G = nx.cycle_graph(N)
    elif name == "small_world":
        G = nx.watts_strogatz_graph(N, params["k"], params["p"], seed=seed)
    elif name == "scale_free":
        G = nx.scale_free_graph(N, **params, seed=seed)
    else:
        raise ValueError(f"Unknown topology: {name}")
    return G

# ---------------------------
# Helper: Laplacian Spectral Gap
# ---------------------------
def spectral_gap(G):
    L = nx.laplacian_matrix(G)
    # Compute smallest 2 eigenvalues (FIX: use astype(float) instead of asfptype())
    eigvals = eigsh(L.astype(float), k=2, which='SM', return_eigenvectors=False)
    return eigvals[1]  # lambda_2

# ---------------------------
# Helper: Kuramoto Simulation
# ---------------------------
def simulate_kuramoto(G, K, sigma, seed_offset=0):
    np.random.seed(seed + seed_offset)
    N = G.number_of_nodes()
    
    # Natural frequencies
    omega = np.random.normal(0, sigma, N)
    
    # Adjacency matrix (normalized)
    A = nx.adjacency_matrix(G).astype(float)
    row_sums = A.sum(axis=1).A1
    row_sums[row_sums == 0] = 1  # avoid division by zero
    A = A / row_sums[:, None]
    
    # Initial phases
    theta = np.random.uniform(0, 2*np.pi, N)
    
    # Transient
    for _ in range(transient):
        dtheta = omega + K * np.sum(A @ np.sin(theta - theta[:, None]), axis=1)
        theta = (theta + dtheta * dt) % (2*np.pi)
    
    # Measurement
    order_param = np.zeros(measurement)
    for t in range(measurement):
        dtheta = omega + K * np.sum(A @ np.sin(theta - theta[:, None]), axis=1)
        theta = (theta + dtheta * dt) % (2*np.pi)
        order_param[t] = np.abs(np.mean(np.exp(1j * theta)))
    
    return np.mean(order_param), np.std(order_param)

# ---------------------------
# Main Scan
# ---------------------------
def main():
    stage_name = "kuramoto_phase_diagram_v5"
    tracker = StageTracker(stage_name)
    
    # Load partial results if resuming
    results = {}
    if tracker.is_done("init"):
        results = tracker.get_stage("results")
    else:
        for topo_name, topo_params in topologies:
            G = generate_topology(topo_name, topo_params, N)
            lambda_2 = spectral_gap(G)
            results[topo_name] = {
                "lambda_2": lambda_2,
                "Kc_empirical": None,
                "data": {}
            }
        tracker.save_stage("init", results)
    
    # Scan K-sigma space
    for topo_idx, (topo_name, topo_params) in enumerate(topologies):
        print(f"Topology: {topo_name} ({topo_idx+1}/{len(topologies)})")
        
        # Skip if already done
        if all(sigma in results[topo_name]["data"] for sigma in map(lambda x: f"{x:.3f}", sigma_values)):
            print(f"  Already complete.")
            continue
            
        G = generate_topology(topo_name, topo_params, N)
        lambda_2 = results[topo_name]["lambda_2"]
        
        for sigma in sigma_values:
            sigma_key = f"{sigma:.3f}"
            if sigma_key in results[topo_name]["data"]:
                print(f"  sigma={sigma:.3f} already done.")
                continue
                
            print(f"  sigma={sigma:.3f}")
            r_vals = []
            
            for r in range(realizations):
                r_mean, r_std = simulate_kuramoto(G, K_values, sigma, seed_offset=r)
                r_vals.append(r_mean)
            
            # Store results
            results[topo_name]["data"][sigma_key] = {
                "K_values": K_values.tolist(),
                "r_mean": np.mean(r_vals, axis=0).tolist(),
                "r_std": np.std(r_vals, axis=0).tolist()
            }
            
            # Save progress
            tracker.save_stage("results", results)
    
    # Final save
    tracker.save_stage("results", results)
    print("Scan complete. Results saved.")

if __name__ == "__main__":
    main()