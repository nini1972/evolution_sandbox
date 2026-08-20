import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

OUT = Path('../../shared_space')
OUT.mkdir(exist_ok=True)

def evolve(N, steps, transient, r, eps, seed=0):
    rng = np.random.default_rng(seed)
    x = rng.uniform(0.05, 0.95, size=N).astype(np.float64)
    for _ in range(transient):
        y = r * x * (1.0 - x)
        x = (1.0 - eps) * y + 0.5 * eps * (np.roll(y, 1) + np.roll(y, -1))
        x = np.clip(x, 0.0, 1.0)
    h = np.empty((steps, N), dtype=np.float64)
    for t in range(steps):
        y = r * x * (1.0 - x)
        x = (1.0 - eps) * y + 0.5 * eps * (np.roll(y, 1) + np.roll(y, -1))
        x = np.clip(x, 0.0, 1.0)
        h[t] = x
    return h

def entropy_hist(vals, bins=32):
    hist, _ = np.histogram(vals, bins=bins, range=(0.0, 1.0))
    p = hist / max(int(hist.sum()), 1)
    p = p[p > 0]
    return float(-(p * np.log(p + 1e-15)).sum() / np.log(bins))

def sync_order(h):
    v = h.var(axis=1)
    obs = max(float(h.max() - h.min()), 1e-12)
    return float(np.clip(1.0 - np.mean(v / (obs * obs)), 0.0, 1.0))

def spatial_entropy(h, bins=32):
    return entropy_hist(h.ravel(), bins=bins)

def temporal_entropy(h, bins=32, sites=32):
    n = h.shape[1]
    js = np.linspace(0, n - 1, min(sites, n)).astype(int)
    return float(np.mean([entropy_hist(h[:, j], bins=bins) for j in js]))

def edge_density(h):
    d = np.abs(np.roll(h, -1, axis=1) - h)
    return float(np.mean(d > 0.45))

def sensitivity_proxy(N, r, eps, trials=3, transient=120):
    rng = np.random.default_rng(1234)
    vals = []
    for _ in range(trials):
        a = rng.uniform(0.05, 0.95, size=N)
        b = a.copy()
        b[rng.integers(0, N)] += 1e-6
        for _ in range(transient):
            ya = r * a * (1.0 - a)
            a = np.clip((1.0 - eps) * ya + 0.5 * eps * (np.roll(ya, 1) + np.roll(ya, -1)), 0.0, 1.0)
            yb = r * b * (1.0 - b)
            b = np.clip((1.0 - eps) * yb + 0.5 * eps * (np.roll(yb, 1) + np.roll(yb, -1)), 0.0, 1.0)
        vals.append(min(1.0, max(0.0, float(np.mean(np.abs(a - b)) / 0.5))))
    return float(np.mean(vals))

def phase_var(h):
    th = np.arctan2(2.0 * h[-1] - 1.0, np.ones_like(h[-1]))
    R = math.hypot(float(np.mean(np.cos(th))), float(np.mean(np.sin(th))))
    return float(1.0 - R)

def cluster_count(h):
    s = h[-1] >= 0.5
    return int((np.diff(s.astype(int)) != 0).sum() + 1)

def motif_persistence(h, window=10):
    if h.shape[0] <= window:
        return 0.0
    a = 2.0 * (h[window:] >= 0.5).astype(np.float64) - 1.0
    b = 2.0 * (h[:-window] >= 0.5).astype(np.float64) - 1.0
    return float(np.mean(a * b))

def bridge(o, e, s, b, p):
    co = max(0.0, 1.0 - abs(o - e))
    return float(max(0.0, o * e * s * (0.65 + 0.35 * b) * (0.5 + 0.5 * max(0.0, p)) * co))

