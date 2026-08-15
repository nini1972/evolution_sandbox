import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path('../../shared_space')
OUT.mkdir(exist_ok=True)
L = 32
T = 100
C = 80
R = np.array([3.55, 3.6, 3.7, 3.8, 3.9, 3.99], dtype=float)
E = np.array([0.0, 0.02, 0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0], dtype=float)
B = np.linspace(0.0, 1.0, 17)


def step(x, r, e):
    y = r * x * (1.0 - x)
    n = np.roll(y, 1, 0) + np.roll(y, -1, 0) + np.roll(y, 1, 1) + np.roll(y, -1, 1)
    return np.clip((1.0 - e) * y + 0.25 * e * n, 0.0, 1.0)


def ent(x):
    h, _ = np.histogram(x.ravel(), bins=B)
    p = h / h.sum()
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum() / np.log2(len(B) - 1))


def edges(x):
    b = (x > 0.5).astype(int)
    return float(((b[:-1] != b[1:]).sum() + (b[:, :-1] != b[:, 1:]).sum()) / (2 * L * (L - 1)))


def order(x):
    return float(abs(np.mean(np.exp(2j * np.pi * x))))


def hblock(s, k):
    c = {}
    for i in range(len(s) - k + 1):
        key = tuple(int(v) for v in s[i:i + k])
        c[key] = c.get(key, 0) + 1
    p = np.array(list(c.values()), dtype=float)
    p /= p.sum()
    return float(-(p * np.log2(p)).sum())


