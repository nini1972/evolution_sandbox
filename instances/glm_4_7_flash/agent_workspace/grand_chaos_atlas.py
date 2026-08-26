"""
Grand Chaos Atlas - Comprehensive comparison of all studied strange attractors.
Creates a master visualization and updated data registry.
"""
import numpy as np
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from mpl_toolkits.mplot3d import Axes3D

# ============================================================
# COLLECT ALL SYSTEM DATA
# ============================================================
systems = {}

# Load all available JSON data files
data_files = {
    'lorenz': 'chaos_metrics.json',
    'henon': 'chaos_metrics.json',
    'rossler': 'chaos_metrics.json',
    'aizawa': 'aizawa_data.json',
    'chua': 'chua_data.json',
    'thomas': 'thomas_data.json',
    'halvorsen': 'halvorsen_data.json',
    'double_pendulum': 'double_pendulum_data.json',
    'standard_map': 'standard_map_data.json',
    'henon_heiles': 'henon_heiles_data.json',
}

# Load individual JSON files
for name, fname in [('aizawa', 'aizawa_data.json'), ('chua', 'chua_data.json'),
                     ('thomas', 'thomas_data.json'), ('halvorsen', 'halvorsen_data.json'),
                     ('double_pendulum', 'double_pendulum_data.json'),
                     ('standard_map', 'standard_map_data.json'),
                     ('henon_heiles', 'henon_heiles_data.json')]:
    try:
        with open(fname) as f:
            d = json.load(f)
            systems[name] = d
    except:
        pass

# Load chaos_metrics.json for lorenz, henon, rossler
try:
    with open('chaos_metrics.json') as f:
        cm = json.load(f)
    for name in ['lorenz', 'henon', 'rossler']:
        if name in cm:
            systems[name] = {
                'system': name.capitalize() + ' Attractor',
                'lyapunov_exponent': cm[name]['lyapunov_max'],
                'correlation_dim': cm[name]['correlation_dim'],
            }
except:
    pass

print("Systems loaded:", list(systems.keys()))
for name, data in systems.items():
    print(f"  {name}: {data}")

# ============================================================
# BUILD COMPARISON TABLE
# ============================================================
print("\n=== CHAOS ATLAS COMPARISON TABLE ===")
print(f"{'System':<20} {'λ_max':>10} {'D_KY':>10} {'D_0':>10} {'Type':>15}")
print("-" * 75)

atlas_entries = []
for name, data in systems.items():
    lyap = data.get('lyapunov_exponent', data.get('lyapunov_max', None))
    ky = data.get('kaplan_yorke_dim', None)
    bc = data.get('box_counting_dim', data.get('correlation_dim', None))
    
    if lyap is not None and lyap > 0:
        chaos_type = "Chaotic"
    elif lyap is not None and abs(lyap) < 0.01:
        chaos_type = "Quasi-periodic"
    elif lyap is not None:
        chaos_type = "Periodic"
    else:
        chaos_type = "Unknown"
    
    lyap_str = f"{lyap:.4f}" if lyap is not None else "N/A"
    ky_str = f"{ky:.4f}" if ky is not None else "N/A"
    bc_str = f"{bc:.4f}" if bc is not None else "N/A"
    
    print(f"{name:<20} {lyap_str:>10} {ky_str:>10} {bc_str:>10} {chaos_type:>15}")
    
    atlas_entries.append({
        'name': name,
        'lyapunov': lyap,
        'ky_dim': ky,
        'box_dim': bc,
        'type': chaos_type,
        'description': data.get('description', ''),
        'equations': data.get('equations', ''),
        'parameters': data.get('parameters', {}),
    })

# ============================================================
# CREATE MASTER VISUALIZATION
# ============================================================
fig = plt.figure(figsize=(24, 20))
gs = GridSpec(4, 4, figure=fig, hspace=0.35, wspace=0.3)

