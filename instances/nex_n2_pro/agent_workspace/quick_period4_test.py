#!/usr/bin/env python3
"""
Quick test of period-4 hypothesis with reduced parameters for fast local execution.
"""

import numpy as np
import matplotlib.pyplot as plt

def generate_coupled_map_lattice(r=3.8625, epsilon=0.132, n=100, t_max=500, seed=42):
    """Generate coupled logistic map lattice data - reduced size"""
    np.random.seed(seed)
    x = np.random.rand(n)
    trajectory = np.zeros((t_max, n))
    
    for t in range(t_max):
        trajectory[t] = x.copy()
        f_x = r * x * (1 - x)
        f_left = r * np.roll(x, 1) * (1 - np.roll(x, 1))
        f_right = r * np.roll(x, -1) * (1 - np.roll(x, -1))
        x = (1 - epsilon) * f_x + epsilon * 0.5 * (f_left + f_right)
        
    return trajectory

def extract_motifs(trajectory, motif_width=4, threshold=0.5):
    """Extract binary motifs from trajectory"""
    n_cells = trajectory.shape[1]
    n_time = trajectory.shape[0]
    binary_traj = (trajectory > threshold).astype(int)
    motifs = []
    
    for t in range(n_time):
        cell_motifs = []
        for i in range(n_cells):
            start_idx = i - motif_width // 2
            motif_indices = [(start_idx + j) % n_cells for j in range(motif_width)]
            motif = tuple(binary_traj[t, motif_indices])
            cell_motifs.append(motif)
        motifs.append(cell_motifs)
    
    return np.array(motifs)

def compute_lag_consistency(motifs, max_lag=50, step=1):
    """Compute motif consistency at different lags - reduced range"""
    n_time, n_cells = motifs.shape
    lags = list(range(step, min(max_lag + 1, n_time), step))
    consistency = []
    
    for lag in lags:
        matches = 0
        total = 0
        for t in range(n_time - lag):
            for i in range(n_cells):
                if np.array_equal(motifs[t, i], motifs[t + lag, i]):
                    matches += 1
                total += 1
        consistency.append(matches / total if total > 0 else 0)
    
    return np.array(lags), np.array(consistency)

def analyze_period_structure(lags, consistency, period=4):
    """Analyze consistency by residue classes modulo period"""
    residue_classes = {}
    for i, lag in enumerate(lags):
        residue = lag % period
        if residue not in residue_classes:
            residue_classes[residue] = []
        residue_classes[residue].append(consistency[i])
    
    residue_means = {res: np.mean(vals) for res, vals in residue_classes.items()}
    return residue_means, residue_classes

# Run quick test
print("Running quick period-4 test...")
trajectory = generate_coupled_map_lattice(r=3.8625, epsilon=0.132, n=100, t_max=500, seed=42)
motifs = extract_motifs(trajectory, motif_width=4)
lags, consistency = compute_lag_consistency(motifs, max_lag=50, step=1)
residue_means, residue_classes = analyze_period_structure(lags, consistency, period=4)

# Traditional even/odd analysis
even_consistency = [consistency[i] for i, lag in enumerate(lags) if lag % 2 == 0]
odd_consistency = [consistency[i] for i, lag in enumerate(lags) if lag % 2 == 1]
even_mean = np.mean(even_consistency) if even_consistency else 0
odd_mean = np.mean(odd_consistency) if odd_consistency else 0
parity_index = max(0, min(1, even_mean - odd_mean))

# Period-4 analysis
mod0_mean = residue_means.get(0, 0)
mod1_mean = residue_means.get(1, 0)
mod2_mean = residue_means.get(2, 0)
mod3_mean = residue_means.get(3, 0)
aligned_mean = np.mean([mod0_mean, mod2_mean])
antiphase_mean = np.mean([mod1_mean, mod3_mean])
phase_contrast = aligned_mean - antiphase_mean

print(f"\nQuick Test Results:")
print(f"Traditional Parity Index: {parity_index:.4f}")
print(f"Phase Contrast (mod 4): {phase_contrast:.4f}")
print(f"Residue means: 0={mod0_mean:.4f}, 1={mod1_mean:.4f}, 2={mod2_mean:.4f}, 3={mod3_mean:.4f}")

# Save quick results
import json
quick_results = {
    'parity_index': parity_index,
    'phase_contrast': phase_contrast,
    'residue_means': residue_means,
    'even_mean': even_mean,
    'odd_mean': odd_mean
}
with open('quick_period4_results.json', 'w') as f:
    json.dump(quick_results, f, indent=2)

print("\nQuick test completed! Results saved to quick_period4_results.json")