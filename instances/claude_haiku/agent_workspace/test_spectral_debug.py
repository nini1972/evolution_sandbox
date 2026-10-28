#!/usr/bin/env python3
"""
Debug spectral gap computation locally
"""

import numpy as np
from scipy.sparse import csr_matrix, diags
from scipy.sparse.linalg import eigsh
from scipy.linalg import eigh

def make_ring(n):
    """1D ring lattice"""
    adj = np.zeros((n, n))
    for i in range(n):
        adj[i, (i+1) % n] = 1
        adj[i, (i-1) % n] = 1
    return adj

def make_complete_graph(n):
    """Complete graph"""
    adj = np.ones((n, n)) - np.eye(n)
    return adj

print("=== Spectral Gap Debug ===\n")

for name, gen_func, n in [('ring', make_ring, 20), ('complete', make_complete_graph, 20)]:
    print(f"Testing {name} (N={n})")
    
    adj = gen_func(n)
    print(f"  Adjacency shape: {adj.shape}")
    print(f"  Adjacency sum: {adj.sum():.1f}")
    
    # Compute degree
    degrees = adj.sum(axis=1)
    print(f"  Degree vector: min={degrees.min():.0f}, max={degrees.max():.0f}, mean={degrees.mean():.1f}")
    
    # Compute Laplacian
    L = np.diag(degrees) - adj
    print(f"  Laplacian diagonal: {np.diag(L)[:5]}")
    
    # Dense eigenvalue solver
    print("  Dense eigenvalue solver:")
    eigenvals_dense, eigenvecs_dense = eigh(L)
    print(f"    Eigenvalues (first 5): {eigenvals_dense[:5]}")
    print(f"    Smallest eigenvalue: {eigenvals_dense[0]:.10f}")
    print(f"    Second smallest eigenvalue (λ₁): {eigenvals_dense[1]:.10f}")
    
    # Sparse eigenvalue solver
    print("  Sparse eigenvalue solver:")
    L_sparse = csr_matrix(L)
    try:
        eigenvals_sparse = eigsh(L_sparse, k=2, which='SM', return_eigenvectors=False)
        print(f"    Eigenvalues: {eigenvals_sparse}")
    except Exception as e:
        print(f"    Error: {e}")
    
    print()

print("\n=== Key Insights ===")
print("1. Ring: Each node has degree 2, Laplacian diagonal = 2")
print("2. Complete: Each node has degree N-1, Laplacian diagonal = N-1")
print("3. Smallest eigenvalue of L should ALWAYS be 0 (constant eigenvector)")
print("4. λ₁ (algebraic connectivity) is the second smallest eigenvalue")
print("5. For ring: λ₁ = 2 - 2*cos(2π/N) ≈ 2π²/N² for large N")
print("6. For complete: λ₁ = N (every node has degree N-1, full connectivity)")

