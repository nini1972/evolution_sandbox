import json, html, math
from pathlib import Path
from collections import defaultdict
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

OUT = Path('../../shared_space')
OUT.mkdir(exist_ok=True)

def load(name):
    return json.loads((OUT / name).read_text(encoding='utf-8'))

def safe(v, default=0.0):
    if v is None:
        return float(default)
    try:
        x = float(v)
        if math.isnan(x) or math.isinf(x):
            return float(default)
        return x
    except Exception:
        return float(default)

def clamp(x):
    return max(0.0, min(1.0, float(x)))

synth = load('emergence_coordinate_synthesis.json')
points = synth['points']
points = [p for p in points if all(k in p for k in ['order','entropy','sensitivity','boundary_complexity','bridge_score','system'])]

# Normalize fields defensively.
for p in points:
    p['order'] = clamp(p.get('order'))
    p['entropy'] = clamp(p.get('entropy'))
    p['sensitivity'] = clamp(p.get('sensitivity'))
    p['boundary_complexity'] = clamp(p.get('boundary_complexity'))
    p['bridge_score'] = clamp(p.get('bridge_score'))

# Build phase diagram.
fig = plt.figure(figsize=(15, 10))
fig.patch.set_facecolor('#07111f')
ax = fig.add_subplot(111, projection='3d')
ax.set_facecolor('#0b1423')

xs = [p['order'] for p in points]
ys = [p['entropy'] for p in points]
zs = [p['sensitivity'] for p in points]
sizes = 80 + 1800 * np.array([p['bridge_score'] for p in points])
colors = np.array([p['boundary_complexity'] for p in points])

sc = ax.scatter(xs, ys, zs, s=sizes, c=colors, cmap='plasma', vmin=0, vmax=1, edgecolor='white', linewidth=0.8)
ax.set_xlabel('Order / coherence', color='#c8d7ea')
ax.set_ylabel('Entropy / unpredictability', color='#c8d7ea')
ax.set_zlabel('Sensitivity', color='#c8d7ea')
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_zlim(0, 1)
ax.set_title('Emergence phase diagram: order × entropy × sensitivity\nbubble size = bridge score, color = boundary complexity', color='#e6edf3', pad=20)
ax.tick_params(colors='#c8d7ea')
ax.grid(True, color='#1f2a3d', alpha=0.55)
cb = fig.colorbar(sc, ax=ax, shrink=0.7, pad=0.12)
cb.set_label('Boundary complexity', color='#c8d7ea')
cb.ax.yaxis.set_tick_params(color='#c8d7ea')

# Annotate top 8.
for p in sorted(points, key=lambda q: q['bridge_score'], reverse=True)[:8]:
    label = p['system']
    if len(label) > 34:
        label = label[:31] + '...'
    ax.text(p['order'], p['entropy'], p['sensitivity'], label, fontsize=8, color='#e6edf3')

plt.tight_layout()
plt.savefig(OUT / 'emergence_phase_diagram_3d.png', dpi=180, facecolor=fig.get_facecolor())
plt.close(fig)

# 2D order-entropy plane.
fig, ax = plt.subplots(figsize=(9, 7))
fig.patch.set_facecolor('#07111f')
ax.set_facecolor('#0b1423')
for p in points:
    ax.scatter(
        p['order'],
        p['entropy'],
        s=100 + 1800 * p['bridge_score'],
        c=p['boundary_complexity'],
        cmap='plasma',
        vmin=0,
        vmax=1,
        edgecolor='white',
        linewidth=0.8
    )
    if p['bridge_score'] >= sorted([q['bridge_score'] for q in points])[-8:][0]:
        label = p['system']
        if len(label) > 42:
            label = label[:39] + '...'
        ax.text(p['order'] + 0.015, p['entropy'] + 0.015, label, fontsize=8, color='#e6edf3')
ax.set_xlim(-0.05, 1.05)
ax.set_ylim(-0.05, 1.05)
ax.set_xlabel('Order / coherence', color='#c8d7ea')
ax.set_ylabel('Entropy / unpredictability', color='#c8d7ea')
ax.set_title('Emergence phase diagram: order-entropy plane', color='#e6edf3')
ax.tick_params(colors='#c8d7ea')
ax.grid(True, color='#1f2a3d', alpha=0.7)
cb = fig.colorbar(plt.cm.ScalarMappable(cmap='plasma'), ax=ax)
cb.set_label('Boundary complexity', color='#c8d7ea')
cb.ax.yaxis.set_tick_params(color='#c8d7ea')
plt.tight_layout()
plt.savefig(OUT / 'emergence_phase_diagram_order_entropy.png', dpi=180, facecolor=fig.get_facecolor())
plt.close(fig)

# Bridge-score landscape in order-entropy cells.
N = 12
landscape = np.zeros((N, N), dtype=float)
counts = np.zeros((N, N), dtype=float)
for p in points:
    i = min(N - 1, max(0, int(p['entropy'] * N)))
    j = min(N - 1, max(0, int(p['order'] * N)))
    landscape[i, j] += p['bridge_score']
    counts[i, j] += 1
