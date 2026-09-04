# Runner: timescale-gap resonance scan (v4 clean model)
import time
import numpy as np
from pathlib import Path
import importlib.util

OUT = Path('/home/runner/work/evolution_sandbox/evolution_sandbox/instances/shared_space')
spec = importlib.util.spec_from_file_location("v4c", OUT / "_v4_core.py")
v4c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v4c)
for _n in ["evolve","metrics_from_history","gap_law","OUT","sensitivity_proxy"]:
    globals()[_n] = getattr(v4c, _n)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def scan(r_values, e_values, N, steps, transient, method, N_fast, f_fast):
    rows = []
    for r in r_values:
        for eps in e_values:
            t0 = time.time()
            h, period = evolve(N, steps, transient, r, eps, seed=7, method=method, N_fast=N_fast, f_fast=f_fast)
            m = metrics_from_history(h, N, r, eps, method, N_fast, f_fast)
            row = {'method': method, 'N_fast': N_fast, 'f_fast': f_fast,
                   'N': N, 'steps': steps, 'transient': transient,
                   'r': float(r), 'epsilon': float(eps)}
            row.update(m)
            row['gap'] = N_fast
            row['C_gap'] = gap_law(N_fast)
            rows.append(row)
            print(f"[{method} g={N_fast} ff={f_fast:.1f}] r={r:.3f} eps={float(eps):.3f} "
                  f"o={m['order']:.3f} e={m['entropy']:.3f} s={m['sensitivity']:.3f} "
                  f"edge={m['boundary_complexity']:.3f} mp={m['motif_persistence']:.3f} "
                  f"bridge={m['bridge_score']:.3f} ({time.time()-t0:.1f}s)", flush=True)
    return rows

def heat(rows, key, r_values, e_values, fname, title):
    a = np.full((len(r_values), len(e_values)), np.nan)
    by = {(q['r'], q['epsilon']): q for q in rows}
    for i, r in enumerate(r_values):
        for j, eps in enumerate(e_values):
            q = by.get((r, eps))
            if q:
                a[i, j] = q[key]
    fig, ax = plt.subplots(figsize=(6, 4.5))
    im = ax.imshow(a, origin='lower', aspect='auto', cmap='viridis')
    ax.set_xticks(range(len(e_values))); ax.set_xticklabels([f"{e:.2f}" for e in e_values])
    ax.set_yticks(range(len(r_values))); ax.set_yticklabels([f"{r:.2f}" for r in r_values])
    ax.set_xlabel('epsilon (coupling)'); ax.set_ylabel('r (growth)')
    ax.set_title(title)
    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    fig.savefig(OUT / fname, dpi=110)
    plt.close(fig)
    print("saved", fname, flush=True)

def main():
    N = 64; steps = 150; transient = 80
    r_values = np.linspace(3.65, 3.95, 9)
    e_values = np.linspace(0.0, 1.0, 6)
    all_rows = []
    print("=== SCAN A: uniform baseline ===", flush=True)
    all_rows += scan(r_values, e_values, N, steps, transient, 'uniform', 1, 0.5)

    for N_fast, ff in [(2,0.5),(4,0.5),(8,0.5),(12,0.5),(16,0.5),(24,0.5)]:
        print(f"\n=== SCAN B: hetero gap={N_fast} f_fast={ff:.1f} ===", flush=True)
        all_rows += scan(r_values, e_values, N, steps, transient, 'hetero', N_fast, ff)

    import json
    (OUT / '_v4_results.json').write_text(json.dumps(all_rows, indent=2))
    print("\nSaved _v4_results.json", flush=True)

    # Gap-law aggregation: best bridge per config
    print("\n=== BEST BRIDGE PER CONFIG (timescale-gap prediction test) ===")
    print(f"{'config':24s} {'bridge':>8s} {'edge':>7s} {'sens':>7s} {'r':>6s} {'eps':>5s}")
    base = [r for r in all_rows if r['method'] == 'uniform']
    base_best = max(r['bridge_score'] for r in base)
    print(f"\nUniform baseline best bridge = {base_best:.4f}")
    prev = base_best
    print(f"{'uniform/gap=1':24s} {base_best:>8.4f} {'':7s} {'':7s} {'':>6s} {'':>5s}")
    for N_fast in [2,4,8,12,16,24]:
        rs = [r for r in all_rows if r['method'] == 'hetero' and r['N_fast'] == N_fast]
        b = max(r['bridge_score'] for r in rs)
        e = max(r['boundary_complexity'] for r in rs)
        s = min(r['sensitivity'] for r in rs)
        bb = max(rs, key=lambda q: q['bridge_score'])
        print(f"{'hetero/gap=%d'%N_fast:24s} {b:>8.4f} {e:>7.4f} {s:>7.4f} {bb['r']:>6.3f} {bb['epsilon']:>5.2f}")
        prev = b

    print("\nr19z prediction: bridge should rise with timescale gap N_fast.")
    print("\nDONE", flush=True)

if __name__ == '__main__':
    main()
