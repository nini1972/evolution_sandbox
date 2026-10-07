#!/usr/bin/env python3
"""
Periodicity Archaeology Toolkit
Tools for detecting hidden periodic structures in chaotic dynamical systems
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

def generate_coupled_logistic_lattice(r=3.865, epsilon=0.132, n_cells=100, t_max=1000, seed=42):
    """
    Generate a coupled logistic map lattice
    
    Parameters:
    - r: chaos parameter (typically 3.57 < r < 4.0 for chaos)
    - epsilon: coupling strength (0 = uncoupled, 1 = fully coupled)  
    - n_cells: number of cells in the 1D lattice
    - t_max: number of time steps to simulate
    - seed: random seed for reproducibility
    
    Returns:
    - trajectory: 2D array of shape (t_max, n_cells)
    """
    np.random.seed(seed)
    x = np.random.rand(n_cells)
    trajectory = np.zeros((t_max, n_cells))
    
    for t in range(t_max):
        trajectory[t] = x.copy()
        # Apply logistic map to each cell
        f_x = r * x * (1 - x)
        # Get neighbors (with periodic boundary conditions)
        f_left = r * np.roll(x, 1) * (1 - np.roll(x, 1))
        f_right = r * np.roll(x, -1) * (1 - np.roll(x, -1))
        # Update with coupling
        x = (1 - epsilon) * f_x + epsilon * 0.5 * (f_left + f_right)
        
    return trajectory

def extract_symbolic_motifs(trajectory, motif_width=4, threshold=0.5):
    """
    Convert continuous trajectory to symbolic motifs
    
    Parameters:
    - trajectory: 2D array (time_steps, spatial_points)
    - motif_width: width of spatial motif to extract
    - threshold: threshold for binary conversion (default 0.5)
    
    Returns:
    - motifs: list of lists, where motifs[t][i] is the motif at time t, position i
    """
    n_time, n_cells = trajectory.shape
    binary_traj = (trajectory > threshold).astype(int)
    motifs = []
    
    for t in range(n_time):
        cell_motifs = []
        for i in range(n_cells):
            # Extract motif centered at position i
            start_idx = i - motif_width // 2
            motif_indices = [(start_idx + j) % n_cells for j in range(motif_width)]
            motif = tuple(binary_traj[t, motif_indices])
            cell_motifs.append(motif)
        motifs.append(cell_motifs)
    
    return motifs

def compute_temporal_consistency(motifs, max_lag=100):
    """
    Compute temporal consistency of motifs across different time lags
    
    Parameters:
    - motifs: symbolic motifs from extract_symbolic_motifs
    - max_lag: maximum time lag to analyze
    
    Returns:
    - lag_consistency: dict mapping lag -> consistency_score
    """
    n_time = len(motifs)
    n_cells = len(motifs[0]) if n_time > 0 else 0
    
    if n_time <= max_lag:
        raise ValueError("Not enough time steps for requested max_lag")
    
    lag_consistency = {}
    
    for lag in range(1, max_lag + 1):
        matches = 0
        total = 0
        for t in range(n_time - lag):
            for i in range(n_cells):
                if motifs[t][i] == motifs[t + lag][i]:
                    matches += 1
                total += 1
        lag_consistency[lag] = matches / total if total > 0 else 0.0
    
    return lag_consistency

def analyze_periodic_structure(lag_consistency, period_candidates=[2, 3, 4, 5, 6]):
    """
    Analyze lag consistency data for periodic structures
    
    Parameters:
    - lag_consistency: output from compute_temporal_consistency
    - period_candidates: periods to test for
    
    Returns:
    - period_analysis: dict with analysis results for each candidate period
    """
    max_lag = max(lag_consistency.keys())
    period_analysis = {}
    
    for period in period_candidates:
        # Group lags by their residue modulo period
        residue_groups = {r: [] for r in range(period)}
        for lag in range(1, min(max_lag + 1, period * 10)):  # Look at first 10 cycles
            if lag in lag_consistency:
                residue = lag % period
                residue_groups[residue].append(lag_consistency[lag])
        
        # Calculate statistics for each residue class
        residue_stats = {}
        for residue, values in residue_groups.items():
            if values:
                residue_stats[residue] = {
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'count': len(values)
                }
            else:
                residue_stats[residue] = {'mean': 0.0, 'std': 0.0, 'count': 0}
        
        # Calculate overall metrics
        even_residues = [residue_stats[r]['mean'] for r in range(0, period, 2) if residue_stats[r]['count'] > 0]
        odd_residues = [residue_stats[r]['mean'] for r in range(1, period, 2) if residue_stats[r]['count'] > 0]
        
        parity_contrast = np.mean(even_residues) - np.mean(odd_residues) if even_residues and odd_residues else 0.0
        
        period_analysis[period] = {
            'residue_stats': residue_stats,
            'parity_contrast': float(parity_contrast),
            'max_consistency': max(lag_consistency.values()) if lag_consistency else 0.0
        }
    
    return period_analysis

def visualize_periodic_analysis(lag_consistency, period_analysis, output_path="periodic_analysis.png"):
    """
    Create visualization of periodic structure analysis
    """
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Plot 1: Lag consistency over time
    lags = sorted(lag_consistency.keys())
    consistencies = [lag_consistency[lag] for lag in lags]
    axes[0, 0].plot(lags, consistencies, 'b-', alpha=0.7)
    axes[0, 0].set_xlabel('Time Lag')
    axes[0, 0].set_ylabel('Motif Consistency')
    axes[0, 0].set_title('Temporal Motif Consistency')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Plot 2: Period-4 residue analysis (focus on our main hypothesis)
    if 4 in period_analysis:
        residues = list(range(4))
        means = [period_analysis[4]['residue_stats'][r]['mean'] for r in residues]
        stds = [period_analysis[4]['residue_stats'][r]['std'] for r in residues]
        axes[0, 1].bar(residues, means, yerr=stds, capsize=5, alpha=0.7)
        axes[0, 1].set_xlabel('Lag mod 4')
        axes[0, 1].set_ylabel('Mean Consistency')
        axes[0, 1].set_title(f'Period-4 Structure\nParity Contrast: {period_analysis[4]["parity_contrast"]:.3f}')
        axes[0, 1].set_xticks(residues)
    
    # Plot 3: Compare different periods
    periods = sorted(period_analysis.keys())
    parity_contrasts = [period_analysis[p]['parity_contrast'] for p in periods]
    axes[1, 0].bar(periods, parity_contrasts, alpha=0.7)
    axes[1, 0].set_xlabel('Candidate Period')
    axes[1, 0].set_ylabel('Parity Contrast')
    axes[1, 0].set_title('Periodic Structure Strength by Candidate Period')
    axes[1, 0].set_xticks(periods)
    
    # Plot 4: Heatmap of residue consistency for period 4
    if 4 in period_analysis:
        residue_matrix = []
        for residue in range(4):
            values = []
            for lag in range(residue, 41, 4):  # First 10 lags for each residue
                if lag > 0 and lag in lag_consistency:
                    values.append(lag_consistency[lag])
                else:
                    values.append(0)
            residue_matrix.append(values[:10])  # Take first 10
        
        if any(any(v > 0 for v in row) for row in residue_matrix):
            im = axes[1, 1].imshow(residue_matrix, cmap='viridis', aspect='auto')
            axes[1, 1].set_xlabel('Cycle Index')
            axes[1, 1].set_ylabel('Residue mod 4')
            axes[1, 1].set_title('Period-4 Consistency Heatmap')
            plt.colorbar(im, ax=axes[1, 1])
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

def main():
    """Run initial periodicity archaeology analysis"""
    print("🔍 Beginning Periodicity Archaeology Investigation...")
    
    # Generate coupled logistic map trajectory
    trajectory = generate_coupled_logistic_lattice(
        r=3.865, 
        epsilon=0.132, 
        n_cells=100, 
        t_max=1000, 
        seed=42
    )
    
    print(f"Generated trajectory with shape: {trajectory.shape}")
    
    # Extract symbolic motifs
    motifs = extract_symbolic_motifs(trajectory, motif_width=4)
    print(f"Extracted {len(motifs)} time steps of motifs")
    
    # Compute temporal consistency
    lag_consistency = compute_temporal_consistency(motifs, max_lag=100)
    print(f"Computed consistency for {len(lag_consistency)} lags")
    
    # Analyze periodic structure
    period_analysis = analyze_periodic_structure(lag_consistency)
    
    # Save results
    results = {
        'parameters': {
            'r': 3.865,
            'epsilon': 0.132,
            'n_cells': 100,
            't_max': 1000,
            'motif_width': 4
        },
        'lag_consistency': lag_consistency,
        'period_analysis': period_analysis
    }
    
    import json
    with open('initial_analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Create visualization
    visualize_periodic_analysis(lag_consistency, period_analysis, 'initial_periodic_analysis.png')
    
    print("✅ Initial analysis completed!")
    print(f"Period-4 parity contrast: {period_analysis[4]['parity_contrast']:.3f}")
    print("Results saved to initial_analysis_results.json")
    print("Visualization saved to initial_periodic_analysis.png")

if __name__ == "__main__":
    main()