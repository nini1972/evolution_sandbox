#!/usr/bin/env python3
"""
Debug Kuramoto Simulation: Minimal Test Case

Objective: Test a single topology (all_to_all) with N=64, 10 K values, 5 sigma values.
- Add explicit logging.
- Profile memory usage.
- Catch silent errors.
"""

import numpy as np
import networkx as nx
import time
import logging
import tracemalloc

# ---------------------------
# Logging Setup
# ---------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ---------------------------
# Parameters
# ---------------------------
N = 64
K_values = np.linspace(0.5, 2.0, 10)
sigma_values = np.linspace(0.01, 1.0, 5)
realizations = 3
transient = 500
measurement = 200
dt = 0.05
seed = 42

topology = "all_to_all"

# ---------------------------
# Helper: Generate Topology
# ---------------------------
def generate_topology(name, N):
    if name == "all_to_all":
        G = nx.complete_graph(N)
    elif name == "ring":
        G = nx.cycle_graph(N)
    else:
        raise ValueError(f"Unknown topology: {name}")
    return G

# ---------------------------
# Helper: Kuramoto Simulation (Debug)
# ---------------------------
def simulate_kuramoto(G, K, sigma, seed_offset=0):
    try:
        tracemalloc.start()
        np.random.seed(seed + seed_offset)
        N = G.number_of_nodes()
        
        # Memory check
        current_mem, peak_mem = tracemalloc.get_traced_memory()
        logger.info(f"Memory before simulation: {peak_mem / 1024:.2f} KB")
        
        # Natural frequencies
        omega = np.random.normal(0, sigma, N)
        
        # Adjacency matrix (normalized)
        A = nx.adjacency_matrix(G).astype(float)
        row_sums = A.sum(axis=1)
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
        
        # Memory check
        current_mem, peak_mem = tracemalloc.get_traced_memory()
        logger.info(f"Memory after simulation: {peak_mem / 1024:.2f} KB")
        tracemalloc.stop()
        
        return np.mean(order_param), np.std(order_param)
    except Exception as e:
        logger.error(f"Error in simulate_kuramoto: {e}")
        raise

# ---------------------------
# Main Debug
# ---------------------------
def main():
    logger.info(f"Starting debug for topology: {topology}")
    G = generate_topology(topology, N)
    
    results = {}
    for sigma in sigma_values:
        sigma_key = f"{sigma:.3f}"
        logger.info(f"Testing sigma={sigma:.3f}")
        results[sigma_key] = {
            "K_values": K_values.tolist(),
            "r_mean": [],
            "r_std": []
        }
        
        for K in K_values:
            r_vals = []
            for r in range(realizations):
                r_mean, r_std = simulate_kuramoto(G, K, sigma, seed_offset=r)
                r_vals.append(r_mean)
            
            results[sigma_key]["r_mean"].append(np.mean(r_vals))
            results[sigma_key]["r_std"].append(np.std(r_vals))
    
    logger.info("Debug complete. Results:")
    logger.info(results)
    
    # Save results
    import json
    with open("debug_kuramoto_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info("Results saved to debug_kuramoto_results.json")

if __name__ == "__main__":
    main()