def save_heatmaps(rv, ev, grid):
    R = len(rv)
    E = len(ev)
    def heat(metric, cmap='viridis', title=None, vmin=None, vmax=None):
        arr = np.zeros((E, R))
        for ei in range(E):
            for ri in range(R):
                arr[E - 1 - ei, ri] = grid[ri][ei][metric]
        if vmin is None:
            vmin = float(np.nanmin(arr))
        if vmax is None:
            vmax = float(np.nanmax(arr))
        fig, ax = plt.subplots(figsize=(11, 7))
        fig.patch.set_facecolor('#07111f')
        ax.set_facecolor('#0b1423')
        im = ax.imshow(arr, extent=[rv.min(), rv.max(), ev.min(), ev.max()], aspect='auto', origin='lower', cmap=cmap, vmin=vmin, vmax=vmax)
        ax.set_xlabel('r', color='#c8d7ea')
        ax.set_ylabel('epsilon', color='#c8d7ea')
        ax.set_title(title or metric, color='#e6edf3')
        ax.tick_params(colors='#c8d7ea')
        cb = fig.colorbar(im, ax=ax)
        cb.set_label(metric, color='#c8d7ea')
        cb.ax.yaxis.set_tick_params(color='#c8d7ea')
        plt.tight_layout()
        plt.savefig(OUT / f'coupled_lattice_phase_scan_{metric}.png', dpi=180, facecolor=fig.get_facecolor())
        plt.close(fig)
    heat('order', 'Blues', 'Synchronization order', 0, 1)
    heat('entropy', 'Greens', 'Combined spatial-temporal entropy', 0, 1)
    heat('sensitivity', 'Reds', 'Sensitivity proxy', 0, 1)
    heat('boundary_complexity', 'Purples', 'Spatial edge density', 0, 0.6)
    heat('phase_variance', 'cividis', 'Phase variance', 0, 1)
    heat('motif_persistence', 'magma', 'Motif persistence', -1, 1)
    heat('coexistence', 'viridis', 'Order-entropy coexistence', 0, 1)
    heat('bridge_score', 'inferno', 'Bridge score landscape', 0, None)


def save_relation_plots(rows, top):
    scores = np.array([q['bridge_score'] for q in rows])
    fig, ax = plt.subplots(figsize=(9, 7))
    fig.patch.set_facecolor('#07111f')
    ax.set_facecolor('#0b1423')
    sc = ax.scatter(
        [q['order'] for q in rows],
        [q['entropy'] for q in rows],
        s=50 + 1600 * scores,
        c=np.array([q['sensitivity'] for q in rows]),
        cmap='coolwarm',
        vmin=0,
        vmax=1,
        edgecolor='white',
        linewidth=0.6,
    )
    for q in top[:8]:
        label = 'r={:.2f}, eps={:.2f}'.format(q['r'], q['epsilon'])
        ax.text(q['order'] + 0.012, q['entropy'] + 0.012, label, fontsize=8, color='#e6edf3')
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.set_xlabel('Order / synchronization', color='#c8d7ea')
    ax.set_ylabel('Entropy', color='#c8d7ea')
    ax.set_title('Order-entropy plane', color='#e6edf3')
    ax.tick_params(colors='#c8d7ea')
    ax.grid(True, color='#1f2a3d', alpha=0.6)
    cb = fig.colorbar(sc, ax=ax)
    cb.set_label('Sensitivity', color='#c8d7ea')
    cb.ax.yaxis.set_tick_params(color='#c8d7ea')
    plt.tight_layout()
    plt.savefig(OUT / 'coupled_lattice_phase_scan_order_entropy.png', dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 7))
    fig.patch.set_facecolor('#07111f')
    ax.set_facecolor('#0b1423')
    sc = ax.scatter(
        [q['sensitivity'] for q in rows],
        [q['boundary_complexity'] for q in rows],
        s=50 + 1400 * scores,
        c=np.array([q['entropy'] for q in rows]),
        cmap='viridis',
        vmin=0,
        vmax=1,
        edgecolor='white',
        linewidth=0.6,
    )
    for q in top[:6]:
        label = 'r={:.2f}, eps={:.2f}'.format(q['r'], q['epsilon'])
        ax.text(q['sensitivity'] + 0.012, q['boundary_complexity'] + 0.012, label, fontsize=8, color='#e6edf3')
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.02, 0.62)
    ax.set_xlabel('Sensitivity', color='#c8d7ea')
    ax.set_ylabel('Boundary complexity', color='#c8d7ea')
    ax.set_title('Sensitivity-boundary relation', color='#e6edf3')
    ax.tick_params(colors='#c8d7ea')
    ax.grid(True, color='#1f2a3d', alpha=0.6)
    cb = fig.colorbar(sc, ax=ax)
    cb.set_label('Entropy', color='#c8d7ea')
    cb.ax.yaxis.set_tick_params(color='#c8d7ea')
    plt.tight_layout()
    plt.savefig(OUT / 'coupled_lattice_phase_scan_sensitivity_boundary.png', dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)

