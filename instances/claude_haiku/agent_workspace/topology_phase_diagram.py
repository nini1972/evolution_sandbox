#!/usr/bin/env python3
"""
Comprehensive phase diagram: Kuramoto critical coupling K_c as a function of 
network topology and noise level. Compare scaling exponents across topologies.

Goal: Verify if finite-size scaling exponent depends on topology.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.integrate import odeint
import json

# Import colony_lib
try:
    from colony_lib.dynamics import kuramoto_order_parameter
except ImportError:
    # Fallback: define it locally
    def kuramoto_order_parameter(theta):
        return np.abs(np.mean(np.exp(1j * theta)))

print("=" * 70)
print("TOPOLOGY PHASE DIAGRAM EXPERIMENT")
print("=" * 70)

# ============================================================================
# Network Topology Generators
# ============================================================================

def random_network(N, p=0.2):
    """Erdos-Renyi random network."""
    A = (np.random.rand(N, N) < p).astype(float)
    A = (A + A.T) / 2  # Symmetric
    np.fill_diagonal(A, 0)
    return A

def scale_free_network(N, m=2):
    """Preferential attachment (simplified Barabasi-Albert)."""
    A = np.zeros((N, N))
    degrees = np.zeros(N)
    for i in range(m, N):
        probs = degrees[:i] / (degrees[:i].sum() + 1e-10)
        targets = np.random.choice(i, m, p=probs, replace=False)
        for t in targets:
            A[i, t] = A[t, i] = 1
        degrees[i] += m
        degrees[targets] += 1
    return A

def lattice_network(side_len):
    """2D square lattice with periodic boundary (torus)."""
    N = side_len ** 2
    A = np.zeros((N, N))
    for i in range(N):
        row, col = divmod(i, side_len)
        neighbors = [
            ((row - 1) % side_len) * side_len + col,
            ((row + 1) % side_len) * side_len + col,
            row * side_len + ((col - 1) % side_len),
            row * side_len + ((col + 1) % side_len),
        ]
        for n in neighbors:
            A[i, n] = 1
    return A

def small_world_network(N, k=4, p=0.1):
    """Watts-Strogatz small-world."""
    A = np.zeros((N, N))
    # Ring lattice
    for i in range(N):
        for j in range(1, k // 2 + 1):
            A[i, (i + j) % N] = 1
            A[i, (i - j) % N] = 1
    A = (A + A.T) / 2
    # Rewiring
    for i in range(N):
        for j in range(i + 1, N):
            if A[i, j] > 0 and np.random.rand() < p:
                A[i, j] = A[j, i] = 0
                target = np.random.randint(N)
                while target == i or A[i, target] > 0:
                    target = np.random.randint(N)
                A[i, target] = A[target, i] = 1
    return A

# ============================================================================
# Kuramoto Dynamics
# ============================================================================

def kuramoto_order_parameter_direct(theta):
    """Compute order parameter R."""
    return np.abs(np.mean(np.exp(1j * theta)))

def kuramoto_rhs(theta, t, K, A, omega=None):
    """RHS for Kuramoto with coupling matrix A and coupling strength K."""
    N = len(theta)
    if omega is None:
        omega = np.zeros(N)
    
    # Adjacency-weighted coupling
    coupling = np.zeros(N)
    for i in range(N):
        for j in range(N):
            if A[i, j] > 0:
                coupling[i] += A[i, j] * np.sin(theta[j] - theta[i])
    
    dtheta = omega + (K / N) * coupling
    return dtheta

def find_critical_coupling(N, A, K_max=3.0, dt=0.01, tmax=200, tol=0.01):
    """
    Find K_c where order parameter first crosses threshold.
    """
    K_values = np.linspace(0.1, K_max, 50)
    R_values = []
    
    for K in K_values:
        theta0 = np.random.uniform(0, 2*np.pi, N)
        t_eval = np.linspace(0, tmax, int(tmax / dt))
        sol = odeint(kuramoto_rhs, theta0, t_eval, args=(K, A))
        
        # Average order parameter in final equilibrium window
        R_final = np.mean([kuramoto_order_parameter_direct(sol[i]) for i in range(-50, 0)])
        R_values.append(R_final)
    
    # Find threshold crossing (R > 0.3 as proxy for criticality)
    R_values = np.array(R_values)
    crosses = np.where(np.diff((R_values > 0.3).astype(int)) > 0)[0]
    
    if len(crosses) > 0:
        idx = crosses[0]
        K_c = K_values[idx]
    else:
        K_c = K_max  # Did not synchronize
    
    return K_c, R_values

# ============================================================================
# Main Experiment
# ============================================================================

topologies = {
    'random': lambda N: random_network(N, p=0.2),
    'scale_free': lambda N: scale_free_network(N, m=2),
    'lattice': lambda N: lattice_network(8) if N == 64 else lattice_network(7),  # N=49 or 64
    'small_world': lambda N: small_world_network(N, k=4, p=0.1),
}

sizes = [32, 64, 128]  # System sizes
num_trials = 3  # Trials per size per topology

results = {}

for topo_name, topo_gen in topologies.items():
    print(f"\nTesting topology: {topo_name}")
    results[topo_name] = {'N': [], 'K_c_mean': [], 'K_c_std': []}
    
    for N in sizes:
        K_c_samples = []
        for trial in range(num_trials):
            try:
                A = topo_gen(N)
                K_c, _ = find_critical_coupling(N, A, K_max=2.5)
                K_c_samples.append(K_c)
                print(f"  N={N}, trial={trial+1}: K_c={K_c:.4f}")
            except Exception as e:
                print(f"  N={N}, trial={trial+1}: ERROR - {str(e)}")
        
        if K_c_samples:
            K_c_mean = np.mean(K_c_samples)
            K_c_std = np.std(K_c_samples)
            results[topo_name]['N'].append(N)
            results[topo_name]['K_c_mean'].append(K_c_mean)
            results[topo_name]['K_c_std'].append(K_c_std)

# ============================================================================
# Visualization
# ============================================================================

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: K_c vs N for each topology
ax = axes[0]
for topo_name, data in results.items():
    N_vals = np.array(data['N'])
    K_c_vals = np.array(data['K_c_mean'])
    K_c_err = np.array(data['K_c_std'])
    ax.errorbar(N_vals, K_c_vals, yerr=K_c_err, marker='o', label=topo_name, capsize=5)

ax.set_xlabel('System size N', fontsize=12)
ax.set_ylabel('Critical coupling K_c', fontsize=12)
ax.set_title('Critical Coupling vs Topology', fontsize=13, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xscale('log')

# Plot 2: Scaling exponent comparison
ax = axes[1]
exponents = []
topo_names_list = []
for topo_name, data in results.items():
    if len(data['N']) >= 2:
        N_vals = np.array(data['N'])
        K_c_vals = np.array(data['K_c_mean'])
        # Fit: K_c = K_c_inf - alpha * N^(-beta)
        log_fit = np.polyfit(np.log(N_vals), np.log(K_c_vals), 1)
        exponent = log_fit[0]
        exponents.append(exponent)
        topo_names_list.append(topo_name)
        print(f"{topo_name}: scaling exponent approx {exponent:.3f}")

ax.bar(topo_names_list, exponents)
ax.set_ylabel('Scaling exponent (d log K_c / d log N)', fontsize=12)
ax.set_title('Finite-Size Scaling by Topology', fontsize=13, fontweight='bold')
ax.axhline(y=-0.363, color='r', linestyle='--', label='Canonical -0.363')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('topology_phase_diagram.png', dpi=150, bbox_inches='tight')
print("\nPlot saved to topology_phase_diagram.png")

# Save results as JSON
with open('topology_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nResults saved to topology_results.json")
print("=" * 70)
