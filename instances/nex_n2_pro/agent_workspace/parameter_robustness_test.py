#!/usr/bin/env python3
"""
Test robustness of period-4 structure across parameter variations.
"""

import numpy as np
import json

def generate_coupled_map_lattice(r=3.8625, epsilon=0.132, n=100, t_max=500, seed=42):
    """Generate coupled logistic map lattice data"""
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
    
    return motifs

def compute_phase_contrast(motifs, max_lag=50):
    """Compute phase contrast for period-4 analysis"""
    n_time = len(motifs)
    n_cells = len(motifs[0]) if n_time > 0 else 0
    lags = list(range(1, min(max_lag + 1, n_time)))
    consistency = []
    
    for lag in lags:
        matches = 0
        total = 0
        for t in range(n_time - lag):
            for i in range(n_cells):
                if motifs[t][i] == motifs[t + lag][i]:
                    matches += 1
                total += 1
        consistency.append(matches / total if total > 0 else 0)
    
    # Period-4 analysis
    residue_classes = {}
    for i, lag in enumerate(lags):
        residue = int(lag % 4)
        if residue not in residue_classes:
            residue_classes[residue] = []
        residue_classes[residue].append(float(consistency[i]))
    
    residue_means = {res: float(np.mean(vals)) for res, vals in residue_classes.items()}
    mod0_mean = residue_means.get(0, 0.0)
    mod1_mean = residue_means.get(1, 0.0)
    mod2_mean = residue_means.get(2, 0.0)
    mod3_mean = residue_means.get(3, 0.0)
    aligned_mean = float(np.mean([mod0_mean, mod2_mean]))
    antiphase_mean = float(np.mean([mod1_mean, mod3_mean]))
    phase_contrast = aligned_mean - antiphase_mean
    
    return phase_contrast, residue_means

# Test different parameter combinations
parameter_sets = [
    {"r": 3.8625, "epsilon": 0.132, "label": "baseline"},
    {"r": 3.8600, "epsilon": 0.132, "label": "r_minus_0.0025"},
    {"r": 3.8650, "epsilon": 0.132, "label": "r_plus_0.0025"},
    {"r": 3.8625, "epsilon": 0.130, "label": "epsilon_minus_0.002"},
    {"r": 3.8625, "epsilon": 0.134, "label": "epsilon_plus_0.002"},
]

results = {}

for params in parameter_sets:
    print(f"Testing {params['label']}: r={params['r']}, epsilon={params['epsilon']}")
    trajectory = generate_coupled_map_lattice(
        r=params['r'], 
        epsilon=params['epsilon'], 
        n=100, 
        t_max=500, 
        seed=42
    )
    motifs = extract_motifs(trajectory, motif_width=4)
    phase_contrast, residue_means = compute_phase_contrast(motifs, max_lag=50)
    
    results[params['label']] = {
        'r': float(params['r']),
        'epsilon': float(params['epsilon']),
        'phase_contrast': float(phase_contrast),
        'residue_means': {int(k): float(v) for k, v in residue_means.items()}
    }
    
    print(f"  Phase contrast: {phase_contrast:.4f}")

# Save results
with open('parameter_robustness_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nParameter robustness test completed!")
print("Results saved to parameter_robustness_results.json")