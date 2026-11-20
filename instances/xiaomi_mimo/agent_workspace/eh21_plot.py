#!/usr/bin/env python3
"""EH21 validation figure — reconstructed locally from eh21_validation.json
(job_xiaomi_mimo_1795055199_575b died only on an invalid color 'tab:navy'
 at the final plotting step; all gates PASSED and JSON was written)."""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

with open('world_c_results/eh21_validation.json') as f:
    D = json.load(f)

datasets = list(D['results'].keys())
B = [D['results'][d]['B'] for d in datasets]
spread = [D['results'][d]['B_spread'] for d in datasets]
Aceil = [D['results'][d]['A_ceiling_rate'] for d in datasets]
Cceil = [D['results'][d]['C_ceiling_rate'] for d in datasets]
G4p = [D['results'][d]['G4_p'] for d in datasets]

fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
xs = np.arange(len(datasets))

# Panel 1: estimator B with split-half spread
ax = axes[0]
ax.bar(xs, B, 0.55, yerr=spread, capsize=4, color='tab:blue', label='B (estimator)')
ax.axhline(1.0, ls='--', c='gray', lw=1, label='ceiling (A,C = 1.0)')
ax.set_xticks(xs); ax.set_xticklabels(datasets, rotation=25, ha='right')
ax.set_ylabel('B estimate'); ax.set_ylim(0, 1.05)
ax.set_title('G1/G2: estimator B\n(split-half spread shown)')
ax.legend(fontsize=8)

# Panel 2: ceiling rates A vs C (degeneracy discrimination)
ax = axes[1]
w = 0.35
ax.bar(xs - w/2, Aceil, w, color='tab:orange', label='A ceiling rate')
ax.bar(xs + w/2, Cceil, w, color='tab:green', label='C ceiling rate')
ax.set_xticks(xs); ax.set_xticklabels(datasets, rotation=25, ha='right')
ax.set_ylabel('ceiling rate'); ax.set_ylim(0, 1.1)
ax.set_title('G2b: discrimination range=%.2f' % D['discrimination_range'])
ax.legend(fontsize=8)

# Panel 3: posterior-predictive p-values
ax = axes[2]
ax.bar(xs, G4p, 0.55, color='tab:red', label='G4 p-value')
ax.axhline(0.05, ls='--', c='k', lw=1, label='alpha=0.05')
ax.set_xticks(xs); ax.set_xticklabels(datasets, rotation=25, ha='right')
ax.set_ylabel('p')
ax.set_ylim(0, 0.08)
ax.set_title('G4: posterior-predictive GOF\nverdict: %s' % D['verdict'])
ax.legend(fontsize=8)

fig.suptitle('EH21 — degeneracy-aware gates (stability + discrimination + GOF) '
             'for estimator B  [%s]' % D['verdict'], fontsize=11)
fig.tight_layout()
fig.savefig('world_c_results/eh21_validation.png', dpi=130)
print('saved world_c_results/eh21_validation.png; verdict =', D['verdict'])