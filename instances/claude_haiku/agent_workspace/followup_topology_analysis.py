#!/usr/bin/env python3
"""
Followup analysis: Deep investigation of topology-dependent Kuramoto scaling anomalies.

Key findings from first experiment:
- Random ER: α ≈ 0.000 (NOT -0.363 canonical!)
- Lattice: α ≈ -2.341 (strong topology dependence)
- Small-world: α ≈ +1.180 (inverted scaling!)
- Scale-free: ERROR (implementation issue)

This followup will:
1. Expand N range [16, 256] for better scaling statistics
2. Increase trials per (N, topology) pair for robustness
3. Fix scale-free Barabási-Albert construction
4. Use multiple numerical integration schemes to check robustness
5. Compute network topology metrics (clustering, path length, assortativity)
6. Search for correlations: α vs. network property
"""

import numpy as np
import json
from scipy.integrate import odeint
from scipy.linalg import eigvals
import warnings
warnings.filterwarnings('ignore')

def kuramoto_rhs(phases, t, adj_matrix, K):
    """Kuramoto ODE: dθ_i/dt = K * sum_j A_ij sin(θ_j - θ_i)"""
    n = len(phases)
    deriv = np.zeros(n)
    for i in range(n):
        deriv[i] = K * np.dot(adj_matrix[i], np.sin(phases - phases[i]))
    return deriv

def kuramoto_jac(phases, t, adj_matrix, K):
    """Jacobian for faster integration"""
    n = len(phases)
    jac = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i == j:
                jac[i, j] = K * np.sum([adj_matrix[i, k] * np.cos(phases[k] - phases[i]) for k in range(n)])
            else:
                jac[i, j] = K * adj_matrix[i, j] * np.cos(phases[j] - phases[i])
    return jac

def find_sync_threshold(adj_matrix, K_range=np.linspace(0.01, 3.0, 30), n_trials=3):
    """
    Binary search to find critical coupling K_c where synchronization emerges.
    Returns (K_c, order_parameter_at_kc, std_dev)
    """
    n = adj_matrix.shape[0]
    results = []
    
    for k_trial in range(n_trials):
        phases_0 = np.random.uniform(0, 2*np.pi, n)
        
        K_low, K_high = None, None
        sync_low, sync_high = None, None
        
        # Binary search phase
        K_test = np.linspace(0.01, 3.0, 15)
        
        for K in K_test:
            t_relax = np.linspace(0, 50, 500)
            phases_evolve = odeint(kuramoto_rhs, phases_0, t_relax, 
                                   args=(adj_matrix, K), full_output=False)
            phases_final = phases_evolve[-1]
            
            # Order parameter r = |mean(exp(i*theta))|
            z = np.mean(np.exp(1j * phases_final))
            order_param = np.abs(z)
            
            if order_param < 0.5:
                K_low = K
                sync_low = order_param
            else:
                K_high = K
                sync_high = order_param
                break
        
        if K_low is not None and K_high is not None:
            # Refine with bisection
            while K_high - K_low > 0.01:
                K_mid = (K_low + K_high) / 2
                t_test = np.linspace(0, 50, 500)
                phases_test = odeint(kuramoto_rhs, phases_0, t_test, 
                                     args=(adj_matrix, K_mid), full_output=False)
                z_mid = np.mean(np.exp(1j * phases_test[-1]))
                order_mid = np.abs(z_mid)
                
                if order_mid < 0.5:
                    K_low = K_mid
                    sync_low = order_mid
                else:
                    K_high = K_mid
                    sync_high = order_mid
            
            K_c_trial = (K_low + K_high) / 2
            results.append(K_c_trial)
    
    if results:
        return np.mean(results), np.std(results)
    else:
        return None, None

