# Summary visualization for v4 coupled logistic lattice (timescale-gap test)
import json, importlib.util
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path('/home/runner/work/evolution_sandbox/evolution_sandbox/instances/shared_space')
spec = importlib.util.spec_from_file_location("v4c", OUT / "_v4_core.py")
v4c = importlib.util.module_from_spec(spec); spec.loader.exec_module(v4c)

rows = json.loads((OUT / '_v4_results.json').read_text())

# Aggregate by config: best bridge per N_fast
configs = {}
for r in rows:
    key = (r['method'], r['N_fast'])
    if key not in configs:
        configs[key] = []
    configs[key].append(r)

gaps = sorted({r['N_fast'] for r in rows})
uniform_best = max((r['bridge_score'] for r in rows if r['method']=='uniform'), default=0)
hetero_bridges = []
for g in gaps:
    if g == 1:
        hetero_bridges.append(uniform_best)
    else:
        rs = [r for r in rows if r['method']=='hetero' and r['N_fast']==g]
        hetero_bridges.append(max((r['bridge_score'] for r in rs), default=0))

fig, axes = plt.subplots(1, 3, figsize=(16, 4.5))

# 1. Bridge vs timescale gap (r19z prediction)
ax = axes[0]
ax.plot([1]+gaps, [uniform_best]+hetero_bridges, 'o-', color='crimson', lw=2, ms=8)
ax.axhline(uniform_best, color='gray', ls='--', alpha=0.5, label='uniform baseline')
ax.set_xlabel('Timescale gap N_fast')
ax.set_ylabel('Best bridge score')
ax.set_title('r19z: bridge rises with timescale gap')
ax.set_xticks([1]+gaps)
ax.legend()
ax.grid(alpha=0.3)

# 2. Sensitivity suppression vs gap
hetero_sens = []
for g in gaps:
    rs = [r for r in rows if r['method']=='hetero' and r['N_fast']==g]
    hetero_sens.append(min((r['sensitivity'] for r in rs), default=0))
ax = axes[1]
ax.plot(gaps, hetero_sens, 's-', color='steelblue', lw=2, ms=8)
ax.set_xlabel('Timescale gap N_fast')
ax.set_ylabel('Min sensitivity (divergence)')
ax.set_title('Chaos mixing suppressed by slow scaffold')
ax.set_xticks(gaps)
ax.grid(alpha=0.3)

# 3. Entropy vs bridge scatter (structure trade-off)
ax = axes[2]
for g in gaps:
    rs = [r for r in rows if r['method']=='hetero' and r['N_fast']==g]
    if not rs: continue
    es = [r['entropy'] for r in rs]
    bs = [r['bridge_score'] for r in rs]
    ax.scatter(es, bs, s=20, alpha=0.6, label=f'gap={g}')
ax.set_xlabel('Entropy (spatiotemporal)')
ax.set_ylabel('Bridge score')
ax.set_title('Structure vs disorder trade-off')
ax.legend(fontsize=7)
ax.grid(alpha=0.3)

fig.suptitle('v4 Coupled Logistic Lattice: Timescale-Resonance Gap Law', fontsize=12)
fig.tight_layout()
fig.savefig(OUT / 'v4_summary.png', dpi=120)
print("saved v4_summary.png", flush=True)

# Also heatmap of bridge for gap=16
g = 16
rs = sorted([r for r in rows if r['method']=='hetero' and r['N_fast']==g], key=lambda r:(r['r'], r['epsilon']))
r_vals = sorted({r['r'] for r in rs})
e_vals = sorted({r['epsilon'] for r in rs})
a = np.full((len(r_vals), len(e_vals)), np.nan)
by = {(r['r'], r['epsilon']): r for r in rs}
for i, rv in enumerate(r_vals):
    for j, ev in enumerate(e_vals):
        q = by.get((rv, ev))
        if q: a[i,j] = q['bridge_score']
fig, ax = plt.subplots(figsize=(6,4.5))
im = ax.imshow(a, origin='lower', aspect='auto', cmap='plasma')
ax.set_xticks(range(len(e_vals))); ax.set_xticklabels([f"{e:.2f}" for e in e_vals])
ax.set_yticks(range(len(r_vals))); ax.set_yticklabels([f"{r:.3f}" for r in r_vals])
ax.set_xlabel('epsilon'); ax.set_ylabel('r'); ax.set_title(f'Bridge score heatmap (gap={g})')
fig.colorbar(im, ax=ax); fig.tight_layout()
fig.savefig(OUT / 'v4_bridge_heatmap_g16.png', dpi=110)
print("saved v4_bridge_heatmap_g16.png", flush=True)
