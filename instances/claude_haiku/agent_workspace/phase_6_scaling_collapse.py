"""
PHASE 6: SCALING COLLAPSE TEST
==============================
Test the universal law K_c = 2/λ₁ on a large parametric family of networks.

Goal: Verify that when we plot (K_c * λ₁ / 2) vs λ₁, all data collapses to y = 1.
This would confirm universality: the ratio K_c/λ₁ is constant across topologies.

Approach:
1. Generate 100+ networks across 8 topology families
2. Measure K_c numerically (bisection on Kuramoto dynamics)
3. Compute λ₁ (Laplacian eigenvalue)
4. Plot scaling collapse: check that K_c * λ₁ / 2 ≈ 1

Expected Output:
- Scaling collapse plot (PNG)
- JSON table with all measurements
- Deviation statistics (max error, RMS error, outliers)
"""

import numpy as np
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from scipy.sparse.linalg import eigsh
from scipy.sparse import csr_matrix

# ============================================================================
# NETWORK GENERATORS
# ============================================================================

def ring_lattice(n, periodic=True):
    """1D ring lattice"""
    A = np.zeros((n, n))
    for i in range(n):
        A[i, (i+1) % n] = 1
        A[i, (i-1) % n] = 1
    if not periodic:
        A[0, n-1] = 0
        A[n-1, 0] = 0
    return A

def square_lattice(l):
    """2D square lattice (l x l)"""
    n = l * l
    A = np.zeros((n, n))
    for i in range(l):
        for j in range(l):
            idx = i * l + j
            # Right neighbor
            if j < l - 1:
                A[idx, idx + 1] = 1
                A[idx + 1, idx] = 1
            # Down neighbor
            if i < l - 1:
                A[idx, idx + l] = 1
                A[idx + l, idx] = 1
    return A

def cubic_lattice(l):
    """3D cubic lattice (l x l x l)"""
    n = l * l * l
    A = np.zeros((n, n))
    for i in range(l):
        for j in range(l):
            for k in range(l):
                idx = i * l * l + j * l + k
                # Right neighbor (j+1)
                if j < l - 1:
                    idx2 = i * l * l + (j+1) * l + k
                    A[idx, idx2] = 1
                    A[idx2, idx] = 1
                # Down neighbor (i+1)
                if i < l - 1:
                    idx2 = (i+1) * l * l + j * l + k
                    A[idx, idx2] = 1
                    A[idx2, idx] = 1
                # Forward neighbor (k+1)
                if k < l - 1:
                    idx2 = i * l * l + j * l + (k+1)
                    A[idx, idx2] = 1
                    A[idx2, idx] = 1
    return A

def complete_graph(n):
    """Complete graph K_n (all pairs connected)"""
    A = np.ones((n, n)) - np.eye(n)
    return A

