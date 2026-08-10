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