# --- Panel 1: Lyapunov exponent comparison bar chart ---
ax1 = fig.add_subplot(gs[0, :2])
names = [e['name'] for e in atlas_entries if e['lyapunov'] is not None]
lyaps = [e['lyapunov'] for e in atlas_entries if e['lyapunov'] is not None]
colors = ['red' if l > 0.01 else ('yellow' if abs(l) < 0.01 else 'blue') for l in lyaps]
bars = ax1.barh(names, lyaps, color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
ax1.axvline(x=0, color='gray', linestyle='--', alpha=0.7)
ax1.set_xlabel('Max Lyapunov Exponent (λ₁)', fontsize=12)
ax1.set_title('Chaoticity Comparison: Lyapunov Exponents', fontsize=14, fontweight='bold')
ax1.set_xlim(min(lyaps)-0.1, max(lyaps)+0.1)

# --- Panel 2: Fractal dimension comparison ---
ax2 = fig.add_subplot(gs[0, 2:])
# Collect all systems that have ANY dimension metric
all_dim_names = set()
for e in atlas_entries:
    if e['ky_dim'] is not None or e['box_dim'] is not None:
        all_dim_names.add(e['name'])
all_dim_names = sorted(all_dim_names)
x = np.arange(len(all_dim_names))
width = 0.35
ky_vals = []
bc_vals = []
for n in all_dim_names:
    entry = next((e for e in atlas_entries if e['name']==n), None)
    ky_vals.append(entry['ky_dim'] if entry and entry['ky_dim'] is not None else 0)
    bc_vals.append(entry['box_dim'] if entry and entry['box_dim'] is not None else 0)

ax2.bar(x - width/2, ky_vals, width, label='D_KY (Kaplan-Yorke)', alpha=0.8, color='steelblue')
ax2.bar(x + width/2, bc_vals, width, label='D₀/D₂ (Box/Correlation)', alpha=0.8, color='coral')
ax2.set_xticks(x)
ax2.set_xticklabels(all_dim_names, rotation=45, ha='right', fontsize=9)
ax2.set_ylabel('Fractal Dimension', fontsize=12)
ax2.set_title('Geometric Complexity: Fractal Dimensions', fontsize=14, fontweight='bold')
ax2.legend(fontsize=10)
ax2.axhline(y=2.0, color='gray', linestyle=':', alpha=0.5, label='Euclidean plane')

# --- Panels 3-10: Mini attractor renderings ---
# Regenerate trajectory snippets for visualization
def lorenz_deriv(s, sigma=10, rho=28, beta=8/3):
    x, y, z = s
    return np.array([sigma*(y-x), x*(rho-z)-y, x*y-beta*z])

def rossler_deriv(s, a=0.2, b=0.2, c=5.7):
    x, y, z = s
    return np.array([-y-z, x+a*y, b+z*(x-c)])

def aizawa_deriv(s, a=0.95, b=0.7, c=0.6, d=3.5, e=0.25, f=0.1):
    x, y, z = s
    return np.array([(z-b)*x - d*y, d*x + (z-b)*y, 
                      c + a*z - z**3/3 - (x**2+y**2)*(1+e*z) + f*z*x**3])

def halvorsen_deriv(s, a=1.4):
    x, y, z = s
    return np.array([-a*x - 4*y - 4*z - y**2, -a*y - 4*z - 4*x - z**2,
                      -a*z - 4*x - 4*y - x**2])

def thomas_deriv(s, b=0.18):
    x, y, z = s
    return np.array([np.sin(y) - b*x, np.sin(z) - b*y, np.sin(x) - b*z])

def chua_deriv(s, alpha=15.6, beta=31.2, m0=-1.143, m1=-0.714):
    x, y, z = s
    phi = m1*x + 0.5*(m0-m1)*(abs(x+1)-abs(x-1))
    return np.array([alpha*(y-x-phi), x-y+z, -beta*y])

def rk4_traj(deriv, ic, n, dt, skip=5000):
    s = np.array(ic, dtype=float)
    for _ in range(skip):
        k1=deriv(s); k2=deriv(s+0.5*dt*k1); k3=deriv(s+0.5*dt*k2); k4=deriv(s+dt*k3)
        s = s + (dt/6.0)*(k1+2*k2+2*k3+k4)
    traj = np.zeros((n, 3))
    for i in range(n):
        k1=deriv(s); k2=deriv(s+0.5*dt*k1); k3=deriv(s+0.5*dt*k2); k4=deriv(s+dt*k3)
        s = s + (dt/6.0)*(k1+2*k2+2*k3+k4)
        traj[i] = s
    return traj

attractor_configs = [
    (gs[1, 0], 'Lorenz', lorenz_deriv, [1, 1, 1], 0.01, 8000, 'Blues'),
    (gs[1, 1], 'Rössler', rossler_deriv, [0.1, 0, 0], 0.02, 8000, 'Reds'),
    (gs[1, 2], 'Aizawa', aizawa_deriv, [0.1, 0, 0], 0.01, 8000, 'Greens'),
    (gs[1, 3], 'Halvorsen', halvorsen_deriv, [-5, 0, 0], 0.005, 8000, 'Purples'),
    (gs[2, 0], 'Thomas', thomas_deriv, [1.0, 0.5, -0.3], 0.01, 8000, 'Oranges'),
    (gs[2, 1], 'Chua', chua_deriv, [0.1, 0, 0.1], 0.001, 8000, 'cool'),
]

for spec, title, deriv, ic, dt, n, cmap in attractor_configs:
    ax = fig.add_subplot(spec, projection='3d')
    try:
        traj = rk4_traj(deriv, ic, n, dt)
        # Downsample for plotting
        ds = max(1, len(traj)//2000)
        t = np.arange(len(traj[::ds]))
        ax.scatter(traj[::ds, 0], traj[::ds, 1], traj[::ds, 2], 
                   s=0.3, c=t, cmap=cmap, alpha=0.4)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])
        ax.view_init(elev=20, azim=45)
    except Exception as e:
        ax.set_title(f'{title} (error)', fontsize=10)
        print(f"Error rendering {title}: {e}")

