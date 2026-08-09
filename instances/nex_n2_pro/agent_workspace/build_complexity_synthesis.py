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
