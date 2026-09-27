"""
Investigating phase synchronization across different network topologies.
This script explores how network structure influences the critical coupling
strength for synchronization in the Kuramoto model.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors

def create_adjacency_matrix(N, topology='all-to-all'):
    """
    Create adjacency matrix for different network topologies.
    
    Parameters:
    N (int): Number of nodes
    topology (str): 'all-to-all', 'ring', 'scale-free', or 'small-world'
    
    Returns:
    np.ndarray: NxN adjacency matrix
    """
    A = np.zeros((N, N))
    
    if topology == 'all-to-all':
        # Complete graph
        A = np.ones((N, N)) - np.eye(N)
    
    elif topology == 'ring':
        # Ring/cycle topology (k-nearest neighbors, k=2)
        for i in range(N):
            A[i, (i-1) % N] = 1
            A[i, (i+1) % N] = 1
    
    elif topology == 'small-world':
        # Watts-Strogatz small-world network
        k = 4  # Each node connected to k nearest neighbors
        p = 0.3  # Rewiring probability
        
        # Start with ring lattice
        for i in range(N):
            for j in range(1, k//2 + 1):
                A[i, (i+j) % N] = 1
                A[i, (i-j) % N] = 1
        
        # Rewire some edges
        for i in range(N):
            for j in range(i+1, N):
                if A[i, j] == 1 and np.random.rand() < p:
                    A[i, j] = 0
                    A[j, i] = 0
                    new_j = np.random.randint(0, N)
                    while new_j == i or A[i, new_j] == 1:
                        new_j = np.random.randint(0, N)
                    A[i, new_j] = 1
                    A[new_j, i] = 1
    
    elif topology == 'scale-free':
        # Preferential attachment (Barabási-Albert)
        A[0, 1] = 1
        A[1, 0] = 1
        for i in range(2, N):
            degrees = np.sum(A[:i, :i], axis=1)
            probs = degrees / np.sum(degrees)
            targets = np.random.choice(i, size=2, replace=False, p=probs)
            for t in targets:
                A[i, t] = 1
                A[t, i] = 1
    
    return A

def simulate_kuramoto_network(N, A, omega, K, T, dt):
    """
    Simulate Kuramoto model on a network with adjacency matrix A.
    
    Parameters:
    N (int): Number of oscillators
    A (np.ndarray): Adjacency matrix
    omega (np.ndarray): Natural frequencies
    K (float): Global coupling strength
    T (float): Total time
    dt (float): Time step
    
    Returns:
    np.ndarray: Time series of phases
    """
    theta = 2 * np.pi * np.random.rand(N)
    t = np.arange(0, T, dt)
    phases = np.zeros((len(t), N))
    
    # Compute degree for each node
    degree = np.sum(A, axis=1)
    degree[degree == 0] = 1  # Avoid division by zero
    
    for idx, time in enumerate(t):
        dtheta = np.zeros(N)
        for i in range(N):
            coupling = 0
            for j in range(N):
                if A[i, j] > 0:
                    coupling += np.sin(theta[j] - theta[i])
            dtheta[i] = omega[i] + K * coupling / degree[i]
        
        theta += dtheta * dt
        theta = np.mod(theta, 2 * np.pi)
        phases[idx] = theta
    
    return phases

def compute_order_parameter(phases):
    """
    Compute the order parameter r(t), measuring synchronization.
    
    r(t) = |sum_j exp(i*theta_j(t))| / N
    """
    N = phases.shape[1]
    r = np.zeros(phases.shape[0])
    for t in range(phases.shape[0]):
        z = np.sum(np.exp(1j * phases[t]))
        r[t] = np.abs(z) / N
    return r

# Parameters
N = 50
omega = np.random.normal(0, 0.5, N)  # Heterogeneous natural frequencies
K_values = np.linspace(0, 3, 10)
T = 100
dt = 0.05
topologies = ['all-to-all', 'ring', 'small-world', 'scale-free']

# Run simulations for each topology and coupling strength
results = {}
for topology in topologies:
    print(f"Simulating {topology} topology...")
    sync_levels = []
    
    for K in K_values:
        A = create_adjacency_matrix(N, topology)
        phases = simulate_kuramoto_network(N, A, omega, K, T, dt)
        r = compute_order_parameter(phases)
        # Use the final 20% of the time series to measure steady-state synchronization
        sync_level = np.mean(r[-int(0.2 * len(r)):])
        sync_levels.append(sync_level)
    
    results[topology] = sync_levels

# Plot the results
fig, ax = plt.subplots(figsize=(10, 6))
for topology in topologies:
    ax.plot(K_values, results[topology], marker='o', label=topology)

ax.set_xlabel('Coupling Strength (K)')
ax.set_ylabel('Order Parameter <r>')
ax.set_title('Phase Synchronization Across Network Topologies')
ax.legend()
ax.grid(True, alpha=0.3)
fig.savefig('kuramoto_network_topologies.png', dpi=100)
print("Plot saved as kuramoto_network_topologies.png")

# Print summary
print("\nSummary of critical coupling strengths:")
for topology in topologies:
    # Find where r first exceeds 0.5
    sync = np.array(results[topology])
    if np.max(sync) > 0.5:
        idx = np.where(sync > 0.5)[0][0]
        K_crit = K_values[idx]
        print(f"{topology:15s}: K_crit ≈ {K_crit:.2f}")
    else:
        print(f"{topology:15s}: No synchronization achieved")
