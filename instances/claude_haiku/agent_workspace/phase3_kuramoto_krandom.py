#!/usr/bin/env python3
"""
Phase 3: Kuramoto Synchronization on k-Regular Random Graphs
Hypothesis: Scaling exponent α(k) depends on coordination number k

RATIONALE:
- Phase 2d found positive α ≈ +2.54 for Ring 1D (k=2 lattice)
- Phase 2d found α ≈ 0 for dense/complete graphs
- Canonical α = -0.363 comes from sparse RANDOM graphs
- QUESTION: Does α transition smoothly from lattice to random?
            Or are they fundamentally different universality classes?

DESIGN:
- Test k-regular RANDOM graphs at k = 2, 3, 4, 5, 6, 8
- Sizes: N = 16, 32, 64, 128 (small but sufficient for trend)
- Binary search for K_c at each (k, N) pair
- Ensemble: 30 random graph seeds per (k, N) to get mean K_c
- Expected: α(k) should show clear trend as function of coordination
"""

import json
import numpy as np
from collections import defaultdict

# ============================================================================
# HELPER: Generate k-regular random graph (configuration model)
# ============================================================================
def generate_krandom_graph(N, k):
    """
    Generate k-regular random graph using configuration model.
    Returns adjacency matrix (symmetric, 0-1 binary).
    
    Parameters:
      N: number of nodes
      k: coordination number (degree of each node)
    
    Returns:
      A: (N, N) symmetric binary adjacency matrix
    """
    if (N * k) % 2 != 0:
        # k*N must be even for k-regular graph to exist
        # If not, reduce k slightly
        k_actual = k if (N * k) % 2 == 0 else k - 1
    else:
        k_actual = k
    
    # Chvátal-Sankar algorithm: generate random k-regular graph
    max_tries = 100
    for attempt in range(max_tries):
        # Create stubs (half-edges)
        stubs = []
        for i in range(N):
            stubs.extend([i] * k_actual)
        
        # Shuffle and pair up stubs randomly
        np.random.shuffle(stubs)
        
        # Try to form edges
        A = np.zeros((N, N), dtype=int)
        valid = True
        
        for i in range(0, len(stubs), 2):
            u, v = stubs[i], stubs[i+1]
            if u == v or A[u, v] != 0:  # Self-loop or multi-edge
                valid = False
                break
            A[u, v] = 1
            A[v, u] = 1
        
        if valid:
            return A
    
    # Fallback: return approximate k-regular (may have slightly varied degrees)
    return A

