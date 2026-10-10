"""
Phase 2b: Multi-Topology Kuramoto Scaling with Adaptive K_max
==============================================================

Bug Fix: K_c was a dict, not a scalar. Now returns float K_c values.

Hypothesis: K_c ~ N^α, where α may depend on network topology.
Adaptive K_max per topology to avoid saturation.

Topologies:
  - ER (Erdős-Rényi, p=0.3): sparse, random
  - Ring1D (cycle graph): sparse, regular
  - Ring2D (grid graph): sparse, 2D
  - SmallWorld (Watts-Strogatz): sparse, clustered
  - Complete (full graph): dense

System sizes: N ∈ {16, 32, 64}
"""

import numpy as np
import json
import networkx as nx
from scipy.integrate import odeint

def create_topology(name, N):
    """Create network topology."""
    if name == 'ER':
        return nx.erdos_renyi_graph(N, 0.3)
    elif name == 'Ring1D':
        return nx.cycle_graph(N)
    elif name == 'Ring2D':
        side = int(np.sqrt(N))
        return nx.grid_2d_graph(side, side)
    elif name == 'SmallWorld':
        return nx.watts_strogatz_graph(N, 4, 0.3)
    elif name == 'Complete':
        return nx.complete_graph(N)
    else:
        raise ValueError(f"Unknown topology: {name}")

def get_adjacency_matrix(G):
    """Convert NetworkX graph to adjacency matrix, handling 2D node labels."""
    adj = np.array(nx.adjacency_matrix(G).todense())
    return adj

def kuramoto_ode(theta, t, adj, K):
    """ODE for Kuramoto model."""
    N = len(theta)
    dtheta = np.zeros(N)
    
    for i in range(N):
        coupling = 0.0
        degree = np.sum(adj[i, :])
        
        if degree > 0:
            for j in range(N):
                if adj[i, j] > 0:
                    coupling += np.sin(theta[j] - theta[i])
            dtheta[i] = K * coupling / degree
    
    return dtheta

def measure_order_parameter(theta):
    """Kuramoto order parameter R."""
    N = len(theta)
    R = np.sqrt(np.mean(np.sin(theta))**2 + np.mean(np.cos(theta))**2)
    return R

def find_critical_coupling(adj, K_max, num_K_points=60, num_seeds=3):
    """
    Find K_c by measuring R(K) and finding where R transitions from <0.5 to >=0.5.
    
    Returns:
        K_c (float): Critical coupling strength
        R_array (array): R values at each K tested
        K_array (array): K values tested
    """
    N = len(adj)
    t_eval = np.linspace(0, 50, 200)
    K_array = np.linspace(0.01, K_max, num_K_points)
    
    R_by_seed = []
    
    for seed in range(num_seeds):
        np.random.seed(seed)
        theta_init = np.zeros(N)  # Synchronized initial condition
        
        R_at_K = []
        for K in K_array:
            try:
                sol = odeint(kuramoto_ode, theta_init, t_eval, args=(adj, K),
                           rtol=1e-6, atol=1e-8, full_output=False)
                R_final = measure_order_parameter(sol[-1])
                R_at_K.append(R_final)
            except:
                R_at_K.append(0.0)
        
        R_by_seed.append(R_at_K)
    
    # Average over seeds
    R_array = np.mean(R_by_seed, axis=0)
    
    # Find K_c: crossing of R = 0.5
    crossing_indices = np.where(np.diff(np.sign(R_array - 0.5)) != 0)[0]
    
    if len(crossing_indices) > 0:
        idx = crossing_indices[0]
        K1, K2 = K_array[idx], K_array[idx + 1]
        R1, R2 = R_array[idx], R_array[idx + 1]
        
        # Linear interpolation
        if R2 != R1:
            K_c = K1 + (0.5 - R1) * (K2 - K1) / (R2 - R1)
        else:
            K_c = (K1 + K2) / 2.0
    else:
        # No crossing detected
        if R_array[-1] < 0.5:
            K_c = K_max * 0.95
        else:
            # Find first K where R >= 0.3
            idx = np.where(R_array >= 0.3)[0]
            if len(idx) > 0:
                K_c = K_array[idx[0]]
            else:
                K_c = 0.01
    
    return float(K_c), np.array(R_array), np.array(K_array)

def main():
    print("=" * 80)
    print("PHASE 2B: Multi-Topology Kuramoto Scaling (Adaptive K_max)")
    print("=" * 80)
    
    topologies = ['ER', 'Ring1D', 'SmallWorld', 'Complete']
    system_sizes = [16, 32, 64]
    
    # Adaptive K_max per topology
    K_max_dict = {
        'ER': 200.0,
        'Ring1D': 300.0,
        'SmallWorld': 150.0,
        'Complete': 50.0,
    }
    
    results = {}
    
    for topo in topologies:
        print(f"\n{'=' * 80}")
        print(f"TOPOLOGY: {topo}")
        print(f"{'=' * 80}")
        
        K_c_list = []
        N_list = []
        
        K_max = K_max_dict[topo]
        
        for N in system_sizes:
            print(f"  N = {N:3d} (K_max={K_max:.1f}): ", end='', flush=True)
            
            try:
                G = create_topology(topo, N)
                adj = get_adjacency_matrix(G)
                
                K_c, R_array, K_array = find_critical_coupling(adj, K_max, num_K_points=60, num_seeds=3)
                
                print(f"K_c = {K_c:.6f}")
                
                K_c_list.append(float(K_c))
                N_list.append(N)
                
            except Exception as e:
                print(f"FAILED: {e}")
                continue
        
        if len(K_c_list) >= 2:
            # Compute scaling exponent: K_c ~ N^α
            log_N = np.log(np.array(N_list, dtype=float))
            log_K_c = np.log(np.array(K_c_list))
            
            coeffs = np.polyfit(log_N, log_K_c, 1)
            alpha = float(coeffs[0])
            
            print(f"\n  Scaling Analysis:")
            print(f"    N values: {N_list}")
            print(f"    K_c values: {[f'{k:.6f}' for k in K_c_list]}")
            print(f"    log(K_c) = {alpha:.6f} * log(N) + {coeffs[1]:.6f}")
            print(f"    Scaling exponent α = {alpha:.6f}")
        else:
            alpha = None
            print(f"\n  [WARNING] Insufficient data for scaling analysis (only {len(K_c_list)} points)")
        
        results[topo] = {
            'N': N_list,
            'K_c': K_c_list,
            'alpha': alpha,
            'K_max_used': K_max,
        }
    
    # Print summary
    print(f"\n\n{'=' * 80}")
    print("SUMMARY: SCALING EXPONENTS α (Canonical: α ≈ -0.363)")
    print(f"{'=' * 80}\n")
    
    for topo in topologies:
        if topo in results and results[topo]['alpha'] is not None:
            alpha = results[topo]['alpha']
            delta = alpha - (-0.363)
            print(f"  {topo:15s}: α = {alpha:+.6f}  (Δα = {delta:+.6f})")
        else:
            print(f"  {topo:15s}: [NO DATA]")
    
    # Save results
    with open('phase2b_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n[*] Results saved to phase2b_results.json\n")

if __name__ == '__main__':
    main()