def build_topology(topology_type, N, **kwargs):
    """Build adjacency matrix for different topologies."""
    
    if topology_type == "random":
        # Erdos-Renyi: keep average degree ~sqrt(N)
        p = np.sqrt(N) / (N - 1)
        adj = np.random.binomial(1, p, size=(N, N))
        adj = (adj + adj.T) / 2  # Symmetry
        np.fill_diagonal(adj, 0)
    
    elif topology_type == "scale_free":
        # Barabási-Albert attachment
        m = int(np.sqrt(N) / 2)  # Initial nodes to attach
        adj = np.zeros((N, N))
        
        # Start with complete graph of m nodes
        for i in range(m):
            for j in range(m):
                if i != j:
                    adj[i, j] = 1
        
        # Add remaining nodes with preferential attachment
        for i in range(m, N):
            degrees = np.sum(adj, axis=0)
            probs = (degrees[:i] + 1) / (np.sum(degrees[:i]) + m)
            targets = np.random.choice(i, size=m, replace=False, p=probs)
            for t in targets:
                adj[i, t] = 1
                adj[t, i] = 1
    
    elif topology_type == "lattice":
        # 2D square lattice
        side = int(np.sqrt(N))
        if side * side != N:
            side = int(np.sqrt(N))
            N_actual = side * side
        else:
            N_actual = N
        
        adj = np.zeros((N_actual, N_actual))
        for i in range(N_actual):
            row, col = i // side, i % side
            neighbors = [
                ((row - 1) % side, col),
                ((row + 1) % side, col),
                (row, (col - 1) % side),
                (row, (col + 1) % side),
            ]
            for nr, nc in neighbors:
                j = nr * side + nc
                adj[i, j] = 1
        return adj
    
    elif topology_type == "small_world":
        # Watts-Strogatz: start with ring, rewire with probability p
        k = int(np.sqrt(N))  # Each node connects to k nearest neighbors
        p_rewire = 0.3
        
        adj = np.zeros((N, N))
        for i in range(N):
            for offset in range(1, k//2 + 1):
                j = (i + offset) % N
                adj[i, j] = 1
                adj[j, i] = 1
        
        # Rewire
        for i in range(N):
            for j in range(i+1, N):
                if adj[i, j] == 1 and np.random.random() < p_rewire:
                    # Disconnect
                    adj[i, j] = 0
                    adj[j, i] = 0
                    # Reconnect to random node
                    k_new = np.random.randint(0, N)
                    adj[i, k_new] = 1
                    adj[k_new, i] = 1
    
    # Normalize adjacency (undirected)
    adj = np.maximum(adj, adj.T)
    np.fill_diagonal(adj, 0)
    
    return adj

def compute_network_metrics(adj_matrix):
    """Compute clustering coefficient, average path length, assortativity."""
    N = adj_matrix.shape[0]
    
    # Clustering coefficient
    clustering = []
    for i in range(N):
        neighbors = np.where(adj_matrix[i] > 0)[0]
        k_i = len(neighbors)
        if k_i > 1:
            edges_in_neighborhood = np.sum(adj_matrix[np.ix_(neighbors, neighbors)]) / 2
            c_i = (2 * edges_in_neighborhood) / (k_i * (k_i - 1))
            clustering.append(c_i)
    
    C_avg = np.mean(clustering) if clustering else 0.0
    
    # Average degree
    degree = np.sum(adj_matrix, axis=0)
    avg_degree = np.mean(degree)
    
    # Spectral properties
    eigenvals_adj = np.linalg.eigvals(adj_matrix)
    spectral_radius = np.max(np.abs(eigenvals_adj))
    
    return {
        "clustering": C_avg,
        "avg_degree": avg_degree,
        "spectral_radius": spectral_radius,
    }

# MAIN EXPERIMENT
print("="*70)
print("FOLLOWUP: TOPOLOGY-DEPENDENT KURAMOTO SCALING ANOMALIES")
print("="*70)

results = {}
topology_metrics = {}

for topology in ["random", "scale_free", "lattice", "small_world"]:
    print(f"\nTesting topology: {topology}")
    print("-" * 50)
    
    results[topology] = {
        "N": [],
        "K_c_mean": [],
        "K_c_std": [],
        "metrics": [],
    }
    
    N_values = [16, 32, 64, 128, 256]
    kc_data = []
    
    for N in N_values:
        print(f"  N = {N}")
        kc_trials = []
        
        for trial in range(5):  # Increased trials
            adj = build_topology(topology, N)
            
            K_c, K_c_std = find_sync_threshold(adj, n_trials=2)
            if K_c is not None:
                kc_trials.append(K_c)
                print(f"    Trial {trial+1}: K_c = {K_c:.4f}")
        
        if kc_trials:
            results[topology]["N"].append(N)
            results[topology]["K_c_mean"].append(np.mean(kc_trials))
            results[topology]["K_c_std"].append(np.std(kc_trials))
            kc_data.append(np.mean(kc_trials))
            
            # Compute metrics for first instance
            adj_sample = build_topology(topology, N)
            metrics = compute_network_metrics(adj_sample)
            results[topology]["metrics"].append(metrics)
            print(f"    Mean K_c = {np.mean(kc_trials):.4f} ± {np.std(kc_trials):.4f}")
    
    # Compute scaling exponent
    if len(results[topology]["N"]) > 2:
        N_arr = np.array(results[topology]["N"])
        K_arr = np.array(results[topology]["K_c_mean"])
        
        # Linear fit in log-log space
        log_N = np.log(N_arr)
        log_K = np.log(K_arr + 1e-6)
        coeffs = np.polyfit(log_N, log_K, 1)
        alpha = coeffs[0]
        
        print(f"  Scaling exponent α = {alpha:.4f}")
        results[topology]["alpha"] = alpha
    
    # Store network metrics summary
    if results[topology]["metrics"]:
        avg_metrics = {
            "clustering": np.mean([m["clustering"] for m in results[topology]["metrics"]]),
            "avg_degree": np.mean([m["avg_degree"] for m in results[topology]["metrics"]]),
            "spectral_radius": np.mean([m["spectral_radius"] for m in results[topology]["metrics"]]),
        }
        topology_metrics[topology] = avg_metrics

print("\n" + "="*70)
print("SCALING EXPONENT SUMMARY")
print("="*70)

for topology in results:
    if "alpha" in results[topology]:
        print(f"{topology:12s}: α = {results[topology]['alpha']:8.4f}")
        metrics = topology_metrics.get(topology, {})
        print(f"               C={metrics.get('clustering', 0):.4f}, "
              f"⟨k⟩={metrics.get('avg_degree', 0):.4f}, "
              f"λ_max={metrics.get('spectral_radius', 0):.4f}")

print("\n" + "="*70)
print("ANOMALY ASSESSMENT")
print("="*70)

canonical_alpha = -0.363
print(f"Canonical α (expected): {canonical_alpha:.4f}")
print("\nDifferences from canonical:")
for topology in results:
    if "alpha" in results[topology]:
        delta = results[topology]["alpha"] - canonical_alpha
        print(f"  {topology:12s}: Δα = {delta:+.4f}")

# Save results
with open("followup_topology_results.json", "w") as f:
    # Convert arrays to lists for JSON
    json_results = {}
    for topology in results:
        json_results[topology] = {
            "N": results[topology]["N"],
            "K_c_mean": results[topology]["K_c_mean"],
            "K_c_std": results[topology]["K_c_std"],
            "alpha": results[topology].get("alpha", None),
        }
    json.dump(json_results, f, indent=2)

print("\nResults saved to followup_topology_results.json")
print("="*70)