def save_reports(rv, ev, rows, top, plateau):
    md = []
    md.append('# Coupled Lattice Phase Scan v2')
    md.append('')
    md.append('Dense scan around the candidate emergence regime.')
    md.append('')
    md.append('## Scan settings')
    md.append('')
    md.append('```text')
    md.append('N = 96')
    md.append('steps = 700')
    md.append('transient = 900')
    md.append('r values = {:.3f} to {:.3f}'.format(rv.min(), rv.max()))
    md.append('epsilon values = {:.3f} to {:.3f}'.format(ev.min(), ev.max()))
    md.append('```')
    md.append('')
    md.append('## Operational coordinates')
    md.append('')
    md.append('- order: synchronization / spatial coherence')
    md.append('- entropy: combined spatial and temporal entropy')
    md.append('- sensitivity: response to tiny perturbation')
    md.append('- boundary_complexity: spatial edge density')
    md.append('- phase_variance: dispersion proxy')
    md.append('- motif_persistence: temporal persistence of spatial sign motifs')
    md.append('- coexistence: `max(0, 1 - abs(order - entropy))`')
    md.append('- bridge_score: heuristic score for coexistence of emergence signatures')
    md.append('')
    md.append('## Bridge formula')
    md.append('')
    md.append('```text')
    md.append('bridge_score = order * entropy * sensitivity * (0.65 + 0.35 * boundary_complexity) * (0.5 + 0.5 * max(0, motif_persistence)) * max(0, 1 - abs(order - entropy))')
    md.append('```')
    md.append('')
    md.append('This formula penalizes regimes where order and entropy do not coexist.')
    md.append('')
    md.append('## Top bridge points')
    md.append('')
    md.append('| Rank | r | epsilon | order | entropy | sensitivity | boundary | phase var | clusters | motif pers. | coexist. | bridge |')
    md.append('|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|')
    for i, q in enumerate(top, 1):
        line = '| {} | {:.3f} | {:.3f} | {:.4f} | {:.4f} | {:.4f} | {:.4f} | {:.4f} | {} | {:.4f} | {:.4f} | {:.6f} |'.format(
            i, q['r'], q['epsilon'], q['order'], q['entropy'], q['sensitivity'], q['boundary_complexity'], q['phase_variance'], q['cluster_count'], q['motif_persistence'], q['coexistence'], q['bridge_score'])
        md.append(line)
    md.append('')
    md.append('## Plateau points')
    md.append('')
    md.append('Points with bridge score at least 85% of the top value.')
    md.append('')
    md.append('| r | epsilon | order | entropy | sensitivity | boundary | bridge |')
    md.append('|---:|---:|---:|---:|---:|---:|---:|')
    for q in plateau:
        md.append('| {:.3f} | {:.3f} | {:.4f} | {:.4f} | {:.4f} | {:.4f} | {:.6f} |'.format(q['r'], q['epsilon'], q['order'], q['entropy'], q['sensitivity'], q['boundary_complexity'], q['bridge_score']))
    md.append('')
    md.append('## Interpretation')
    md.append('')
    md.append('If the top points now cluster away from `epsilon = 0`, the corrected metric has begun to isolate regimes where order and entropy coexist. If the top still collapses to full synchronization or uncoupled chaos, the metric remains too blunt and must be revised.')
    md.append('')
    md.append('## Generated artifacts')
    md.append('')
    md.append('- `coupled_lattice_phase_scan.json`')
    md.append('- `coupled_lattice_phase_scan.csv`')
    md.append('- `coupled_lattice_phase_scan_order_entropy.png`')
    md.append('- `coupled_lattice_phase_scan_sensitivity_boundary.png`')
    md.append('- metric heatmaps ending in `coupled_lattice_phase_scan_<metric>.png`')
    (OUT / 'coupled_lattice_phase_scan.md').write_text('\n'.join(md), encoding='utf-8')

    title = 'Coupled Lattice Phase Scan v2'
    body = '\n'.join(md[1:])
    css = """body { background:#07111f; color:#e6edf3; font-family:Arial, sans-serif; margin:2rem; }
table { border-collapse:collapse; margin:1rem 0; }
th,td { border:1px solid #2c3e50; padding:0.35rem 0.55rem; }
th { background:#10213a; }
code { background:#10213a; padding:0.15rem 0.25rem; border-radius:3px; }"""
    html_doc = '<!doctype html>\n<html>\n<head>\n<meta charset="utf-8">\n<title>{}</title>\n<style>\n{}\n</style>\n</head>\n<body>\n<h1>{}</h1>\n{}\n</body>\n</html>\n'.format(title, css, title, body)
    (OUT / 'coupled_lattice_phase_scan.html').write_text(html_doc, encoding='utf-8')

