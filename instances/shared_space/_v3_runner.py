# Coupled Logistic Lattice - Phase Scan v3 runner: tests r19z timescale-gap prediction
import json, math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from _v3_core import (evolve, metrics_from_history, gap_law, OUT,
                      mat_for) if False else (None,)  # placeholder to satisfy import; real import below

import importlib.util
spec = importlib.util.spec_from_file_location("v3c", OUT / "_v3_core.py")
v3c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v3c)
for _n in ["evolve","metrics_from_history","gap_law","mat_for","OUT"]:
    globals()[_n] = getattr(v3c, _n)

def scan(r_values, e_values, N, steps, transient, method, N_fast, f_fast, seed_base=10000):
    rows = []
    for ri, r in enumerate(r_values):
        for ei, eps in enumerate(e_values):
            h = evolve(N, steps, transient, float(r), float(eps),
                       seed=seed_base + ri * 100 + ei, N_fast=N_fast,
                       f_fast=f_fast, method=method)
            m = metrics_from_history(h, N, r, eps, method, N_fast, f_fast)
            row = {'r': float(r), 'epsilon': float(eps), 'method': method,
                   'N': N, 'steps': steps, 'transient': transient,
                   'N_fast': N_fast, 'f_fast': f_fast}
            row.update(m)
            rows.append(row)
            print(f"[{method} g={N_fast} ff={f_fast:.1f}] r={r:.3f} eps={eps:.3f} "
                  f"o={m['order']:.3f} e={m['entropy']:.3f} s={m['sensitivity']:.3f} "
                  f"edge={m['boundary_complexity']:.3f} bridge={m['bridge_score']:.4f}", flush=True)
    return rows

def heat(path, data, title, cmap, vmin=None, vmax=None, rv=None, ev=None):
    fig, ax = plt.subplots(figsize=(11, 6.5))
    fig.patch.set_facecolor('#07111f'); ax.set_facecolor('#0b1423')
    if rv is not None:
        im = ax.imshow(data, origin='lower', aspect='auto', cmap=cmap, vmin=vmin, vmax=vmax,
                       extent=[ev.min(), ev.max(), rv.min(), rv.max()])
    else:
        im = ax.imshow(data, origin='lower', aspect='auto', cmap=cmap, vmin=vmin, vmax=vmax)
    ax.set_title(title, color='#e6edf3')
    ax.set_xlabel('epsilon', color='#c8d7ea'); ax.set_ylabel('r', color='#c8d7ea')
    ax.tick_params(colors='#c8d7ea')
    cb = fig.colorbar(im, ax=ax); cb.ax.yaxis.set_tick_params(color='#c8d7ea')
    plt.tight_layout()
    plt.savefig(path, dpi=170, facecolor=fig.get_facecolor()); plt.close(fig)

def summarize(rows):
    by_cfg = {}
    for q in rows:
        by_cfg.setdefault((q['method'], q['N_fast'], q['f_fast']), []).append(q)
    print("\n=== BEST BRIDGE PER CONFIG (r19z timescale-gap prediction test) ===", flush=True)
    print(f"{'config':<26}{'best_bridge':>13}{'C(gap)':>10}{'r':>8}{'eps':>7}", flush=True)
    table = []
    for key, qs in sorted(by_cfg.items(), key=lambda kv: gap_law(kv[0][1]) if kv[0][0]=='hetero' else 0):
        top = max(qs, key=lambda q: q['bridge_score'])
        method, Nf, ff = key
        C = gap_law(Nf) if method == 'hetero' else gap_law(1)
        cfg = f"{method[:4]}/gap={Nf}/ff={ff:.1f}"
        print(f"{cfg:<26}{top['bridge_score']:>13.4f}{C:>10.4f}{top['r']:>8.3f}{top['epsilon']:>7.2f}", flush=True)
        table.append((method, Nf, ff, top, C))
    ub = max(by_cfg[('uniform',1,0.5)], key=lambda q: q['bridge_score'])['bridge_score']
    print(f"\nUniform baseline best bridge = {ub:.4f}", flush=True)
    # monotonic check across gap
    het = [(Nf,C,top['bridge_score']) for method,Nf,ff,top,C in table if method=='hetero' and ff in (0.3,0.5,0.7)]
    print("\nr19z prediction: bridge should rise with timescale gap N_fast.", flush=True)
    return table

def make_predictive_plot(table):
    # best bridge vs timescale gap, with r19z gap law overlay (normalized)
    gaps = []; bridges = []
    for method, Nf, ff, top, C in table:
        gaps.append(Nf); bridges.append(top['bridge_score'])
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('#07111f'); ax.set_facecolor('#0b1423')
    # uniform baseline
    ub = max([t for t in table if t[0]=='uniform'], key=lambda t:t[3]['bridge_score'])
    ax.scatter([1], [ub[3]['bridge_score']], color='#ff8c00', s=120, zorder=5, label='uniform (gap=1)')
    # hetero
    xs = [t[1] for t in table if t[0]=='hetero']
    ys = [t[3]['bridge_score'] for t in table if t[0]=='hetero']
    ax.scatter(xs, ys, color='#00d6ff', s=100, zorder=5, label='hetero (observed bridge)')
    # r19z gap law curve (scaled: normalized to uniform baseline max so shapes comparable)
    gl = [gap_law(Nf) for Nf in range(1, 22)]
    scale = ub[3]['bridge_score'] / max(gl[0], 1e-9) if gl[0] else 1
    ax.plot(list(range(1, 22)), [g*scale for g in gl], color='#7c3aed', ls='--', lw=1.6,
            label=r'r19z gap law $C(N)=0.793(1-e^{-N/11.2})$ (scaled)')
    ax.set_xscale('log'); ax.set_xlabel('Timescale gap N_fast', color='#c8d7ea')
    ax.set_ylabel('Best bridge score (max over r,eps)', color='#c8d7ea')
    ax.set_title('r19z prediction test: bridge score vs timescale gap\n(bridge should rise with heterogeneity)', color='#e6edf3')
    ax.tick_params(colors='#c8d7ea'); ax.legend(facecolor='#141e2e', edgecolor='#334760', labelcolor='#c8d7ea')
    plt.tight_layout(); plt.savefig(OUT/'r19z_prediction_test.png', dpi=170, facecolor=fig.get_facecolor()); plt.close(fig)

def main():
    N = 128; steps = 400; transient = 400
    r_values = np.linspace(3.65, 3.95, 21)
    e_values = np.linspace(0.0, 1.0, 11)
    all_rows = []
    print("=== SCAN A: uniform baseline (higher res) ===", flush=True)
    all_rows += scan(r_values, e_values, N, steps, transient, 'uniform', 1, 0.5)
    for N_fast, ff in [(2,0.5),(4,0.5),(6,0.5),(8,0.5),(10,0.5),(12,0.5),(16,0.5),(20,0.5)]:
        print(f"\n=== SCAN B: hetero gap={N_fast} f_fast={ff:.1f} ===", flush=True)
        all_rows += scan(r_values, e_values, N, steps, transient, 'hetero', N_fast, ff)
    (OUT/'coupled_lattice_phase_scan_hetero.json').write_text(json.dumps(all_rows, indent=2))
    tb = summarize(all_rows)
    make_predictive_plot(tb)
    print("\nDONE", flush=True)

if __name__ == '__main__':
    main()