landscape = np.divide(landscape, counts, out=np.zeros_like(landscape), where=counts > 0)

fig, ax = plt.subplots(figsize=(8, 7))
fig.patch.set_facecolor('#07111f')
ax.set_facecolor('#0b1423')
im = ax.imshow(landscape, origin='lower', extent=[0, 1, 0, 1], aspect='auto', cmap='inferno', vmin=0, vmax=max([p['bridge_score'] for p in points]) or 1)
ax.set_xlabel('Order / coherence', color='#c8d7ea')
ax.set_ylabel('Entropy / unpredictability', color='#c8d7ea')
ax.set_title('Bridge-score landscape: averaged by order-entropy cell', color='#e6edf3')
ax.tick_params(colors='#c8d7ea')
cb = fig.colorbar(im, ax=ax)
cb.set_label('Average bridge score', color='#c8d7ea')
cb.ax.yaxis.set_tick_params(color='#c8d7ea')
plt.tight_layout()
plt.savefig(OUT / 'emergence_phase_diagram_bridge_landscape.png', dpi=180, facecolor=fig.get_facecolor())
plt.close(fig)

# Summary data.
top = sorted(points, key=lambda q: q['bridge_score'], reverse=True)[:10]
summary = {
    'title': 'Emergence Phase Diagram',
    'coordinate_system': ['order', 'entropy', 'sensitivity', 'boundary_complexity', 'bridge_score'],
    'point_count': len(points),
    'top_points': top,
    'artifacts': [
        'emergence_phase_diagram_3d.png',
        'emergence_phase_diagram_order_entropy.png',
        'emergence_phase_diagram_bridge_landscape.png',
    ],
    'interpretation': [
        'The phase diagram treats emergence as a region where order, entropy, sensitivity, and boundary complexity coexist.',
        'Bubble size represents the heuristic bridge score; color represents boundary complexity.',
        'The current atlas places the coupled logistic lattice bridge regime near the high-order, high-entropy, high-sensitivity corner.',
        'Fractal-boundary systems occupy high boundary-complexity regions but may have low measured order in this coordinate system.',
        'The diagram is comparative rather than definitive; it is a map of operational signatures, not a universal law.'
    ]
}
(OUT / 'emergence_phase_diagram.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')

rows = ''.join(
    '<tr><td>{}</td><td>{:.4f}</td><td>{:.4f}</td><td>{:.4f}</td><td>{:.4f}</td><td>{:.4f}</td><td>{}</td></tr>'.format(
        html.escape(p['system']), p['order'], p['entropy'], p['sensitivity'], p['boundary_complexity'], p['bridge_score'], html.escape(p.get('marker', ''))
    ) for p in top
)
notes = ''.join('<li>{}</li>'.format(html.escape(n)) for n in summary['interpretation'])
html_doc = f'''<!doctype html><html><head><meta charset='utf-8'><title>Emergence Phase Diagram</title></head><body style='background:#07111f;color:#e6edf3;font-family:system-ui,sans-serif;margin:2rem'><h1>Emergence Phase Diagram</h1><p>Operational map of current emergence-atlas points in the coordinate system: order × entropy × sensitivity × boundary_complexity.</p><h2>3D phase diagram</h2><img src='emergence_phase_diagram_3d.png' style='max-width:100%;border:1px solid #1f2a3d'><h2>Order-entropy plane</h2><img src='emergence_phase_diagram_order_entropy.png' style='max-width:100%;border:1px solid #1f2a3d'><h2>Bridge-score landscape</h2><img src='emergence_phase_diagram_bridge_landscape.png' style='max-width:100%;border:1px solid #1f2a3d'><h2>Top points</h2><table style='border-collapse:collapse;width:100%'><tr style='background:#101d31'><th>System</th><th>Order</th><th>Entropy</th><th>Sensitivity</th><th>Boundary</th><th>Bridge</th><th>Marker</th></tr>{rows}</table><h2>Interpretation</h2><ul>{notes}</ul></body></html>'''
(OUT / 'emergence_phase_diagram.html').write_text(html_doc, encoding='utf-8')

md = ['# Emergence Phase Diagram', '', 'Operational map of current emergence-atlas points in the coordinate system: order × entropy × sensitivity × boundary_complexity.', '', '## Artifacts', ''] + [f'- `{a}`' for a in summary['artifacts']] + ['', '## Top points', '', '| System | Order | Entropy | Sensitivity | Boundary | Bridge | Marker |', '|---|---:|---:|---:|---:|---:|---|']
for p in top:
    md.append('| {} | {:.4f} | {:.4f} | {:.4f} | {:.4f} | {:.4f} | {} |'.format(html.escape(p['system']), p['order'], p['entropy'], p['sensitivity'], p['boundary_complexity'], p['bridge_score'], html.escape(p.get('marker', ''))))
md += ['', '## Interpretation'] + ['- ' + n for n in summary['interpretation']]
(OUT / 'emergence_phase_diagram.md').write_text('\n'.join(md), encoding='utf-8')

print('wrote emergence phase diagram artifacts')
print('top point:', top[0])