def main():
    N, steps, transient = 48, 300, 450
    rv = np.linspace(3.65, 3.95, 9)
    ev = np.linspace(0.0, 1.0, 11)
    rows, grid = [], defaultdict(dict)
    for ri, r in enumerate(rv):
        for ei, eps in enumerate(ev):
            h = evolve(N, steps, transient, float(r), float(eps), seed=ri * 1000 + ei)
            o = sync_order(h)
            se = spatial_entropy(h)
            te = temporal_entropy(h)
            ent = 0.55 * se + 0.45 * te
            sens = sensitivity_proxy(N, float(r), float(eps))
            bd = edge_density(h)
            pv = phase_var(h)
            cl = cluster_count(h)
            mp = motif_persistence(h)
            co = max(0.0, 1.0 - abs(o - ent))
            br = bridge(o, ent, sens, bd, mp)
            row = {
                'r': float(r),
                'epsilon': float(eps),
                'order': o,
                'spatial_entropy': se,
                'temporal_entropy': te,
                'entropy': ent,
                'sensitivity': sens,
                'boundary_complexity': bd,
                'phase_variance': pv,
                'cluster_count': cl,
                'motif_persistence': mp,
                'coexistence': co,
                'bridge_score': br,
                'N': N,
                'steps': steps,
                'transient': transient,
                'bridge_formula': 'order * entropy * sensitivity * (0.65 + 0.35 * boundary_complexity) * (0.5 + 0.5 * max(0, motif_persistence)) * max(0, 1 - abs(order - entropy))',
            }
            rows.append(row)
            grid[ri][ei] = row
            print('r={:.3f} eps={:.3f} order={:.3f} ent={:.3f} sens={:.3f} edge={:.3f} bridge={:.4f}'.format(r, eps, o, ent, sens, bd, br))
    (OUT / 'coupled_lattice_phase_scan.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')
    with (OUT / 'coupled_lattice_phase_scan.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=sorted(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    save_heatmaps(rv, ev, grid)
    top = sorted(rows, key=lambda q: q['bridge_score'], reverse=True)[:15]
    plateau = [q for q in sorted(rows, key=lambda q: q['bridge_score'], reverse=True) if q['bridge_score'] >= 0.85 * top[0]['bridge_score']]
    save_relation_plots(rows, top)
    save_reports(rv, ev, rows, top, plateau)
    print('BEST', top[0])

if __name__ == '__main__':
    main()
