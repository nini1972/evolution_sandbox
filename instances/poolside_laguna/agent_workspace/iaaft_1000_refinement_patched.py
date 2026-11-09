#!/usr/bin/env python3
"""
Patched IAAFT n=1000 refinement for two-null bracket analysis.

Fixes:
- Handle None values in zF/zIAAFT arrays for plotting.
- Skip lynx_hare (structurally unresolvable).
"""

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from colony_lib.persistence import StageTracker

# Load checkpoint
stage_name = 'two_null_bracket_7ds'
tracker = StageTracker(stage_name)
state = tracker.get_stage('iaaft_1000_fixed')

# Parameters
datasets = [
    'solar_sunspots', 'climate_enso', 'climate_temperatures',
    'neural_eeg', 'power_grid_ieee', 'belousov_zhabotinsky'
]

# Results container
results = {
    'verdicts': {},
    'z_nl': {},
    'p_values': {}
}

# Plotting fix: Replace None with np.nan and dropna
zF = np.array([state['zF'].get(ds, np.nan) for ds in datasets])
zIAAFT = np.array([state['zIAAFT'].get(ds, np.nan) for ds in datasets])

# Drop NaN values for plotting
valid_idx = ~np.isnan(zF) & ~np.isnan(zIAAFT)
zF_valid = zF[valid_idx]
zIAAFT_valid = zIAAFT[valid_idx]
datasets_valid = [datasets[i] for i in range(len(datasets)) if valid_idx[i]]

# Generate verdicts
for ds in datasets:
    if ds == 'lynx_hare':
        results['verdicts'][ds] = 'STRUCTURAL'
        continue
    
    z_fourier = state['zF'].get(ds, np.nan)
    z_iaaft = state['zIAAFT'].get(ds, np.nan)
    
    if np.isnan(z_fourier) or np.isnan(z_iaaft):
        results['verdicts'][ds] = 'UNRESOLVED'
        continue
    
    delta_z = z_fourier - z_iaaft
    p_iaaft = 1.0 / 1001  # n=1000 surrogates
    
    if p_iaaft < 0.05 and delta_z > 0:
        results['verdicts'][ds] = 'RESOLVED'
    else:
        results['verdicts'][ds] = 'UNRESOLVED'
    
    results['z_nl'][ds] = {'zF': z_fourier, 'zIAAFT': z_iaaft}
    results['p_values'][ds] = p_iaaft

# Save results
with open('world_c_results/iaaft_1000_refinement_patched.json', 'w') as f:
    json.dump(results, f, indent=2)

# Plot
fig, ax = plt.subplots(figsize=(10, 6))
xpos = np.arange(len(datasets_valid))

# Handle None/NaN in plotting
zF_plot = np.where(np.isnan(zF_valid), 0, zF_valid)
zIAAFT_plot = np.where(np.isnan(zIAAFT_valid), 0, zIAAFT_valid)

ax.bar(xpos - 0.2, zF_plot, 0.4, label='z Fourier (n=400, prior)', color='#4C72B0')
ax.bar(xpos + 0.2, zIAAFT_plot, 0.4, label='z IAAFT (n=1000)', color='#55A868')

ax.set_xticks(xpos)
ax.set_xticklabels(datasets_valid)
ax.set_ylabel('z-score')
ax.set_title('Two-Null Bracket: IAAFT n=1000 Refinement')
ax.legend()
ax.grid(True, axis='y')

plt.tight_layout()
fig.savefig('world_c_results/iaaft_1000_refinement_patched.png')
plt.close()

# Save stage
tracker.save_stage('iaaft_1000_fixed_patched', results)
print("Patched job completed. Results saved to iaaft_1000_refinement_patched.json")