def run(r, e, seed):
    rng = np.random.default_rng(seed)
    x = rng.random((L, L))
    y = np.clip(x + 1e-10, 1e-12, 1.0 - 1e-12)
    os = np.empty(C, dtype=float)
    es = np.empty(C, dtype=float)
    eds = np.empty(C, dtype=float)
    bits = np.empty(C, dtype=int)
    for t in range(T + C):
        x = step(x, r, e)
        y = step(y, r, e)
        if t >= T:
            i = t - T
            os[i] = order(x)
            es[i] = ent(x)
            eds[i] = edges(x)
            bits[i] = int(x[L // 2, L // 2] > 0.5)
    dist = float(np.sqrt(np.mean((x - y) ** 2)))
    return {
        'r': float(r), 'epsilon': float(e),
        'mean_synchronization_order': float(os.mean()),
        'final_synchronization_order': float(os[-1]),
        'mean_spatial_entropy_norm': float(es.mean()),
        'final_spatial_entropy_norm': float(ent(x)),
        'mean_edge_density': float(eds.mean()),
        'final_edge_density': float(eds[-1]),
        'temporal_entropy_rate_bits': float(max(0.0, hblock(bits, 4) - hblock(bits, 3))),
        'final_log10_distance': float(np.log10(max(dist, 1e-300))),
    }


def mat(records, key):
    a = np.empty((len(R), len(E)), dtype=float)
    for i, r in enumerate(R):
        for j, e in enumerate(E):
            vals = [q.get(key, 0.0) for q in records if q['r'] == r and q['epsilon'] == e]
            a[i, j] = vals[0] if vals else 0.0
    return a


def heat(path, data, title, cmap, vmin=None, vmax=None):
    fig, ax = plt.subplots(figsize=(8, 5.2))
    fig.patch.set_facecolor('#07111f')
    ax.set_facecolor('#0b1423')
    im = ax.imshow(data, origin='lower', aspect='auto', cmap=cmap, vmin=vmin, vmax=vmax)
    ax.set_title(title, color='#e6edf3')
    ax.set_xlabel('epsilon', color='#c8d7ea')
    ax.set_ylabel('r', color='#c8d7ea')
    ax.set_xticks(np.arange(len(E)))
    ax.set_xticklabels([f'{e:.2f}' for e in E], color='#c8d7ea')
    ax.set_yticks(np.arange(len(R)))
    ax.set_yticklabels([f'{r:.2f}' for r in R], color='#c8d7ea')
    ax.tick_params(colors='#c8d7ea')
    cb = fig.colorbar(im, ax=ax)
    cb.ax.yaxis.set_tick_params(color='#c8d7ea')
    plt.tight_layout()
    plt.savefig(path, dpi=140, facecolor=fig.get_facecolor())
    plt.close(fig)


def corr(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if np.std(a) == 0 or np.std(b) == 0:
        return None
    return float(np.corrcoef(a, b)[0, 1])


records = []
for i, r in enumerate(R):
    for j, e in enumerate(E):
        rec = run(r, e, i * 100 + j)
        records.append(rec)
        print(f"r={r:.2f} eps={e:.2f} order={rec['mean_synchronization_order']:.3f} entropy={rec['mean_spatial_entropy_norm']:.3f} distance={rec['final_log10_distance']:.2f}")

max_abs_log_distance = max(abs(q['final_log10_distance']) for q in records) or 1e-300
for rec in records:
    sensitivity = 1.0 - abs(rec['final_log10_distance']) / max_abs_log_distance
    bridge = rec['mean_synchronization_order'] * rec['mean_spatial_entropy_norm'] * max(0.0, sensitivity)
    rec['sensitivity_score'] = float(max(0.0, min(1.0, sensitivity)))
    rec['bridge_score'] = float(max(0.0, min(1.0, bridge)))

order_m = mat(records, 'mean_synchronization_order')
entropy_m = mat(records, 'mean_spatial_entropy_norm')
edge_m = mat(records, 'mean_edge_density')
rate_m = mat(records, 'temporal_entropy_rate_bits')
sens_m = mat(records, 'sensitivity_score')
bridge_m = mat(records, 'bridge_score')
best = max(records, key=lambda q: q['bridge_score'])

summary = {
    'parameters': {'lattice_size': L, 'transient_steps': T, 'collect_steps': C, 'r_values': R.tolist(), 'epsilon_values': E.tolist(), 'bins': int(len(B) - 1)},
    'records': records,
    'landmarks': {
        'max_synchronization': float(order_m.max()), 'min_synchronization': float(order_m.min()),
        'max_spatial_entropy_norm': float(entropy_m.max()), 'min_spatial_entropy_norm': float(entropy_m.min()),
        'max_edge_density': float(edge_m.max()), 'min_edge_density': float(edge_m.min()),
        'max_temporal_entropy_rate_bits': float(rate_m.max()), 'min_temporal_entropy_rate_bits': float(rate_m.min()),
        'max_sensitivity_score': float(sens_m.max()), 'min_sensitivity_score': float(sens_m.min()),
        'best_bridge_score': float(best['bridge_score']), 'best_bridge_parameters': {'r': best['r'], 'epsilon': best['epsilon']},
    },
    'correlations': {
        'order_vs_entropy': corr(order_m.ravel(), entropy_m.ravel()),
        'order_vs_edge_density': corr(order_m.ravel(), edge_m.ravel()),
        'entropy_vs_edge_density': corr(entropy_m.ravel(), edge_m.ravel()),
        'sensitivity_vs_entropy': corr(sens_m.ravel(), entropy_m.ravel()),
        'bridge_vs_entropy': corr(bridge_m.ravel(), entropy_m.ravel()),
    },
    'interpretive_notes': [
        'Coupling tends to increase synchronization order, but can also reorganize spatial entropy depending on the local logistic parameter.',
        'High synchronization order is not equivalent to low complexity; synchronized lattices may retain structured gradients.',
        'The final perturbation distance is an operational sensitivity proxy, not a formal Lyapunov exponent.',
        'One-site entropy-rate estimates are coarse and exploratory.',
        'Coupling strength is treated as a bridge between local chaos and collective coherence.',
    ],
}

Path(OUT / 'coupled_lattice_exploration.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')

rows = []
for q in records:
    rows.append('| {:.2f} | {:.2f} | {:.4f} | {:.4f} | {:.4f} | {:.4f} | {:.4f} | {:.4f} |'.format(q['r'], q['epsilon'], q['mean_synchronization_order'], q['mean_spatial_entropy_norm'], q['mean_edge_density'], q['temporal_entropy_rate_bits'], q['final_log10_distance'], q['bridge_score']))

land = summary['landmarks']
md = ['# Coupled Logistic Lattice Exploration', '', 'A small atlas of local chaos under spatial coupling.', '', '## Parameters', f'- Lattice size: `{L} x {L}`', f'- Transient steps: `{T}`', f'- Collection steps: `{C}`', f'- Logistic r values: `{R.tolist()}`', f'- Coupling epsilon values: `{E.tolist()}`', '', '## Landmarks', f"- Max synchronization order: `{land['max_synchronization']:.4f}`", f"- Min synchronization order: `{land['min_synchronization']:.4f}`", f"- Max spatial entropy norm: `{land['max_spatial_entropy_norm']:.4f}`", f"- Min spatial entropy norm: `{land['min_spatial_entropy_norm']:.4f}`", f"- Max edge density: `{land['max_edge_density']:.4f}`", f"- Max temporal entropy-rate proxy: `{land['max_temporal_entropy_rate_bits']:.4f}`", f"- Max sensitivity score: `{land['max_sensitivity_score']:.4f}`", f"- Best bridge score: `{land['best_bridge_score']:.4f}` at r={land['best_bridge_parameters']['r']:.2f}, epsilon={land['best_bridge_parameters']['epsilon']:.2f}", '', '## Correlations']
for k, v in summary['correlations'].items():
    md.append(f'- {k}: `{None if v is None else v:.4f}`')
md += ['', '## Interpretive notes'] + ['- ' + n for n in summary['interpretive_notes']]
md += ['', '## Unified table', '', '| r | epsilon | mean order | mean entropy | mean edge density | entropy-rate proxy | log10 final distance | bridge score |', '|---:|---:|---:|---:|---:|---:|---:|---:|'] + rows
Path(OUT / 'coupled_lattice_exploration.md').write_text('\n'.join(md), encoding='utf-8')

html_rows = ''.join('<tr><td>{:.2f}</td><td>{:.2f}</td><td>{:.4f}</td><td>{:.4f}</td><td>{:.4f}</td><td>{:.4f}</td><td>{:.4f}</td><td>{:.4f}</td></tr>'.format(q['r'], q['epsilon'], q['mean_synchronization_order'], q['mean_spatial_entropy_norm'], q['mean_edge_density'], q['temporal_entropy_rate_bits'], q['final_log10_distance'], q['bridge_score']) for q in records)
notes = ''.join('<li>{}</li>'.format(q) for q in summary['interpretive_notes'])
html = f'''<!doctype html><html><head><meta charset='utf-8'><title>Coupled Logistic Lattice Exploration</title></head><body style='background:#07111f;color:#e6edf3;font-family:system-ui,sans-serif;margin:2rem'><h1>Coupled Logistic Lattice Exploration</h1><p>A small atlas of local chaos under spatial coupling.</p><h2>Heatmaps</h2><img src='coupled_lattice_order.png' style='max-width:100%;border:1px solid #1f2a3d'><img src='coupled_lattice_entropy.png' style='max-width:100%;border:1px solid #1f2a3d'><img src='coupled_lattice_edges.png' style='max-width:100%;border:1px solid #1f2a3d'><img src='coupled_lattice_sensitivity.png' style='max-width:100%;border:1px solid #1f2a3d'><img src='coupled_lattice_bridge.png' style='max-width:100%;border:1px solid #1f2a3d'><h2>Order-entropy relation</h2><img src='coupled_lattice_order_entropy_relation.png' style='max-width:100%;border:1px solid #1f2a3d'><h2>Unified table</h2><table style='border-collapse:collapse;width:100%'><tr style='background:#101d31'><th>r</th><th>epsilon</th><th>mean order</th><th>mean entropy</th><th>mean edge density</th><th>entropy-rate proxy</th><th>log10 final distance</th><th>bridge score</th></tr>{html_rows}</table><h2>Interpretive notes</h2><ul>{notes}</ul><h2>Cautionary epistemology</h2><div style='background:#101d31;border-left:4px solid #00d1ff;padding:1rem'>This experiment is an atlas entry, not a proof. Sensitivity, entropy-rate, and bridge scores are operational lenses for comparing regimes of local chaos and collective coherence.</div></body></html>'''
Path(OUT / 'coupled_lattice_exploration.html').write_text(html, encoding='utf-8')

heat(OUT / 'coupled_lattice_order.png', order_m, 'Mean synchronization order', 'magma')
heat(OUT / 'coupled_lattice_entropy.png', entropy_m, 'Mean spatial entropy norm', 'viridis', 0.0, 1.0)
heat(OUT / 'coupled_lattice_edges.png', edge_m, 'Mean edge density', 'plasma', 0.0, 1.0)
heat(OUT / 'coupled_lattice_sensitivity.png', sens_m, 'Sensitivity score from final perturbation distance', 'cividis', 0.0, 1.0)
heat(OUT / 'coupled_lattice_bridge.png', bridge_m, 'Bridge score: order x entropy x sensitivity', 'inferno', 0.0, 1.0)

fig, ax = plt.subplots(figsize=(7.5, 5.2))
fig.patch.set_facecolor('#07111f')
ax.set_facecolor('#0b1423')
ax.scatter(order_m.ravel(), entropy_m.ravel(), s=70, c=bridge_m.ravel(), cmap='inferno', vmin=0, vmax=1, edgecolor='white')
ax.set_xlabel('mean synchronization order', color='#c8d7ea')
ax.set_ylabel('mean spatial entropy norm', color='#c8d7ea')
ax.set_title('Order-entropy relation colored by bridge score', color='#e6edf3')
ax.tick_params(colors='#c8d7ea')
ax.grid(True, color='#1f2a3d', alpha=.8)
plt.tight_layout()
plt.savefig(OUT / 'coupled_lattice_order_entropy_relation.png', dpi=160, facecolor=fig.get_facecolor())
plt.close(fig)

print('wrote coupled_lattice_exploration artifacts')
print('best bridge', best)
