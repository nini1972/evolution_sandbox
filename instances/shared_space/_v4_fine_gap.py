# Fine-gap resonance scan: map the bridge-vs-gap curve with high resolution in small gaps
import json, time, importlib.util
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path('/home/runner/work/evolution_sandbox/evolution_sandbox/instances/shared_space')
spec = importlib.util.spec_from_file_location("v4c", OUT / "_v4_core.py")
v4c = importlib.util.module_from_spec(spec); spec.loader.exec_module(v4c)
evolve, metrics_from_history, gap_law = v4c.evolve, v4c.metrics_from_history, v4c.gap_law

def best_for(gap, seeds=4):
    best = 0.0
    for s in range(seeds):
        h, _ = evolve(64, 160, 100, 3.65 + 0.03*(gap % 3), 1.0 if gap<=6 else 0.83,
                      seed=s, method='hetero', N_fast=gap, f_fast=0.5)
        m = metrics_from_history(h, 64, 3.65, 1.0, 'hetero', gap, 0.5)
        best = max(best, m['bridge_score'])
    return best

# fine gaps 1..12 plus a few coarse larger
gaps = list(range(1, 13)) + [16, 20, 24]
emp = []
for g in gaps:
    b = best_for(g, seeds=3)
    emp.append(b)
    print(f"gap={g:2d} bridge={b:.4f}", flush=True)

emp = np.array(emp)
mono = np.array([gap_law(g) for g in gaps])

fig, ax = plt.subplots(figsize=(7,4.5))
ax.plot(gaps, emp, 'o-', color='crimson', lw=2, ms=7, label='empirical bridge')
ax.plot(gaps, mono, 's--', color='steelblue', lw=1.5, ms=6, label='monotonic gap_law()')
ax.axvspan(1, 4, alpha=0.08, color='green')
ax.set_xlabel('Timescale gap N_fast')
ax.set_ylabel('Bridge score')
ax.set_title('Resonance vs monotonic: fine gap scan')
ax.set_xticks(gaps)
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(OUT / 'v4_fine_gap_scan.png', dpi=120)
print("saved v4_fine_gap_scan.png", flush=True)

# Write results
res = {'gaps': gaps, 'empirical_bridge': emp.tolist(), 'monotonic_gap_law': mono.tolist()}
(OUT / '_v4_fine_gap.json').write_text(json.dumps(res, indent=2))
print("saved _v4_fine_gap.json", flush=True)

peak_idx = int(np.argmax(emp))
print(f"\nPeak bridge = {emp[peak_idx]:.4f} at gap = {gaps[peak_idx]}", flush=True)
print(f"Baseline (gap=1) = {emp[0]:.4f}")
