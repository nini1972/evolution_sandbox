# Reconstruct true bridge-vs-gap curve from the v4 parameter scan + compare to monotonic gap law
import json, importlib.util
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path('../../instances/shared_space') if False else Path('/home/runner/work/evolution_sandbox/evolution_sandbox/instances/shared_space')
spec = importlib.util.spec_from_file_location("v4c", OUT / "_v4_core.py")
v4c = importlib.util.module_from_spec(spec); spec.loader.exec_module(v4c)
evolve, metrics_from_history, gap_law = v4c.evolve, v4c.metrics_from_history, v4c.gap_law

rows = json.loads((OUT / '_v4_results.json').read_text())
from collections import defaultdict
d = defaultdict(list)
for r in rows: d[r['N_fast']].append(r)
gaps = sorted(d.keys())
emp_best = [max((r['bridge_score'] for r in d[g]), default=0) for g in gaps]
emp_mean = [np.mean([r['bridge_score'] for r in d[g]]) for g in gaps]
emp_sens = [min((r['sensitivity'] for r in d[g]), default=0) for g in gaps]
mono = [gap_law(g) for g in gaps]

fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))

ax = axes[0]
ax.plot(gaps, emp_best, 'o-', color='crimson', lw=2, ms=8, label='empirical best bridge')
ax.plot(gaps, emp_mean, 's--', color='darkorange', lw=1.5, ms=6, label='empirical mean bridge')
ax.plot(gaps, mono, '^:', color='steelblue', lw=1.5, ms=6, label='monotonic gap_law()')
ax.axhline(emp_best[0] if gaps[0]==1 else (max((r['bridge_score'] for r in rows if r['N_fast']==1)) if any(r['N_fast']==1 for r in rows) else 0.3), color='gray', ls='--', alpha=0.4, label='uniform baseline (gap=1)')
ax.set_xlabel('Timescale gap N_fast')
ax.set_ylabel('Bridge score')
ax.set_title('Bridge vs timescale gap: resonance (non-monotonic) vs monotonic law')
ax.set_xticks(gaps)
ax.legend(fontsize=8)
ax.grid(alpha=0.3)

ax = axes[1]
ax.plot(gaps, emp_sens, 'd-', color='seagreen', lw=2, ms=8)
ax.set_xlabel('Timescale gap N_fast')
ax.set_ylabel('Min sensitivity (divergence)')
ax.set_title('Sensitivity suppression (chaos mixing)')
ax.set_xticks(gaps)
ax.grid(alpha=0.3)

fig.suptitle('v4 Resonance Gap Law: empirical parameter scan vs monotonic prediction', fontsize=11)
fig.tight_layout()
fig.savefig(OUT / 'v4_fine_gap_scan.png', dpi=120)
print("saved v4_fine_gap_scan.png", flush=True)

# Also save a cleaner single plot focusing on the curve
fig, ax = plt.subplots(figsize=(7,4.5))
ax.plot(gaps, emp_best, 'o-', color='crimson', lw=2.5, ms=9, label='empirical best (scan)')
ax.plot(gaps, emp_mean, 's--', color='darkorange', lw=1.5, ms=6, label='empirical mean')
ax.plot(gaps, mono, '^:', color='steelblue', lw=2, ms=7, label='monotonic gap_law()')
ub = max((r['bridge_score'] for r in rows if r['N_fast']==1), default=0.3)
ax.axhline(ub, color='gray', ls='--', alpha=0.5, label=f'uniform baseline ({ub:.2f})')
ax.set_xlabel('Timescale gap N_fast')
ax.set_ylabel('Best bridge score')
ax.set_title('r19z: bridge peaks at intermediate gap (resonance), NOT monotonic')
ax.set_xticks(gaps)
ax.legend(fontsize=8)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(OUT / 'v4_gap_law_comparison.png', dpi=120)
print("saved v4_gap_law_comparison.png", flush=True)

# Summary stats
gap_peak = gaps[int(np.argmax(emp_best))]
print(f"\nPeak bridge {max(emp_best):.3f} at gap={gap_peak}", flush=True)
print(f"Uniform baseline (gap=1): {ub:.3f}", flush=True)
print(f"Resonance ratio (peak/baseline): {max(emp_best)/max(ub,1e-9):.2f}x", flush=True)
print(f"Large-gap (24) bridge: {emp_best[-1]:.3f} (decays from peak)", flush=True)
