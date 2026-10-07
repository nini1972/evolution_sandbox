#!/usr/bin/env python3
"""
Periodicity Archaeology: Uncovering hidden periodic structures in chaotic systems
"""

import numpy as np
import json
import matplotlib.pyplot as plt

# Set non-interactive backend for headless server
import matplotlib
matplotlib.use('Agg')

def coupled_logistic_map(x, r, epsilon):
    """Evolve coupled logistic map lattice one time step."""
    n = len(x)
    f_x = r * x * (1 - x)
    # Apply periodic boundary conditions
    f_left = np.roll(f_x, 1)
    f_right = np.roll(f_x, -1)
    return (1 - epsilon) * f_x + (epsilon / 2) * (f_left + f_right)

def analyze_periodic_structure():
    """Analyze hidden periodic structures in coupled logistic map lattice."""
    
    # System parameters (chaotic regime)
    r = 3.865
    epsilon = 0.132
    n_cells = 100
    
    # Initialize system
    np.random.seed(42)
    x = np.random.rand(n_cells)
    
    # Transient evolution to reach attractor
    print("Evolving transient...")
    for _ in range(1000):
        x = coupled_logistic_map(x, r, epsilon)
    
    # Record trajectory for analysis
    print("Recording trajectory...")
    trajectory = []
    for _ in range(2000):
        x = coupled_logistic_map(x, r, epsilon)
        trajectory.append(x.copy())
    
    trajectory = np.array(trajectory)
    
    # Convert to binary using median threshold
    binary_traj = (trajectory > np.median(trajectory)).astype(int)
    
    # Extract binary motifs of width 4 from each time step
    motif_width = 4
    motifs = []
    for t in range(len(trajectory)):
        # Take first motif_width cells as motif
        motif_str = ''.join(str(bit) for bit in binary_traj[t, :motif_width])
        motifs.append(motif_str)
    
    # Analyze lag consistency
    print("Analyzing lag consistency...")
    max_lag = 50
    lag_consistency = {}
    
    for lag in range(1, max_lag + 1):
        matches = 0
        total = 0
        for i in range(len(motifs) - lag):
            if motifs[i] == motifs[i + lag]:
                matches += 1
            total += 1
        lag_consistency[lag] = matches / total if total > 0 else 0
    
    # Analyze period-4 structure
    residue_stats = {}
    for residue in range(4):
        residues = [lag for lag in lag_consistency.keys() if lag % 4 == residue]
        if residues:
            values = [lag_consistency[lag] for lag in residues]
            residue_stats[residue] = {
                'mean': np.mean(values),
                'std': np.std(values),
                'count': len(values)
            }
        else:
            residue_stats[residue] = {'mean': 0, 'std': 0, 'count': 0}
    
    # Calculate parity contrast
    even_mean = (residue_stats[0]['mean'] + residue_stats[2]['mean']) / 2
    odd_mean = (residue_stats[1]['mean'] + residue_stats[3]['mean']) / 2
    parity_contrast = even_mean - odd_mean
    
    results = {
        'parameters': {
            'r': r,
            'epsilon': epsilon,
            'n_cells': n_cells,
            'trajectory_length': len(trajectory),
            'motif_width': motif_width,
            'max_lag': max_lag
        },
        'lag_consistency': lag_consistency,
        'residue_stats': residue_stats,
        'parity_contrast': parity_contrast
    }
    
    # Save results
    with open('initial_analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Create visualization
    lags = list(lag_consistency.keys())
    consistency_values = list(lag_consistency.values())
    
    plt.figure(figsize=(12, 8))
    
    # Main plot: lag consistency
    plt.subplot(2, 1, 1)
    plt.plot(lags, consistency_values, 'b-', alpha=0.7, linewidth=1.5)
    plt.xlabel('Lag')
    plt.ylabel('Motif Consistency')
    plt.title(f'Hidden Periodic Structure Analysis\nr={r}, ε={epsilon}, Parity Contrast={parity_contrast:.3f}')
    plt.grid(True, alpha=0.3)
    
    # Highlight period-4 residues
    colors = ['red', 'orange', 'green', 'purple']
    for residue in range(4):
        residue_lags = [lag for lag in lags if lag % 4 == residue]
        residue_consistency = [lag_consistency[lag] for lag in residue_lags]
        plt.scatter(residue_lags, residue_consistency, c=colors[residue], 
                   label=f'Residue {residue} mod 4', alpha=0.6, s=30)
    
    plt.legend()
    
    # Residue statistics
    plt.subplot(2, 2, 3)
    residues = list(residue_stats.keys())
    means = [residue_stats[r]['mean'] for r in residues]
    stds = [residue_stats[r]['std'] for r in residues]
    plt.bar(residues, means, yerr=stds, capsize=5, color=colors)
    plt.xlabel('Residue mod 4')
    plt.ylabel('Mean Consistency')
    plt.title('Period-4 Residue Statistics')
    plt.xticks(residues)
    
    # Parity contrast
    plt.subplot(2, 2, 4)
    plt.bar(['Even', 'Odd'], [even_mean, odd_mean], color=['lightblue', 'lightcoral'])
    plt.ylabel('Mean Consistency')
    plt.title(f'Parity Contrast: {parity_contrast:.3f}')
    
    plt.tight_layout()
    plt.savefig('initial_periodic_analysis.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Analysis complete!")
    print(f"Period-4 parity contrast: {parity_contrast:.3f}")
    print(f"Residue 0 mean: {residue_stats[0]['mean']:.3f}")
    print(f"Residue 2 mean: {residue_stats[2]['mean']:.3f}")
    print(f"Residues 1,3 mean: {(residue_stats[1]['mean'] + residue_stats[3]['mean'])/2:.3f}")
    
    return results

if __name__ == "__main__":
    results = analyze_periodic_structure()