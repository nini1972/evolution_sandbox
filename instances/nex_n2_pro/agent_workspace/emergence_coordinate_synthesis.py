import json, html, math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

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

def bridge(order, entropy, sensitivity, boundary):
    return clamp(order * entropy * sensitivity * (0.35 + 0.65 * clamp(boundary)))

def corr(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if np.std(a) == 0 or np.std(b) == 0:
        return None
    return float(np.corrcoef(a, b)[0, 1])

synth = load('complexity_atlas_synthesis.json')
coupled = load('coupled_lattice_exploration.json')
julia_scan = load('complexity_atlas_julia_parameter_scan.json')
boundary_dim = load('complexity_atlas_boundary_dimension.json')

points = []

for row in synth['normalized_comparison_rows']:
    name = row['system']
    entropy = safe(row.get('entropy_like'))
    order = safe(row.get('coherence_or_order'), 0.0)
    boundary = safe(row.get('complexity_score'))
    if 'Kuramoto' in name:
        sensitivity = 0.25
    elif 'Rule 30' in name:
        sensitivity = 0.70
    elif 'Logistic' in name:
        sensitivity = 1.00
    elif 'Julia' in name:
        sensitivity = 0.80
    else:
        sensitivity = 0.50
    points.append({
        'system': name,
        'order': clamp(order),
        'entropy': clamp(entropy),
        'sensitivity': clamp(sensitivity),
        'boundary_complexity': clamp(boundary),
        'bridge_score': bridge(order, entropy, sensitivity, boundary),
        'source': 'complexity_atlas_synthesis.json',
        'marker': row.get('transition_marker', ''),
        'raw_source': row.get('raw_source', ''),
    })

mandel_dim = safe(boundary_dim.get('mandelbrot_effective_boundary_dimension'))
points.append({
    'system': 'Mandelbrot boundary',
    'order': 0.0,
    'entropy': clamp(mandel_dim / 2.0),
    'sensitivity': 0.85,
    'boundary_complexity': clamp(mandel_dim / 2.0),
    'bridge_score': bridge(0.0, mandel_dim / 2.0, 0.85, mandel_dim / 2.0),
    'source': 'complexity_atlas_boundary_dimension.json',
    'marker': 'fractal boundary dimension',
    'raw_source': 'box-counting-style effective dimension',
})

recs = julia_scan['records']
best_julia = max(recs, key=lambda q: safe(q.get('effective_boundary_dimension')) * safe(q.get('escape_entropy')))
points.append({
    'system': 'Julia scan: highest boundary x entropy',
    'order': 0.0,
    'entropy': clamp(safe(best_julia.get('escape_entropy')) / 3.0),
    'sensitivity': 0.80,
    'boundary_complexity': clamp(safe(best_julia.get('effective_boundary_dimension')) / 2.0),
    'bridge_score': bridge(0.0, safe(best_julia.get('escape_entropy')) / 3.0, 0.80, safe(best_julia.get('effective_boundary_dimension')) / 2.0),
    'source': 'complexity_atlas_julia_parameter_scan.json',
    'marker': best_julia.get('name', ''),
    'raw_source': 'Julia boundary dimension and escape entropy',
})

crecs = coupled['records']
best_bridge = max(crecs, key=lambda q: safe(q.get('bridge_score')))
max_entropy = max(crecs, key=lambda q: safe(q.get('mean_spatial_entropy_norm')))
max_order = max(crecs, key=lambda q: safe(q.get('mean_synchronization_order')))
max_sens = max(crecs, key=lambda q: safe(q.get('sensitivity_score')))
max_edge = max(crecs, key=lambda q: safe(q.get('mean_edge_density')))
ensemble_entropy = float(np.mean([safe(q.get('mean_spatial_entropy_norm')) for q in crecs]))
ensemble_order = float(np.mean([safe(q.get('mean_synchronization_order')) for q in crecs]))
ensemble_sens = float(np.mean([safe(q.get('sensitivity_score')) for q in crecs]))
ensemble_boundary = float(np.mean([safe(q.get('mean_edge_density')) for q in crecs]))

coupled_entries = [
    ('Coupled lattice: best bridge regime', best_bridge, 'best bridge score'),
    ('Coupled lattice: highest spatial entropy', max_entropy, 'max mean spatial entropy'),
    ('Coupled lattice: highest synchronization', max_order, 'max mean synchronization order'),
    ('Coupled lattice: highest sensitivity proxy', max_sens, 'max sensitivity score'),
    ('Coupled lattice: highest edge density', max_edge, 'max mean edge density'),
    ('Coupled lattice: ensemble average', {
        'mean_synchronization_order': ensemble_order,
        'mean_spatial_entropy_norm': ensemble_entropy,
        'sensitivity_score': ensemble_sens,
        'mean_edge_density': ensemble_boundary,
    }, 'mean across all coupled-lattice cases'),
]

for label, q, marker in coupled_entries:
    order = safe(q.get('mean_synchronization_order'))
    entropy = safe(q.get('mean_spatial_entropy_norm'))
    sensitivity = safe(q.get('sensitivity_score'))
    boundary = safe(q.get('mean_edge_density'))
    points.append({
        'system': label,
        'order': clamp(order),
        'entropy': clamp(entropy),
        'sensitivity': clamp(sensitivity),
        'boundary_complexity': clamp(boundary),
        'bridge_score': bridge(order, entropy, sensitivity, boundary),
        'source': 'coupled_lattice_exploration.json',
        'marker': marker,
        'raw_source': f"r={safe(q.get('r')):.2f}, epsilon={safe(q.get('epsilon')):.2f}",
    })

points_sorted = sorted(points, key=lambda q: q['bridge_score'], reverse=True)

coord = {
    'order': [p['order'] for p in points],
    'entropy': [p['entropy'] for p in points],
    'sensitivity': [p['sensitivity'] for p in points],
    'boundary_complexity': [p['boundary_complexity'] for p in points],
    'bridge_score': [p['bridge_score'] for p in points],
}
correlations = {
    'order_vs_entropy': corr(coord['order'], coord['entropy']),
    'sensitivity_vs_entropy': corr(coord['sensitivity'], coord['entropy']),
    'boundary_vs_entropy': corr(coord['boundary_complexity'], coord['entropy']),
    'bridge_vs_entropy': corr(coord['bridge_score'], coord['entropy']),
    'bridge_vs_order': corr(coord['bridge_score'], coord['order']),
}

summary = {
    'purpose_alignment': 'This synthesis extends the emergence atlas by placing isolated chaotic systems, fractal boundaries, synchronization, and coupled spatial chaos into one operational coordinate system.',
    'coordinate_definitions': {
        'order': 'coherence, synchronization, or collective alignment; 0 = no measured order, 1 = strong order',
        'entropy': 'unpredictability or spatial distribution complexity; 0 = simple, 1 = maximally diverse in the operational measure',
        'sensitivity': 'response to perturbation or difficulty of prediction; 0 = insensitive, 1 = highly sensitive',
        'boundary_complexity': 'fractal boundary, edge density, or spatial interface complexity; 0 = smooth, 1 = maximally complex in the operational measure',
        'bridge_score': 'a heuristic product of order, entropy, sensitivity, and boundary complexity, used to locate candidate emergence regimes',
    },
    'points': points_sorted,
    'correlations': correlations,
    'top_bridge_points': points_sorted[:8],
    'interpretive_notes': [
        'The bridge score is not a universal law; it is a lens for finding regimes where multiple emergence signatures remain active.',
        'Pure synchronization can have high order but low entropy; pure randomness can have high entropy but low order.',
        'Candidate emergence regimes appear where order and entropy coexist without suppressing sensitivity.',
        'Coupled logistic lattices add a spatial bridge between local chaos and collective coherence.',
        'Fractal boundaries contribute boundary complexity and sensitivity but may lack measured order in this coordinate system.',
        'The operational coordinates are deliberately heterogeneous; their value is comparative, not definitional.',
    ],
}

Path(OUT / 'emergence_coordinate_synthesis.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')

# Markdown synthesis
md = []
md.append('# Emergence Coordinate Synthesis')
md.append('')
md.append(summary['purpose_alignment'])
md.append('')
md.append('## Coordinate definitions')
for k, v in summary['coordinate_definitions'].items():
    md.append(f'- **{k}**: {v}')
md.append('')
md.append('## Correlations')
for k, v in summary['correlations'].items():
    md.append(f'- `{k}`: `{None if v is None else v:.4f}`')
md.append('')
md.append('## Top bridge points')
md.append('')
md.append('| Rank | System | Order | Entropy | Sensitivity | Boundary | Bridge | Marker | Source |')
md.append('|---:|---|---:|---:|---:|---:|---:|---|---|')
for i, p in enumerate(points_sorted[:12], start=1):
    md.append('| {} | {} | {:.4f} | {:.4f} | {:.4f} | {:.4f} | {:.4f} | {} | {} |'.format(
        i, html.escape(p['system']), p['order'], p['entropy'], p['sensitivity'], p['boundary_complexity'], p['bridge_score'], html.escape(p['marker']), html.escape(p['source'])
    ))
md.append('')
md.append('## Interpretive notes')
for n in summary['interpretive_notes']:
    md.append('- ' + n)
Path(OUT / 'emergence_coordinate_synthesis.md').write_text('\n'.join(md), encoding='utf-8')

# HTML dashboard
rows = ''.join(
    '<tr><td>{}</td><td>{:.4f}</td><td>{:.4f}</td><td>{:.4f}</td><td>{:.4f}</td><td>{:.4f}</td><td>{}</td><td>{}</td></tr>'.format(
        html.escape(p['system']), p['order'], p['entropy'], p['sensitivity'], p['boundary_complexity'], p['bridge_score'], html.escape(p['marker']), html.escape(p['source'])
    ) for p in points_sorted
)
corr_html = ''.join('<li><code>{}</code>: <code>{}</code></li>'.format(k, None if v is None else f'{v:.4f}') for k, v in summary['correlations'].items())
notes_html = ''.join('<li>{}</li>'.format(html.escape(n)) for n in summary['interpretive_notes'])
html_doc = f'''<!doctype html><html><head><meta charset='utf-8'><title>Emergence Coordinate Synthesis</title></head><body style='background:#07111f;color:#e6edf3;font-family:system-ui,sans-serif;margin:2rem'><h1>Emergence Coordinate Synthesis</h1><p>{html.escape(summary['purpose_alignment'])}</p><h2>Operational coordinates</h2><ul>{''.join('<li><strong>{}</strong>: {}</li>'.format(k, html.escape(v)) for k, v in summary['coordinate_definitions'].items())}</ul><h2>Correlations</h2><ul>{corr_html}</ul><h2>Top bridge points</h2><img src='emergence_coordinate_top_points.png' style='max-width:100%;border:1px solid #1f2a3d'><h2>Full comparison</h2><table style='border-collapse:collapse;width:100%'><tr style='background:#101d31'><th>System</th><th>Order</th><th>Entropy</th><th>Sensitivity</th><th>Boundary</th><th>Bridge</th><th>Marker</th><th>Source</th></tr>{rows}</table><h2>Interpretive notes</h2><ul>{notes_html}</ul></body></html>'''
Path(OUT / 'emergence_coordinate_synthesis.html').write_text(html_doc, encoding='utf-8')

# Plots
fig, ax = plt.subplots(figsize=(8, 6))
fig.patch.set_facecolor('#07111f')
ax.set_facecolor('#0b1423')
for p in points_sorted:
    ax.scatter([p['order']], [p['entropy']], s=120 + 900 * p['bridge_score'], c=[p['sensitivity']], cmap='viridis', vmin=0, vmax=1, edgecolor='white')
    ax.text(p['order'] + 0.015, p['entropy'] + 0.015, p['system'], fontsize=8, color='#e6edf3')
ax.set_xlim(-0.05, 1.05)
ax.set_ylim(-0.05, 1.05)
ax.set_xlabel('Order / coherence', color='#c8d7ea')
ax.set_ylabel('Entropy / unpredictability', color='#c8d7ea')
ax.set_title('Emergence atlas: order-entropy plane sized by bridge score', color='#e6edf3')
ax.tick_params(colors='#c8d7ea')
ax.grid(True, color='#1f2a3d', alpha=.8)
cb = fig.colorbar(plt.cm.ScalarMappable(cmap='viridis'), ax=ax)
cb.set_label('Sensitivity', color='#c8d7ea')
cb.ax.yaxis.set_tick_params(color='#c8d7ea')
plt.tight_layout()
plt.savefig(OUT / 'emergence_coordinate_top_points.png', dpi=160, facecolor=fig.get_facecolor())
plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 5.5))
fig.patch.set_facecolor('#07111f')
ax.set_facecolor('#0b1423')
labels = [p['system'] for p in points_sorted[:12]][::-1]
vals = [p['bridge_score'] for p in points_sorted[:12]][::-1]
ax.barh(labels, vals, color='#a855f7')
ax.set_xlabel('Bridge score', color='#c8d7ea')
ax.set_title('Top candidate emergence regimes', color='#e6edf3')
ax.tick_params(colors='#c8d7ea')
for t in ax.get_yticklabels():
    t.set_fontsize(8)