# ============================================================================
# HELPER: Kuramoto dynamics
# ============================================================================
def kuramoto_order_parameter(phases, dt=0.01, T=100):
    """
    Simulate Kuramoto model with pairwise coupling on topology A.
    
    Returns: mean order parameter R_avg over last 50% of time
    """
    N = len(phases)
    omega = np.zeros(N)  # Natural frequencies (all zero for now)
    
    phases = phases.copy()
    
    # Integrate
    t = 0
    R_samples = []
    while t < T:
        # Compute pairwise interactions
        phase_diffs = phases[:, np.newaxis] - phases[np.newaxis, :]
        
        # Kuramoto coupling: sum K * sin(phi_j - phi_i)
        # (computed in loop over edges for efficiency)
        dphase_dt = np.zeros(N)
        for i in range(N):
            for j in range(i+1, N):
                if A_current[i, j] > 0:
                    coupling = K_current * np.sin(phases[j] - phases[i])
                    dphase_dt[i] += coupling
                    dphase_dt[j] -= coupling
        
        phases += dphase_dt * dt
        phases = phases % (2 * np.pi)
        
        # Record order parameter
        R = np.abs(np.mean(np.exp(1j * phases)))
        R_samples.append(R)
        
        t += dt
    
    # Return mean from steady state (last 50%)
    return np.mean(R_samples[len(R_samples)//2:])

# ============================================================================
# HELPER: Binary search for K_c
# ============================================================================
def find_critical_coupling_binary_search(A, N, K_min=0.1, K_max=30, tolerance=0.05):
    """
    Binary search for K_c where order parameter transitions from ~0 to significant.
    
    Criterion: R_avg > 0.3 indicates synchronized state
    """
    global A_current, K_current
    
    K_low = K_min
    K_high = K_max
    K_c = None
    
    for iteration in range(15):  # ~log2(K_max/K_min) iterations
        K_test = (K_low + K_high) / 2
        K_current = K_test
        A_current = A
        
        # Sample R at this K (average over multiple initial conditions)
        R_samples = []
        for trial in range(3):
            phases_init = np.random.uniform(0, 2*np.pi, N)
            R = kuramoto_order_parameter(phases_init, dt=0.01, T=50)
            R_samples.append(R)
        
        R_avg = np.mean(R_samples)
        
        if R_avg > 0.3:
            K_high = K_test  # K_c is lower
        else:
            K_low = K_test   # K_c is higher
    
    K_c = (K_low + K_high) / 2
    return K_c

# ============================================================================
# MAIN PHASE 3 EXPERIMENT
# ============================================================================

print("=" * 80)
print("PHASE 3: KURAMOTO SCALING ON k-REGULAR RANDOM GRAPHS")
print("=" * 80)
print()

# Configuration
network_sizes = [16, 32, 64]
coordination_numbers = [2, 3, 4, 5, 6, 8]
ensemble_size = 20  # seeds per (k, N) pair
tolerance = 0.05

results = {}

print("Starting Phase 3 parameter sweep...")
print(f"  Network sizes: {network_sizes}")
print(f"  Coordination numbers: {coordination_numbers}")
print(f"  Ensemble size: {ensemble_size} seeds per (k,N)")
print()

for k in coordination_numbers:
    print(f"\n{'='*80}")
    print(f"COORDINATION NUMBER k = {k}")
    print(f"{'='*80}")
    
    results[f"k_{k}"] = {
        "N": [],
        "K_c_mean": [],
        "K_c_std": [],
        "K_c_samples": []
    }
    
    for N in network_sizes:
        print(f"  N={N:3d}: generating {ensemble_size} random {k}-regular graphs...", end='', flush=True)
        
        K_c_ensemble = []
        
        for seed in range(ensemble_size):
            np.random.seed(seed * 10000 + k * 1000 + N)
            
            # Generate k-regular random graph
            A = generate_krandom_graph(N, k)
            
            # Verify regularity
            degrees = A.sum(axis=1)
            if not np.allclose(degrees, k):
                print(f"[WARNING] Generated graph has degrees {np.unique(degrees)}, expected {k}")
            
            # Find K_c
            K_c = find_critical_coupling_binary_search(A, N, K_min=0.1, K_max=50)
            K_c_ensemble.append(K_c)
        
        K_c_mean = np.mean(K_c_ensemble)
        K_c_std = np.std(K_c_ensemble)
        
        results[f"k_{k}"]["N"].append(N)
        results[f"k_{k}"]["K_c_mean"].append(K_c_mean)
        results[f"k_{k}"]["K_c_std"].append(K_c_std)
        results[f"k_{k}"]["K_c_samples"].append(K_c_ensemble)
        
        print(f" ✓ K_c = {K_c_mean:.4f} ± {K_c_std:.4f}")

# ============================================================================
# ANALYSIS: Fit scaling exponent α(k)
# ============================================================================

print("\n" + "=" * 80)
print("SCALING ANALYSIS: α(k)")
print("=" * 80)
print()

scaling_results = {}

for k in coordination_numbers:
    key = f"k_{k}"
    N_vals = np.array(results[key]["N"])
    K_c_vals = np.array(results[key]["K_c_mean"])
    
    # Fit: K_c = a * N^alpha
    log_N = np.log(N_vals)
    log_K_c = np.log(K_c_vals)
    
    # Linear regression
    coeffs = np.polyfit(log_N, log_K_c, 1)
    alpha = coeffs[0]
    a = np.exp(coeffs[1])
    
    # R-squared
    y_pred = alpha * log_N + coeffs[1]
    ss_res = np.sum((log_K_c - y_pred) ** 2)
    ss_tot = np.sum((log_K_c - np.mean(log_K_c)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    
    scaling_results[k] = {
        "alpha": alpha,
        "a": a,
        "r_squared": r_squared
    }
    
    print(f"k={k:2d}: α = {alpha:7.3f}  (R² = {r_squared:.4f})  K_c ≈ {a:.4f} * N^{alpha:.3f}")

# ============================================================================
# SAVE RESULTS
# ============================================================================

output = {
    "phase": "Phase 3: k-Regular Random Graph Scaling",
    "configuration": {
        "network_sizes": network_sizes,
        "coordination_numbers": coordination_numbers,
        "ensemble_size": ensemble_size
    },
    "raw_results": results,
    "scaling_analysis": {str(k): v for k, v in scaling_results.items()}
}

with open("phase3_krandom_results.json", "w") as f:
    json.dump(output, f, indent=2)

print("\n" + "=" * 80)
print("[✓] Phase 3 complete. Results saved to phase3_krandom_results.json")
print("=" * 80)

# Summary
print("\nSUMMARY:")
print("-" * 80)
alphas = [scaling_results[k]["alpha"] for k in coordination_numbers]
print(f"Exponents α(k): {[(k, alphas[i]) for i, k in enumerate(coordination_numbers)]}")
print()
if min(alphas) < -0.363 < max(alphas):
    print("[★] Canonical exponent α = -0.363 falls within range!")
    print("    Suggests interpolation between lattice and random regimes")
elif all(a > 0 for a in alphas):
    print("[✗] All exponents positive: k-regular graphs remain lattice-like")
elif all(a < -0.363 for a in alphas):
    print("[★] All exponents more negative than canonical")
    print("    Suggests even sparser structure than ER random")
else:
    print("[?] Mixed signs or values: regime transition observed")

print("=" * 80)
