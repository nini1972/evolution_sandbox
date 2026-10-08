#!/usr/bin/env python3
"""
Debug the binary encoding process to understand the periodic structure
"""

import numpy as np

def coupled_logistic_map(x, r, epsilon):
    """Evolve coupled logistic map lattice one time step."""
    n = len(x)
    f_x = r * x * (1 - x)
    f_left = np.roll(f_x, 1)
    f_right = np.roll(f_x, -1)
    return (1 - epsilon) * f_x + (epsilon / 2) * (f_left + f_right)

def debug_encoding():
    """Debug the binary encoding process."""
    
    r = 3.865
    epsilon = 0.132
    n_cells = 100
    
    # Initialize
    np.random.seed(42)
    x = np.random.rand(n_cells)
    
    # Transient
    for _ in range(1000):
        x = coupled_logistic_map(x, r, epsilon)
    
    # Record short trajectory
    trajectory = []
    for _ in range(10):
        x = coupled_logistic_map(x, r, epsilon)
        trajectory.append(x.copy())
    
    trajectory = np.array(trajectory)
    
    # Show actual values for first few cells
    print("Actual trajectory values (first 5 cells, first 10 time steps):")
    print(trajectory[:10, :5])
    print()
    
    # Binary encoding with median
    median_val = np.median(trajectory)
    binary_traj = (trajectory > median_val).astype(int)
    
    print(f"Median threshold: {median_val:.6f}")
    print("Binary trajectory (first 5 cells, first 10 time steps):")
    print(binary_traj[:10, :5])
    print()
    
    # Extract motifs
    motif_width = 4
    motifs = []
    for t in range(len(trajectory)):
        motif_str = ''.join(str(bit) for bit in binary_traj[t, :motif_width])
        motifs.append(motif_str)
    
    print("Motifs over time:")
    for t, motif in enumerate(motifs):
        print(f"t={t}: {motif}")
    print()
    
    # Check periodicity
    print("Checking period-2 pattern:")
    for t in range(len(motifs)-2):
        if motifs[t] == motifs[t+2]:
            match = "✓"
        else:
            match = "✗"
        print(f"t={t} vs t={t+2}: {motifs[t]} vs {motifs[t+2]} {match}")

if __name__ == "__main__":
    debug_encoding()