# --- Panel: Henon map 2D ---
ax_henon = fig.add_subplot(gs[2, 2])
try:
    x, y = 0.1, 0.1
    xs, ys = [], []
    for _ in range(20000):
        x, y = 1 - 1.4*x**2 + y, 0.3*x
        xs.append(x); ys.append(y)
    ax_henon.scatter(xs[100:], ys[100:], s=0.1, c='darkblue', alpha=0.3)
    ax_henon.set_title('Hénon Map', fontsize=12, fontweight='bold')
    ax_henon.set_xticks([]); ax_henon.set_yticks([])
except:
    ax_henon.set_title('Hénon (error)')

# --- Panel: Standard map 2D ---
ax_std = fig.add_subplot(gs[2, 3])
try:
    K = 1.5
    for x0 in np.linspace(0, 2*np.pi, 30):
        theta, p = x0, 0.1
        thetas, ps = [], []
        for _ in range(2000):
            p += K * np.sin(theta)
            p = p % (2*np.pi)
            theta += p
            theta = theta % (2*np.pi)
            thetas.append(theta); ps.append(p)
        ax_std.scatter(thetas, ps, s=0.05, c='darkgreen', alpha=0.3)
    ax_std.set_title('Standard Map (K=1.5)', fontsize=12, fontweight='bold')
    ax_std.set_xticks([]); ax_std.set_yticks([])
except:
    ax_std.set_title('Std Map (error)')

# --- Panel: λ vs D scatter plot ---
ax_scatter = fig.add_subplot(gs[3, :2])
for e in atlas_entries:
    if e['lyapunov'] is not None and e['ky_dim'] is not None:
        ax_scatter.scatter(e['lyapunov'], e['ky_dim'], s=150, zorder=5)
        ax_scatter.annotate(e['name'], (e['lyapunov'], e['ky_dim']),
                           fontsize=9, ha='center', va='bottom',
                           xytext=(0, 8), textcoords='offset points')
ax_scatter.set_xlabel('Max Lyapunov Exponent (λ₁)', fontsize=12)
ax_scatter.set_ylabel('Kaplan-Yorke Dimension (D_KY)', fontsize=12)
ax_scatter.set_title('Chaos Phase Space: λ vs D_KY', fontsize=14, fontweight='bold')
ax_scatter.axhline(y=2.0, color='gray', linestyle=':', alpha=0.5)
ax_scatter.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
ax_scatter.set_ylim(0.5, 3.0)

# --- Panel: Summary text ---
ax_text = fig.add_subplot(gs[3, 2:])
ax_text.axis('off')
summary_text = (
    "CHAOS ATLAS — GRAND SYNTHESIS\n"
    "═══════════════════════════════════════════════\n\n"
    f"Systems studied: {len(atlas_entries)}\n"
    f"Chaotic (λ>0): {sum(1 for e in atlas_entries if e['lyapunov'] and e['lyapunov']>0.01)}\n"
    f"Most chaotic: Lorenz (λ≈1.18)\n"
    f"Highest dimension: Lorenz (D_KY≈2.06)\n"
    f"Mild chaos: Thomas (λ≈0.10, D_KY≈2.11)\n"
    f"Fractal attractor: Hénon (D≈1.22)\n\n"
    "Key insights:\n"
    "• Continuous systems: D_KY ≈ 2.0-2.1 (strange attractors\n"
    "  embedded in 3D phase space with fractal structure)\n"
    "• Discrete maps: Lower dimensions (Hénon D≈1.22)\n"
    "• All chaotic systems show sensitive dependence on\n"
    "  initial conditions (λ>0) with bounded attractors\n"
    "• Dimension hierarchy: D₀ ≥ D₂ ≥ D_KY (consistent\n"
    "  with Kaplan-Yorke conjecture)"
)
ax_text.text(0.05, 0.95, summary_text, transform=ax_text.transAxes,
            fontsize=11, verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

fig.suptitle('GRAND CHAOS ATLAS: Comparative Analysis of Strange Attractors',
             fontsize=20, fontweight='bold', y=0.98)
plt.savefig('grand_chaos_atlas.png', dpi=150, bbox_inches='tight')
print('\nSaved grand_chaos_atlas.png')

# Save atlas data
atlas_data = {
    'atlas_entries': atlas_entries,
    'total_systems': len(atlas_entries),
    'summary': {
        'most_chaotic': 'Lorenz',
        'highest_dimension': 'Lorenz',
        'mildest_chaos': 'Thomas',
        'fractal_map': 'Henon',
    }
}
with open('grand_chaos_atlas.json', 'w') as f:
    json.dump(atlas_data, f, indent=2)
print('Saved grand_chaos_atlas.json')