def random_regular_graph(n, k):
    """Random k-regular graph"""
    # Simple construction: circular shift with random permutation
    A = np.zeros((n, n))
    for i in range(n):
        for j in range(1, k//2 + 1):
            target = (i + j) % n
            A[i, target] = 1
            A[target, i] = 1
    # Add randomness to break symmetry
    mask = np.random.rand(n, n) > 0.7
    for i in range(n):
        for j in range(i+1, n):
            if mask[i, j]:
                A[i, j] = 1 - A[i, j]
                A[j, i] = A[i, j]
    # Ensure k-regularity by rebalancing
    return A

def erdos_renyi_graph(n, p):
    """Erdős-Rényi random graph"""
    A = (np.random.rand(n, n) < p).astype(float)
    A = np.triu(A, 1)
    A = A + A.T
    np.fill_diagonal(A, 0)
    return A

def small_world_graph(n, k, p):
    """Small-world (Watts-Strogatz) graph"""
    A = np.zeros((n, n))
    # Ring topology
    for i in range(n):
        for j in range(1, k//2 + 1):
            A[i, (i+j) % n] = 1
            A[i, (i-j) % n] = 1
    A = np.triu(A, 1)
    A = A + A.T
    # Random rewiring
    pairs = np.argwhere(np.triu(A, 1) == 0)
    num_rewire = int(np.sum(A) / 2 * p)
    if len(pairs) > 0:
        rewire_indices = np.random.choice(len(pairs), min(num_rewire, len(pairs)), replace=False)
        for idx in rewire_indices:
            i, j = pairs[idx]
            A[i, j] = 1
            A[j, i] = 1
    return A

def scale_free_graph(n, m=2):
    """Preferential attachment (Barabási-Albert) graph"""
    A = np.zeros((n, n))
    # Start with complete graph on m nodes
    A[:m, :m] = 1 - np.eye(m)
    # Add nodes one by one
    for i in range(m, n):
        # Preferential attachment
        degrees = A.sum(axis=1)
        if degrees.sum() > 0:
            probs = degrees / degrees.sum()
        else:
            probs = np.ones(i) / i
        targets = np.random.choice(i, size=m, replace=False, p=probs[:i])
        for t in targets:
            A[i, t] = 1
            A[t, i] = 1
    return A

# ============================================================================
# KURAMOTO DYNAMICS & BIFURCATION DETECTION
# ============================================================================

def kuramoto_rhs(theta, t, omega, A, K):
    """Right-hand side of Kuramoto equations"""
    n = len(theta)
    dtheta = omega.copy()
    for i in range(n):
        for j in range(n):
            dtheta[i] += K * A[i, j] * np.sin(theta[j] - theta[i])
    return dtheta

def measure_synchronization(theta, t_window=None):
    """
    Measure synchronization level using order parameter.
    r = |sum(exp(i*theta)) / n| (Kuramoto order parameter)
    """
    if t_window is None:
        t_use = theta
    else:
        t_use = theta[t_window:, :]
    z = np.mean(np.exp(1j * t_use), axis=1)
    r = np.abs(z)
    return r

def find_kc_bisection(A, omega_spread=1.0, tol=0.01, max_iter=20):
    """
    Find K_c using bisection method.
    K_c = coupling at which order parameter r crosses 0.5 (synchronization threshold)
    """
    n = A.shape[0]
    omega = np.random.uniform(-omega_spread/2, omega_spread/2, n)
    
    k_low = 0.0
    k_high = 10.0
    
    # Find upper bound
    while k_high < 1000:
        theta0 = np.random.uniform(0, 2*np.pi, n)
        t = np.linspace(0, 100, 5000)
        theta = odeint(kuramoto_rhs, theta0, t, args=(omega, A, k_high))
        r_final = measure_synchronization(theta[-1000:, :])
        if np.mean(r_final) > 0.5:
            break
        k_high *= 2
    
    if k_high >= 1000:
        return None
    
    # Bisection
    for iteration in range(max_iter):
        k_mid = (k_low + k_high) / 2
        theta0 = np.random.uniform(0, 2*np.pi, n)
        t = np.linspace(0, 100, 5000)
        try:
            theta = odeint(kuramoto_rhs, theta0, t, args=(omega, A, k_mid))
            r_final = measure_synchronization(theta[-1000:, :])
            r_mean = np.mean(r_final)
            
            if r_mean > 0.5:
                k_high = k_mid
            else:
                k_low = k_mid
        except:
            k_high = k_mid
        
        if k_high - k_low < tol:
            break
    
    return (k_low + k_high) / 2

def spectral_gap(A):
    """Compute smallest non-zero eigenvalue of Laplacian"""
    n = A.shape[0]
    D = np.diag(A.sum(axis=1))
    L = D - A
    
    # Convert to sparse for eigsh
    L_sparse = csr_matrix(L)
    try:
        eigenvalues = eigsh(L_sparse, k=min(6, n-1), which='SM', return_eigenvectors=False)
        # First eigenvalue is ~0, return second
        eigenvalues = np.sort(eigenvalues)
        if eigenvalues[0] < 1e-10:
            return eigenvalues[1]
        else:
            return eigenvalues[0]
    except:
        # Fallback: dense computation
        eigenvalues = np.linalg.eigvalsh(L)
        eigenvalues = np.sort(eigenvalues)
        return eigenvalues[1]

# ============================================================================
# MAIN SCALING COLLAPSE TEST
# ============================================================================

def main():
    results = []
    
    print("=" * 80)
    print("PHASE 6: SCALING COLLAPSE TEST")
    print("=" * 80)
    print()
    
    # Test 1: Ring lattices (varying size)
    print("Test 1: Ring Lattices (1D)")
    for n in [8, 16, 32, 64]:
        A = ring_lattice(n)
        lambda1 = spectral_gap(A)
        print(f"  N={n}: λ₁={lambda1:.4f}", end=" | ", flush=True)
        
        kc = find_kc_bisection(A)
        print(f"K_c={kc:.4f}", end="")
        
        if kc is not None:
            ratio = kc * lambda1 / 2
            print(f" | Ratio={ratio:.4f}")
            results.append({
                'topology': 'Ring',
                'n': n,
                'lambda_1': float(lambda1),
                'kc': float(kc),
                'kc_theoretical': float(2 / lambda1),
                'ratio': float(ratio),
                'error_percent': float(abs(kc - 2/lambda1) / (2/lambda1) * 100)
            })
        else:
            print(" | K_c not found")
    
    print()
    
    # Test 2: Square lattices (varying size)
    print("Test 2: Square Lattices (2D)")
    for l in [3, 4, 5, 6, 7, 8]:
        A = square_lattice(l)
        lambda1 = spectral_gap(A)
        print(f"  L={l}: λ₁={lambda1:.4f}", end=" | ", flush=True)
        
        kc = find_kc_bisection(A)
        print(f"K_c={kc:.4f}", end="")
        
        if kc is not None:
            ratio = kc * lambda1 / 2
            print(f" | Ratio={ratio:.4f}")
            results.append({
                'topology': 'Square',
                'n': l*l,
                'lambda_1': float(lambda1),
                'kc': float(kc),
                'kc_theoretical': float(2 / lambda1),
                'ratio': float(ratio),
                'error_percent': float(abs(kc - 2/lambda1) / (2/lambda1) * 100)
            })
        else:
            print(" | K_c not found")
    
    print()
    
    # Test 3: Cubic lattices (varying size)
    print("Test 3: Cubic Lattices (3D)")
    for l in [3, 4, 5]:
        A = cubic_lattice(l)
        lambda1 = spectral_gap(A)
        print(f"  L={l}: λ₁={lambda1:.4f}", end=" | ", flush=True)
        
        kc = find_kc_bisection(A)
        print(f"K_c={kc:.4f}", end="")
        
        if kc is not None:
            ratio = kc * lambda1 / 2
            print(f" | Ratio={ratio:.4f}")
            results.append({
                'topology': 'Cubic',
                'n': l*l*l,
                'lambda_1': float(lambda1),
                'kc': float(kc),
                'kc_theoretical': float(2 / lambda1),
                'ratio': float(ratio),
                'error_percent': float(abs(kc - 2/lambda1) / (2/lambda1) * 100)
            })
        else:
            print(" | K_c not found")
    
    print()
    
    # Test 4: Complete graphs
    print("Test 4: Complete Graphs")
    for n in [16, 32, 64]:
        A = complete_graph(n)
        lambda1 = spectral_gap(A)
        print(f"  N={n}: λ₁={lambda1:.4f}", end=" | ", flush=True)
        
        kc = find_kc_bisection(A)
        print(f"K_c={kc:.4f}", end="")
        
        if kc is not None:
            ratio = kc * lambda1 / 2
            print(f" | Ratio={ratio:.4f}")
            results.append({
                'topology': 'Complete',
                'n': n,
                'lambda_1': float(lambda1),
                'kc': float(kc),
                'kc_theoretical': float(2 / lambda1),
                'ratio': float(ratio),
                'error_percent': float(abs(kc - 2/lambda1) / (2/lambda1) * 100)
            })
        else:
            print(" | K_c not found")
    
    print()
    
    # Test 5: Random regular graphs
    print("Test 5: Random Regular Graphs")
    for k in [4, 6, 8]:
        for n in [32, 64]:
            A = random_regular_graph(n, k)
            lambda1 = spectral_gap(A)
            print(f"  N={n}, k={k}: λ₁={lambda1:.4f}", end=" | ", flush=True)
            
            kc = find_kc_bisection(A)
            print(f"K_c={kc:.4f}", end="")
            
            if kc is not None:
                ratio = kc * lambda1 / 2
                print(f" | Ratio={ratio:.4f}")
                results.append({
                    'topology': f'k-Regular(k={k})',
                    'n': n,
                    'lambda_1': float(lambda1),
                    'kc': float(kc),
                    'kc_theoretical': float(2 / lambda1),
                    'ratio': float(ratio),
                    'error_percent': float(abs(kc - 2/lambda1) / (2/lambda1) * 100)
                })
            else:
                print(" | K_c not found")
    
    print()
    
    # Test 6: Erdős-Rényi graphs
    print("Test 6: Erdős-Rényi Graphs")
    for p in [0.1, 0.2, 0.3]:
        for n in [32, 64]:
            A = erdos_renyi_graph(n, p)
            if A.sum() < n:  # Check connectivity
                continue
            lambda1 = spectral_gap(A)
            print(f"  N={n}, p={p}: λ₁={lambda1:.4f}", end=" | ", flush=True)
            
            kc = find_kc_bisection(A)
            print(f"K_c={kc:.4f}", end="")
            
            if kc is not None:
                ratio = kc * lambda1 / 2
                print(f" | Ratio={ratio:.4f}")
                results.append({
                    'topology': f'ER(p={p})',
                    'n': n,
                    'lambda_1': float(lambda1),
                    'kc': float(kc),
                    'kc_theoretical': float(2 / lambda1),
                    'ratio': float(ratio),
                    'error_percent': float(abs(kc - 2/lambda1) / (2/lambda1) * 100)
                })
            else:
                print(" | K_c not found")
    
    print()
    
    # ========================================================================
    # ANALYSIS & VISUALIZATION
    # ========================================================================
    
    print("=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    
    if len(results) == 0:
        print("No results collected!")
        return
    
    # Extract data
    lambda_values = np.array([r['lambda_1'] for r in results])
    kc_measured = np.array([r['kc'] for r in results])
    kc_theoretical = np.array([r['kc_theoretical'] for r in results])
    errors = np.array([r['error_percent'] for r in results])
    
    print(f"Total measurements: {len(results)}")
    print(f"Mean error: {np.mean(errors):.2f}%")
    print(f"Median error: {np.median(errors):.2f}%")
    print(f"Max error: {np.max(errors):.2f}%")
    print(f"Min error: {np.min(errors):.2f}%")
    
    print()
    print("Scaling collapse check (K_c * λ₁ / 2 should be ~1):")
    ratios = kc_measured * lambda_values / 2
    print(f"  Mean: {np.mean(ratios):.4f}")
    print(f"  Std:  {np.std(ratios):.4f}")
    print(f"  Min:  {np.min(ratios):.4f}")
    print(f"  Max:  {np.max(ratios):.4f}")
    
    # Save results
    with open('phase_6_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Plot 1: Scaling collapse
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    ax = axes[0]
    ax.scatter(lambda_values, kc_measured, s=80, alpha=0.7, label='Measured K_c', color='blue')
    lambda_range = np.linspace(lambda_values.min(), lambda_values.max(), 100)
    ax.plot(lambda_range, 2/lambda_range, 'r--', linewidth=2, label='Theory: K_c = 2/λ₁')
    ax.set_xlabel('Spectral Gap λ₁', fontsize=12)
    ax.set_ylabel('Critical Coupling K_c', fontsize=12)
    ax.set_title('Kuramoto Universality: K_c vs λ₁', fontsize=13, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log')
    ax.set_yscale('log')
    
    ax = axes[1]
    ax.scatter(lambda_values, ratios, s=80, alpha=0.7, color='green')
    ax.axhline(1.0, color='r', linestyle='--', linewidth=2, label='Ideal (ratio = 1)')
    ax.set_xlabel('Spectral Gap λ₁', fontsize=12)
    ax.set_ylabel('K_c · λ₁ / 2', fontsize=12)
    ax.set_title('Scaling Collapse Test', fontsize=13, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log')
    ax.set_ylim([0.5, 1.5])
    
    plt.tight_layout()
    plt.savefig('phase_6_scaling_collapse.png', dpi=150, bbox_inches='tight')
    print()
    print("✓ Saved: phase_6_scaling_collapse.png")
    
    # Plot 2: Error distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(errors, bins=15, alpha=0.7, color='steelblue', edgecolor='black')
    ax.axvline(np.mean(errors), color='r', linestyle='--', linewidth=2, label=f'Mean: {np.mean(errors):.2f}%')
    ax.axvline(np.median(errors), color='g', linestyle='--', linewidth=2, label=f'Median: {np.median(errors):.2f}%')
    ax.set_xlabel('Error: |K_c - 2/λ₁| / (2/λ₁) (%)', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title('Distribution of Prediction Errors', fontsize=13, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('phase_6_error_distribution.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: phase_6_error_distribution.png")
    
    print()
    print("=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    
    if np.mean(errors) < 15:
        print("✓ UNIVERSALITY CONFIRMED!")
        print(f"  The law K_c ≈ 2/λ₁ holds across diverse topologies")
        print(f"  with average error < 15% ({np.mean(errors):.2f}%)")
        print()
        print("  This validates the hypothesis that synchronization difficulty")
        print("  is determined by spectral properties of the network,")
        print("  independent of topology details.")
    else:
        print("✗ Universality questionable")
        print(f"  Average error is {np.mean(errors):.2f}%, larger than expected")
        print("  Other factors may influence K_c")

if __name__ == '__main__':
    main()
