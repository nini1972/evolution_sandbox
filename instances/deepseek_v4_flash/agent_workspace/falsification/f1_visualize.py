#!/usr/bin/env python3
"""F1 visualization + baseline comparison.
Shows where deepseek-vs-tencent similarity falls within the ecosystem-wide
distribution of pairwise cosine distances. If the "clone" pair sits inside the
normal crowd, the "near-verbatim clone" claim is falsified.
"""
import os, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

DW = '/home/runner/work/evolution_sandbox/evolution_sandbox/instances/deepseek_v4_flash/agent_workspace'
rep = json.load(open(os.path.join(DW, 'falsification', 'f1_clone_audit.json')))

all_d = [v['cosine_dist'] for v in rep['pairwise'].values()]
all_j = [v['jaccard_dist'] for v in rep['pairwise'].values()]

# Targeted pairs
targets = {
    'ds current vs tencent': rep['targets']['deepseek_v4_flash vs tencent_hy3']['cosine_dist'],
    'ds ORIGINAL vs tencent': rep['targets']['deepseek_v4_flash__ORIGINAL vs tencent_hy3']['cosine_dist'],
    'ds current vs ds ORIGINAL': rep['targets']['deepseek_v4_flash vs deepseek_v4_flash__ORIGINAL']['cosine_dist'],
}

fig, ax = plt.subplots(1, 2, figsize=(14, 5))
# Cosine
ax[0].hist(all_d, bins=20, color='#4a90d9', alpha=0.7, edgecolor='white')
ax[0].axvline(np.mean(all_d), color='k', ls='--', lw=1.2, label=f'ecosystem mean {np.mean(all_d):.3f}')
for label, val in targets.items():
    ax[0].axvline(val, lw=2, ls='-')
    ax[0].annotate(f'{label}\n{val:.3f}', (val, ax[0].get_ylim()[1]*0.9), rotation=0, ha='center', fontsize=8)
ax[0].set_title('Cosine distance distribution (all core pairs)\nlower = more similar')
ax[0].set_xlabel('cosine distance')
ax[0].legend()
# Jaccard
ax[1].hist(all_j, bins=20, color='#e07b39', alpha=0.7, edgecolor='white')
ax[1].axvline(np.mean(all_j), color='k', ls='--', lw=1.2, label=f'ecosystem mean {np.mean(all_j):.3f}')
for label, val in [('ds cur vs tencent', rep['targets']['deepseek_v4_flash vs tencent_hy3']['jaccard_dist']),
                   ('ds ORIG vs tencent', rep['targets']['deepseek_v4_flash__ORIGINAL vs tencent_hy3']['jaccard_dist'])]:
    ax[1].axvline(val, lw=2, ls='-')
    ax[1].annotate(f'{label}\n{val:.3f}', (val, ax[1].get_ylim()[1]*0.9), rotation=0, ha='center', fontsize=8)
ax[1].set_title('Jaccard distance distribution (all core pairs)\nlower = more similar')
ax[1].set_xlabel('jaccard distance')
plt.tight_layout()
out = os.path.join(DW, 'falsification', 'f1_clone_audit.png')
plt.savefig(out, dpi=110)
print('saved', out)

# Percentile of each target within the ecosystem baseline
import scipy.stats as st
for label, val in targets.items():
    pct = (np.array(all_d) < val).mean() * 100
    print(f"{label}: cosine_dist={val:.4f} -> percentile {pct:.1f}% (lower = more similar than this pair)")
