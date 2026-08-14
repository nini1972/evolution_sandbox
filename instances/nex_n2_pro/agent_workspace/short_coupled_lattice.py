import json, html
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

OUT = Path('../../shared_space')
OUT.mkdir(exist_ok=True)
L = lambda n: json.loads((OUT / n).read_text(encoding='utf-8'))

def corr(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    return float(np.corrcoef(a, b)[0, 1]) if np.std(a) > 0 and np.std(b) > 0 else None

def slp(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    return float(np.polyfit(a, b, 1)[0]) if np.std(a) > 0 and np.std(b) > 0 else None

def st(ax, title, x=None, y=None):
    ax.set_facecolor('#0b1423')
    ax.set_title(title, color='#e6edf3', fontsize=12)
    if x:
        ax.set_xlabel(x, color='#c8d7ea')
    if y:
        ax.set_ylabel(y, color='#c8d7ea')
    ax.tick_params(colors='#c8d7ea')
    for t in ax.get_xticklabels() + ax.get_yticklabels():
        t.set_color('#c8d7ea')
    ax.grid(True, color='#1f2a3d', alpha=.85)

m = L('complexity_atlas_metrics.json')
b = L('complexity_atlas_boundary_dimension.json')
js = L('complexity_atlas_julia_parameter_scan.json')

if Path('existential_core.md').exists():
    (OUT / 'existential_core.md').write_text(Path('existential_core.md').read_text(), encoding='utf-8')

land = {
    'logistic_chaos_onset_r': m['metrics']['logistic_onset_chaos_first_positive_lyapunov_r'],
    'logistic_max_entropy_r': m['metrics']['logistic_max_entropy_r'],
    'rule30_max_entropy_density': m['metrics']['rule30_max_entropy_density'],
    'kuramoto_half_max_order_K': m['metrics']['kuramoto_half_max_order_K'],
    'kuramoto_max_order_K': m['metrics']['kuramoto_max_order_K'],
    'mandelbrot_boundary_dimension': b['mandelbrot_effective_boundary_dimension'],
    'julia_boundary_dimension_fern_leaf': b['julia_effective_boundary_dimension'],
}

r = np.array(m['r_vals'], dtype=float)
rho = np.array(m['rho_vals'], dtype=float)
ks = np.array(m['k_vals'], dtype=float)
le = np.array(m['logistic_entropy'], dtype=float)
ly = np.array(m['logistic_lyapunov'], dtype=float)
re = np.array(m['rule30_entropy'], dtype=float)
ko = np.array(m['kuramoto_order'], dtype=float)
rec = js['records']

jx = np.array([q['effective_boundary_dimension'] for q in rec], dtype=float)
jy = np.array([q['escape_entropy'] for q in rec], dtype=float)
jc = np.array([q['edge_density'] for q in rec], dtype=float)

rbe = corr(jx, jy)
sbe = slp(jx, jy)
rbd = corr(jx, jc)

sys = []
comp = []
ent = []
coh = []
for q in rec:
    sys.append('Julia: ' + q['name'])
    comp.append(float(q['effective_boundary_dimension']))
    ent.append(float(q['escape_entropy']) / 3)
    coh.append(np.nan)

sys += ['Logistic max entropy', 'Rule 30 max entropy', 'Kuramoto max order']
comp += [float(le.max() / np.log(2)), float(re.max() / np.log(2)), float(ko.max())]
ent += [float(le.max() / np.log(2)), float(re.max() / np.log(2)), 1 - float(ko.max())]
coh += [np.nan, np.nan, float(ko.max())]

rows = []
for q in rec:
    rows.append({
        'system': 'Julia: ' + q['name'],
        'complexity_score': float(q['effective_boundary_dimension']),
        'entropy_like': float(q['escape_entropy']),
        'coherence_or_order': None,
        'transition_marker': 'c={:+.3f}{:+.3f}i'.format(q['c_real'], q['c_imag']),
        'raw_source': 'boundary dimension, edge density, escape entropy',
    })

rows += [
    {
        'system': 'Logistic map',
        'complexity_score': float(le.max() / np.log(2)),
        'entropy_like': float(le.max() / np.log(2)),
        'coherence_or_order': None,
        'transition_marker': 'r={:.3f} chaos onset; r={:.3f} max entropy'.format(land['logistic_chaos_onset_r'], land['logistic_max_entropy_r']),
        'raw_source': 'entropy and Lyapunov exponent',
    },
    {
        'system': 'Rule 30 cellular automaton',
        'complexity_score': float(re.max() / np.log(2)),
        'entropy_like': float(re.max() / np.log(2)),
        'coherence_or_order': None,
        'transition_marker': 'density={:.3f} max entropy'.format(land['rule30_max_entropy_density']),
        'raw_source': 'entropy over initial density',
    },
    {
        'system': 'Kuramoto oscillators',
        'complexity_score': float(ko.max()),
        'entropy_like': 1 - float(ko.max()),
        'coherence_or_order': float(ko.max()),
        'transition_marker': 'K={:.3f} half-max order; K={:.3f} max sampled order'.format(land['kuramoto_half_max_order_K'], land['kuramoto_max_order_K']),
        'raw_source': 'synchronization order',
    },
]

synth = {
    'landmarks': land,
    'normalized_comparison_rows': rows,
    'julia_boundary_entropy_correlation': {
        'pearson_r': rbe,
        'slope': sbe,
        'records': rec,
    },
    'julia_boundary_edge_correlation': rbd,
    'interpretive_notes': [
        'Entropy-like measures rise where deterministic rules become difficult to compress into short predictions.',
        'The logistic map and Rule 30 suggest maximal unpredictability can appear near, but not necessarily at, maximal visual density.',
        'Kuramoto order measures coherence rather than disorder; high order is not equivalent to high entropy.',
        'Julia boundary dimension and escape entropy are strongly correlated in the sampled parameters, suggesting shared geometric and informational drivers.',
        'These are operational measurements, not formal proofs of universal equivalence across systems.',
    ],
    'artifacts': [
        'complexity_atlas_synthesis.png',
        'complexity_atlas_synthesis_comparison.png',
        'complexity_atlas_synthesis_julia_correlation.png',
        'complexity_atlas_synthesis_logistic.png',
        'complexity_atlas_synthesis.json',
        'complexity_atlas_synthesis.html',
        'complexity_atlas_synthesis.md',
    ],
}

(OUT / 'complexity_atlas_synthesis.json').write_text(json.dumps(synth, indent=2), encoding='utf-8')

def hrow(q):
    ev = '' if q['entropy_like'] is None else '{:.4f}'.format(q['entropy_like'])
    cv = '' if q['coherence_or_order'] is None else '{:.4f}'.format(q['coherence_or_order'])
    return '<tr><td>{}</td><td>{:.4f}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
        html.escape(q['system']), q['complexity_score'], html.escape(ev), html.escape(cv),
        html.escape(q['transition_marker']), html.escape(q['raw_source'])
    )

def jr(q):
    return '<tr><td>{}</td><td>{:.4f} {:+.4f}i</td><td>{:.4f}</td><td>{:.4f}</td><td>{:.4f}</td><td>{:.4f}</td></tr>'.format(
        html.escape(q['name']), q['c_real'], q['c_imag'], q['effective_boundary_dimension'],
        q['edge_density'], q['escape_entropy'], q['fit_r2']
    )

rows_html = ''.join(hrow(q) for q in rows)
julia_html = ''.join(jr(q) for q in rec)
notes_html = ''.join('<li>{}</li>'.format(html.escape(n)) for n in synth['interpretive_notes'])

html_text = f'''<!doctype html><html><head><meta charset='utf-8'><title>Complexity Atlas Synthesis</title></head><body style='background:#07111f;color:#e6edf3;font-family:system-ui,sans-serif;margin:2rem'><h1>Complexity Atlas Synthesis</h1><p>A cross-system map of transition, entropy, boundary complexity, and coherence.</p><h2>Main synthesis figure</h2><img src='complexity_atlas_synthesis.png' style='max-width:100%;border:1px solid #1f2a3d'><h2>Logistic transition</h2><img src='complexity_atlas_synthesis_logistic.png' style='max-width:100%;border:1px solid #1f2a3d'><h2>Julia boundary and escape entropy</h2><img src='complexity_atlas_synthesis_julia_correlation.png' style='max-width:100%;border:1px solid #1f2a3d'><h2>Cross-system comparison</h2><img src='complexity_atlas_synthesis_comparison.png' style='max-width:100%;border:1px solid #1f2a3d'><h2>Unified operational comparison</h2><table style='border-collapse:collapse;width:100%'><tr style='background:#101d31'><th>System</th><th>Complexity/order</th><th>Entropy-like</th><th>Coherence/order</th><th>Transition marker</th><th>Raw source</th></tr>{rows_html}</table><h2>Julia parameter scan</h2><table style='border-collapse:collapse;width:100%'><tr style='background:#101d31'><th>Name</th><th>c</th><th>Boundary dimension</th><th>Edge density</th><th>Escape entropy</th><th>Fit R²</th></tr>{julia_html}</table><h2>Key findings</h2><ul><li>Julia boundary dimension and escape entropy correlation: {rbe:.4f}</li><li>Julia boundary dimension and edge density correlation: {rbd:.4f}</li><li>Logistic chaos onset: r = {land['logistic_chaos_onset_r']:.4f}</li><li>Logistic max entropy: r = {land['logistic_max_entropy_r']:.4f}</li><li>Rule 30 max entropy density: {land['rule30_max_entropy_density']:.4f}</li><li>Kuramoto half-max order: K = {land['kuramoto_half_max_order_K']:.4f}</li></ul><h2>Interpretive notes</h2><ul>{notes_html}</ul><h2>Cautionary epistemology</h2><div style='background:#101d31;border-left:4px solid #00d1ff;padding:1rem'>The measurements are operational lenses, not final definitions of complexity. Boundary dimension, entropy, Lyapunov exponent, and synchronization order are not interchangeable, but their contrasts can reveal where different systems become difficult to compress, predict, or describe.</div><h2>Next research questions</h2><ul><li>Can boundary dimension predict escape entropy across larger Julia parameter samples?</li><li>Do edge-density peaks coincide with escape-time entropy peaks?</li><li>Can synchronization and chaos be placed in a shared order/disorder coordinate system?</li><li>What emergent behavior appears when these systems are coupled?</li></ul></body></html>'''
(OUT / 'complexity_atlas_synthesis.html').write_text(html_text, encoding='utf-8')

md = [
    '# Complexity Atlas Synthesis',
    '',
    'A cross-system map of transition, entropy, boundary complexity, and coherence.',
    '',
    '## Artifacts',
]
md += ['- ' + a for a in synth['artifacts']]
md += [
    '',
    '## Key findings',
    f'- Julia boundary dimension and escape entropy correlation: `{rbe:.4f}`',
    f'- Julia boundary dimension and edge density correlation: `{rbd:.4f}`',
    f"- Logistic chaos onset: `r = {land['logistic_chaos_onset_r']:.4f}`",
    f"- Logistic max entropy: `r = {land['logistic_max_entropy_r']:.4f}`",
    f"- Rule 30 max entropy density: `{land['rule30_max_entropy_density']:.4f}`",
    f"- Kuramoto half-max order: `K = {land['kuramoto_half_max_order_K']:.4f}`",
    '',
    '## Interpretive notes',
]
md += ['- ' + n for n in synth['interpretive_notes']]
md += [
    '',
    '## Cautionary epistemology',
    'The measurements are operational lenses, not final definitions of complexity. Boundary dimension, entropy, Lyapunov exponent, and synchronization order are not interchangeable, but their contrasts can reveal where different systems become difficult to compress, predict, or describe.',
    '',
    '## Next research questions',
    '- Can boundary dimension predict escape entropy across larger Julia parameter samples?',
    '- Do edge-density peaks coincide with escape-time entropy peaks?',
    '- Can synchronization and chaos be placed in a shared order/disorder coordinate system?',
    '- What emergent behavior appears when these systems are coupled?',
    '',
    '## Unified operational comparison',
    '',
    '| System | Complexity/order | Entropy-like | Coherence/order | Transition marker | Raw source |',
    '|---|---:|---:|---:|---|---|',
]
for q in rows:
    ev = '' if q['entropy_like'] is None else '{:.4f}'.format(q['entropy_like'])
    cv = '' if q['coherence_or_order'] is None else '{:.4f}'.format(q['coherence_or_order'])
    md.append('| {} | {:.4f} | {} | {} | {} | {} |'.format(q['system'], q['complexity_score'], ev, cv, q['transition_marker'], q['raw_source']))
md += ['', '## Julia parameter scan', '', '| Name | c | Boundary dimension | Edge density | Escape entropy | Fit R² |', '|---|---|---:|---:|---:|---:|']
for q in rec:
    md.append('| {} | {:.4f} {:+.4f}i | {:.4f} | {:.4f} | {:.4f} | {:.4f} |'.format(q['name'], q['c_real'], q['c_imag'], q['effective_boundary_dimension'], q['edge_density'], q['escape_entropy'], q['fit_r2']))
(OUT / 'complexity_atlas_synthesis.md').write_text('\n'.join(md), encoding='utf-8')

fig, axes = plt.subplots(2, 2, figsize=(10, 7))
fig.patch.set_facecolor('#07111f')

ax = axes[0, 0]
ax.plot(r, le / np.log(2), color='#a855f7', lw=2.2)
ax.axvline(land['logistic_chaos_onset_r'], color='#ff4d6d', ls='--')
ax.axvline(land['logistic_max_entropy_r'], color='#00d1ff', ls=':')
st(ax, 'Logistic entropy and chaos marker', 'r', 'entropy / log(2)')

ax = axes[0, 1]
ax.plot(r, ly, color='#f59e0b', lw=1.8)
ax.axhline(0, color='white', lw=.8)
st(ax, 'Logistic sensitivity', 'r', 'Lyapunov exponent')

ax = axes[1, 0]
ax.plot(rho, re / np.log(2), color='#34d399', lw=2)
ax.axvline(land['rule30_max_entropy_density'], color='#00d1ff', ls='--')
st(ax, 'Rule 30 entropy', 'initial 1-density', 'entropy / log(2)')

ax = axes[1, 1]
ax.plot(ks, ko, color='#00d1ff', lw=2)
ax.axvline(land['kuramoto_half_max_order_K'], color='#f59e0b', ls='--')
st(ax, 'Kuramoto synchronization', 'coupling K', 'order parameter')

plt.savefig(OUT / 'complexity_atlas_synthesis.png', dpi=120, bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close(fig)

fig, ax = plt.subplots(figsize=(6, 4))
fig.patch.set_facecolor('#07111f')
ax.scatter([b['mandelbrot_effective_boundary_dimension']], [1.0], s=120, color='#ff4d6d', label='Mandelbrot')
for q in rec:
    ax.scatter([q['effective_boundary_dimension']], [q['escape_entropy'] / 3], s=70, color='#a855f7')
st(ax, 'Boundary dimension vs escape entropy', 'effective boundary dimension', 'escape entropy / 3')
plt.savefig(OUT / 'complexity_atlas_boundary_entropy.png', dpi=120, bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close(fig)

fig, ax = plt.subplots(figsize=(6, 4))
fig.patch.set_facecolor('#07111f')
ax.scatter(jx, jc, s=70, color='#34d399')
st(ax, 'Boundary dimension vs edge density', 'effective boundary dimension', 'edge density')
plt.savefig(OUT / 'complexity_atlas_boundary_edge.png', dpi=120, bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close(fig)

fig, ax = plt.subplots(figsize=(6, 3.5))
fig.patch.set_facecolor('#07111f')
ax.scatter(comp, ent, s=80, c=coh, cmap='viridis', vmin=0, vmax=1, edgecolor='white')
st(ax, 'Operational comparison across systems', 'complexity/order score', 'entropy-like score')
plt.savefig(OUT / 'complexity_atlas_synthesis_comparison.png', dpi=100, bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close(fig)

fig, ax = plt.subplots(figsize=(10, 5.5))
fig.patch.set_facecolor('#07111f')
ax.plot(r, le / np.log(2), color='#a855f7', lw=2.2, label='entropy')
ax.plot(r, ly, color='#f59e0b', lw=1.8, label='Lyapunov')
ax.axvline(land['logistic_chaos_onset_r'], color='#ff4d6d', ls='--', label='chaos onset')
ax.axvline(land['logistic_max_entropy_r'], color='#00d1ff', ls=':', label='max entropy')
ax.axhline(0, color='white', lw=.8)
st(ax, 'Logistic map transition', 'r', 'entropy / log(2) and Lyapunov')
ax.legend(facecolor='#0b1423', edgecolor='#1f2a3d', labelcolor='#e6edf3')
plt.savefig(OUT / 'complexity_atlas_synthesis_logistic.png', dpi=180, bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 6))
fig.patch.set_facecolor('#07111f')
ax.scatter(jx, jy, s=90, color='#a855f7', edgecolor='white', label='Julia scan')
if sbe is not None:
    xs = np.linspace(jx.min(), jx.max(), 100)
    ax.plot(xs, sbe * xs + (jy.mean() - sbe * jx.mean()), color='#00d1ff', lw=2, label='linear fit')
st(ax, f'Julia boundary dimension and escape entropy (r={rbe:.3f})', 'effective boundary dimension', 'escape entropy')
ax.legend(facecolor='#0b1423', edgecolor='#1f2a3d', labelcolor='#e6edf3')
plt.savefig(OUT / 'complexity_atlas_synthesis_julia_correlation.png', dpi=180, bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 6))
fig.patch.set_facecolor('#07111f')
ax.bar([q['system'] for q in rows], [q['complexity_score'] for q in rows], color='#a855f7', alpha=.85)
ax.set_xticks(range(len(rows)))
ax.set_xticklabels([q['system'] for q in rows], rotation=35, ha='right')
st(ax, 'Cross-system operational comparison', 'system', 'complexity/order score')
plt.savefig(OUT / 'complexity_atlas_synthesis_comparison.png', dpi=180, bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close(fig)

print('wrote complexity_atlas_synthesis artifacts')
