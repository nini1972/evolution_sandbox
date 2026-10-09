#!/usr/bin/env python3
"""
Analyze the most chaotic parameter case for hidden periodic structures
"""

import numpy as np
import json
import matplotlib.pyplot as plt

# Set non-interactive backend
import matplotlib
matplotlib.use('Agg')

def coupled_logistic_map(x, r, epsilon):
    """Evolve coupled logistic map lattice one time step."""
    n = len(x)
    f_x = r * x * (1 - x)
    f_left = np.roll(f_x, 1)
    f_right = np.roll(f_x, -1)
    return (1 - epsilon) * f_x + (epsilon / 2) * (f_left + f_right)

def analyze_motif_periodicity(r=4.0, epsilon=0.15, n_cells=100, trajectory_length=2000, motif_width=4, max_lag=50):
    """
    Analyze motif periodicity in coupled logistic map lattice.
    """
    
    # Initialize system
    np.random.seed(42)
    x = np.random.rand(n_cells)
    
    # Evolve through transient
    print("Evolving transient...")
    for _ in range(1000):
        x = coupled_logistic_map(x, r, epsilon)
    
    # Record trajectory
    print("Recording trajectory...")
    trajectory = []
    for _ in range(trajectory_length):
        x = coupled_logistic_map(x, r, epsilon)
        trajectory.append(x.copy())
    
    trajectory = np.array(trajectory)
    
    # Convert to binary using median threshold
    median_val = np.median(trajectory)
    binary_trajectory = (trajectory > median_val).astype(int)
    
    # Extract motifs
    motifs = []
    for t in range(len(binary_trajectory)):
        motif_str = ''.join(str(bit) for bit in binary_trajectory[t, :motif_width])
        motifs.append(motif_str)
    
    # Analyze lag consistency
    print("Analyzing lag consistency...")
    lag_consistency = {}
    for lag in range(1, max_lag + 1):
        matches = 0
        total = 0
        for t in range(len(motifs) - lag):
            if motifs[t] == motifs[t + lag]:
                matches += 1
            total += 1
        consistency = matches / total if total > 0 else 0
        lag_consistency[lag] = consistency
    
    # Analyze by residue classes modulo small periods
    residue_stats = {}
    for period in [2, 3, 4, 5]:
        residue_stats[period] = {}
        for residue in range(period):
            lags = [lag for lag in range(1, max_lag + 1) if lag % period == residue]
            if lags:
                consistencies = [lag_consistency[lag] for lag in lags]
                residue_stats[period][residue] = {
                    'mean': np.mean(consistencies),
                    'std': np.std(consistencies),
                    'count': len(consistencies)
                }
    
    # Calculate parity contrast for period 2
    even_lags = [lag for lag in range(2, max_lag + 1, 2)]
    odd_lags = [lag for lag in range(1, max_lag + 1, 2)]
    even_mean = np.mean([lag_consistency[lag] for lag in even_lags])
    odd_mean = np.mean([lag_consistency[lag] for lag in odd_lags])
    parity_contrast = abs(even_mean - odd_mean)
    
    # Save results
    results = {
        'parameters': {
            'r': r,
            'epsilon': epsilon,
            'n_cells': n_cells,
            'trajectory_length': trajectory_length,
            'motif_width': motif_width,
            'max_lag': max_lag
        },
        'lag_consistency': lag_consistency,
        'residue_stats': residue_stats,
        'parity_contrast': parity_contrast
    }
    
    with open('chaotic_case_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Create visualization
    plt.figure(figsize=(12, 8))
    
    # Plot lag consistency
    lags = list(range(1, max_lag + 1))
    consistencies = [lag_consistency[lag] for lag in lags]
    plt.subplot(2, 1, 1)
    plt.plot(lags, consistencies, 'b-', linewidth=1)
    plt.xlabel('Lag')
    plt.ylabel('Motif Consistency')
    plt.title(f'Motif Lag Consistency (r={r}, ε={epsilon})')
    plt.grid(True, alpha=0.3)
    
    # Highlight period-4 structure
    for period in [2, 4]:
        plt.subplot(2, 1, 2)
        residues = list(range(period))
        means = [residue_stats[period][res][ 'mean'] for res in residues]
        plt.bar([f'Res {res} mod {period}' for res in residues], means, 
                alpha=0.7, label=f'Period {period}')
    
    plt.ylabel('Mean Consistency')
    plt.title('Residue Class Consistency')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('chaotic_case_analysis.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Analysis complete!")
    print(f"Period-2 parity contrast: {parity_contrast:.3f}")
    period4_means = [residue_stats[4][res]['mean'] for res in range(4)]
    print(f"Period-4 residue means: {[f'{mean:.3f}' for mean in period4_means]}")
    
    return results

if __name__ == "__main__":
    results = analyze_motif_periodicity()