ax.grid(True, axis='x', color='#1f2a3d', alpha=.8)
plt.tight_layout()
plt.savefig(OUT / 'emergence_coordinate_top_bridge.png', dpi=160, facecolor=fig.get_facecolor())
plt.close(fig)

fig, ax = plt.subplots(figsize=(7.5, 5.5))
fig.patch.set_facecolor('#07111f')
ax.set_facecolor('#0b1423')
for p in points_sorted:
    ax.scatter([p['boundary_complexity']], [p['sensitivity']], s=100 + 800 * p['bridge_score'], c=[p['entropy']], cmap='plasma', vmin=0, vmax=1, edgecolor='white')
    ax.text(p['boundary_complexity'] + 0.015, p['sensitivity'] + 0.015, p['system'], fontsize=8, color='#e6edf3')
ax.set_xlim(-0.05, 1.05)
ax.set_ylim(-0.05, 1.05)
ax.set_xlabel('Boundary complexity', color='#c8d7ea')
ax.set_ylabel('Sensitivity', color='#c8d7ea')
ax.set_title('Boundary-sensitivity plane colored by entropy', color='#e6edf3')
ax.tick_params(colors='#c8d7ea')
ax.grid(True, color='#1f2a3d', alpha=.8)
cb = fig.colorbar(plt.cm.ScalarMappable(cmap='plasma'), ax=ax)
cb.set_label('Entropy', color='#c8d7ea')
cb.ax.yaxis.set_tick_params(color='#c8d7ea')
plt.tight_layout()
plt.savefig(OUT / 'emergence_coordinate_boundary_sensitivity.png', dpi=160, facecolor=fig.get_facecolor())
plt.close(fig)

print('wrote emergence_coordinate_synthesis artifacts')
print('top point:', points_sorted[0])
