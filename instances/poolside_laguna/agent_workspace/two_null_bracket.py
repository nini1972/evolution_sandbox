#!/usr/bin/env python3
"""
Two-Null Bracket Pipeline for Period-4 Tongue in Coupled-Logistic Lattice.

Goal: Apply Fourier-phase + IAAFT surrogates to q-metric series and compute z_nl scores.
"""

import json
import numpy as np
from scipy.stats import zscore
from statsmodels.tsa.stattools import acf
from nolitsa import surrogates
from colony_lib.persistence import StageTracker

# Load artifacts
with open('world_c_results/p4_n_stress.json', 'r') as f:
    p4_data = json.load(f)

with open('world_c_results/p4_n_stress_state.json', 'r') as f:
    p4_state = json.load(f)

# Initialize StageTracker
stage_name = 'p4_two_null_bracket'
tracker = StageTracker(stage_name)

# Parameters
N_SURROGATES = 100  # Number of surrogates per trajectory
Q_LAG = 4            # Lag for q-metric (d₄/d₂)

# Results container
results = {
    'cells': [],
    'z_nl_fourier': [],
    'z_nl_iaaft': [],
    'q_observed': []
}

# Process each cell
def process_cell(cell_id, trajectory):
    """Generate surrogates and compute z_nl for a single trajectory."""
    q_obs = compute_q_metric(trajectory, Q_LAG)
    
    # Generate surrogates
    fourier_surr = [surrogates.fourier_phase(trajectory) for _ in range(N_SURROGATES)]
    iaaft_surr = [surrogates.iaaft(trajectory)[0] for _ in range(N_SURROGATES)]
    
    # Compute q-metric for surrogates
    q_fourier = [compute_q_metric(s, Q_LAG) for s in fourier_surr]
    q_iaaft = [compute_q_metric(s, Q_LAG) for s in iaaft_surr]
    
    # Compute z_nl scores
    z_nl_fourier = (q_obs - np.mean(q_fourier)) / np.std(q_fourier)
    z_nl_iaaft = (q_obs - np.mean(q_iaaft)) / np.std(q_iaaft)
    
    return {
        'cell_id': cell_id,
        'q_observed': q_obs,
        'z_nl_fourier': z_nl_fourier,
        'z_nl_iaaft': z_nl_iaaft,
        'q_fourier_mean': np.mean(q_fourier),
        'q_iaaft_mean': np.mean(q_iaaft)
    }

def compute_q_metric(series, lag):
    """Compute q-metric (d₄/d₂) for a given lag."""
    d2 = np.mean(np.abs(np.diff(series, n=2)))
    d4 = np.mean(np.abs(np.diff(series, n=4)))
    return d4 / d2 if d2 != 0 else np.nan

# Main loop
for N, data in p4_data.items():
    for cell_idx, cell in enumerate(p4_state[N]['cells']):
        if cell['is_p4']:
            trajectory = cell['trajectory']
            result = process_cell(f"N{N}_cell{cell_idx}", trajectory)
            results['cells'].append(result)
            results['z_nl_fourier'].append(result['z_nl_fourier'])
            results['z_nl_iaaft'].append(result['z_nl_iaaft'])
            results['q_observed'].append(result['q_observed'])

# Save results
with open('world_c_results/two_null_bracket_results.json', 'w') as f:
    json.dump(results, f, indent=2)

# Save stage
if not tracker.is_done('final'):
    tracker.save_stage('final', results)
    print("Saved stage 'final' and results to two_null_bracket_results.json")
else:
    print("Stage 'final' already exists. Skipping save.")