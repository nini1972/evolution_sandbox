#!/usr/bin/env python3
"""
Rebuild the two_null_bracket_7ds stage from @claude_sonnet_4_5's artifacts.
"""

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from colony_lib.persistence import StageTracker

# Load @claude_sonnet_4_5's artifacts
with open('world_c_results/iaaft_1000_refinement.json', 'r') as f:
    iaaft_results = json.load(f)

# Rebuild state
state = {
    'zF': {},
    'zIAAFT': {},
    'verdicts': {}
}

# Populate state from iaaft_results
datasets = [
    'solar_sunspots', 'climate_enso', 'climate_temperatures',
    'neural_eeg', 'power_grid_ieee', 'belousov_zhabotinsky', 'lynx_hare'
]

for ds in datasets:
    if ds == 'lynx_hare':
        state['verdicts'][ds] = 'STRUCTURAL'
        continue
    
    # Extract zF (Fourier) and zIAAFT (IAAFT)
    state['zF'][ds] = iaaft_results['results'][ds]['fourier_z_used']
    state['zIAAFT'][ds] = iaaft_results['results'][ds]['iaaft']['z']
    
    # Extract verdict
    if iaaft_results['verdict'][ds]:
        state['verdicts'][ds] = 'RESOLVED'
    else:
        state['verdicts'][ds] = 'UNRESOLVED'

# Save stage
tracker = StageTracker('two_null_bracket_7ds')
tracker.save_stage('iaaft_1000_fixed_rebuilt', state)

# Generate plot
fig, ax = plt.subplots(figsize=(10, 6))
xpos = np.arange(len(datasets) - 1)  # Exclude lynx_hare

# Extract z-scores
zF = np.array([state['zF'].get(ds, np.nan) for ds in datasets if ds != 'lynx_hare'])
zIAAFT = np.array([state['zIAAFT'].get(ds, np.nan) for ds in datasets if ds != 'lynx_hare'])

# Handle NaN values
zF_plot = np.where(np.isnan(zF), 0, zF)
zIAAFT_plot = np.where(np.isnan(zIAAFT), 0, zIAAFT)

ax.bar(xpos - 0.2, zF_plot, 0.4, label='z Fourier (n=400, prior)', color='#4C72B0')
ax.bar(xpos + 0.2, zIAAFT_plot, 0.4, label='z IAAFT (n=1000)', color='#55A868')

ax.set_xticks(xpos)
ax.set_xticklabels([ds for ds in datasets if ds != 'lynx_hare'])
ax.set_ylabel('z-score')
ax.set_title('Two-Null Bracket: IAAFT n=1000 Refinement (Rebuilt)')
ax.legend()
ax.grid(True, axis='y')

plt.tight_layout()
fig.savefig('world_c_results/iaaft_1000_refinement_rebuilt.png')
plt.close()

print("Stage rebuilt and saved as 'iaaft_1000_fixed_rebuilt'.")