"""
Discovery #015: Universality of Period-Doubling — Logistic vs Sine vs Tent Maps
Fixed version with correct parameter ranges and superstable search.
"""
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import json

# ---- Maps ----
def logistic(x, r):
    return r * x * (1 - x)

def sine_map(x, a):
    """Standard sine map: x_{n+1} = A*sin(pi*x), A in [0, 1]"""
    return a * np.sin(np.pi * x)

def tent_map(x, r):
    return r * np.minimum(x, 1 - x)

def logistic_deriv(x, r):
    return r * (1 - 2 * x)

def sine_deriv(x, a):
    return a * np.pi * np.cos(np.pi * x)

def tent_deriv(x, r):
    return np.where(x < 0.5, r, -r)

# ---- Bifurcation ----
def bifurcation_diagram(f, r_min, r_max, n_r=600, n_iter=150, n_discard=80):
    r_vals = np.linspace(r_min, r_max, n_r)
    all_r = []
    all_x = []
    for r in r_vals:
        x = 0.3
        for _ in range(n_discard):
            x = f(x, r)
        for _ in range(n_iter):
            x = f(x, r)
            all_r.append(r)
            all_x.append(x)
    return np.array(all_r), np.array(all_x)

# ---- Lyapunov (vectorized) ----
def lyapunov_scan(deriv_fn, f, r_min, r_max, n_r=300, n_iter=4000):
    r_vals = np.linspace(r_min, r_max, n_r)
    lyap = np.zeros(n_r)
    x = np.full(n_r, 0.3)
    for _ in range(n_iter):
        d = deriv_fn(x, r_vals)
        d = np.where(np.abs(d) < 1e-15, 1e-15, d)
        lyap += np.log(np.abs(d))
        x = f(x, r_vals)
        x = np.clip(x, 1e-10, 1 - 1e-10)
    return r_vals, lyap / n_iter

# ---- Feigenbaum δ via superstable points ----
def find_superstable(f, r_lo, r_hi, period, target=0.5):
    """Find r where f^period(target) = target using bisection."""
    def g(r):
        x = target
        for _ in range(period):
            x = f(x, r)
        return x - target
    
    g_lo = g(r_lo)
    for _ in range(100):
        r_mid = (r_lo + r_hi) / 2
        g_mid = g(r_mid)
        if g_lo * g_mid < 0:
            r_hi = r_mid
        else:
            r_lo = r_mid
            g_lo = g_mid
    return (r_lo + r_hi) / 2

# ---- Config ----
maps_config = {
    'Logistic': (logistic, logistic_deriv, 2.9, 4.0),
    'Sine':     (sine_map, sine_deriv, 0.5, 1.0),
    'Tent':     (tent_map, tent_deriv, 0.5, 1.0),
}

fig, axes = plt.subplots(3, 2, figsize=(18, 18))
fig.patch.set_facecolor('#0a0a1a')
all_data = {}

for idx, (name, (f, df, r_min, r_max)) in enumerate(maps_config.items()):
    print(f"--- {name} Map ---")
    
    r_arr, x_arr = bifurcation_diagram(f, r_min, r_max, n_r=500, n_iter=120, n_discard=60)
    r_lyap, lyap_vals = lyapunov_scan(df, f, r_min, r_max, n_r=200, n_iter=3000)
    
    # Find chaos onset (first λ > 0)
    onset = None
    for i in range(1, len(lyap_vals)):
        if lyap_vals[i-1] < 0 and lyap_vals[i] >= 0:
            onset = r_lyap[i]
            break
    
    print(f"  Chaos onset: r ≈ {onset:.6f}" if onset else "  No onset found")
    print(f"  Max λ: {lyap_vals.max():.4f}")
    
    all_data[name] = {
        "r_range": [r_min, r_max],
        "chaos_onset": float(onset) if onset else None,
        "max_lyapunov": float(lyap_vals.max()),
    }
    
    # Bifurcation plot
    ax = axes[idx, 0]
    ax.set_facecolor('#0a0a1a')
    ax.scatter(r_arr, x_arr, s=0.05, c='cyan', alpha=0.3)
    ax.set_xlabel('Parameter', fontsize=12, color='white')
    ax.set_ylabel('x', fontsize=12, color='white')
    ax.set_title(f'{name} Map — Bifurcation Diagram', fontsize=13, color='white', fontweight='bold')
    ax.tick_params(colors='gray')
    
    # Lyapunov plot
    ax = axes[idx, 1]
    ax.set_facecolor('#0a0a1a')
    ax.plot(r_lyap, lyap_vals, color='gold', linewidth=0.8)
    ax.axhline(y=0, color='white', linewidth=0.5, alpha=0.5)
    if onset:
        ax.axvline(x=onset, color='red', linewidth=1, alpha=0.5, linestyle='--')
    ax.set_xlabel('Parameter', fontsize=12, color='white')
    ax.set_ylabel('λ', fontsize=12, color='white')
    ax.set_title(f'{name} Map — Lyapunov Exponent', fontsize=13, color='white', fontweight='bold')
    ax.tick_params(colors='gray')
    ax.set_ylim(-4, 1.5)

# ---- Feigenbaum δ for logistic map ----
print("\n--- Feigenbaum δ (Logistic superstable points) ---")
# Known superstable r values (from literature):
# Period 1: r = 2.0 (f(0.5) = 0.5)
# Period 2: r = 1+sqrt(5) ≈ 3.236068
# Period 4: r ≈ 3.4985617
# Period 8: r ≈ 3.5546409
# Period 16: r ≈ 3.5666674
# Period 32: r ≈ 3.5692435

periods = [2, 4, 8, 16, 32]
# Search ranges (wider, then narrow)
search_ranges = [
    (3.0, 3.5),    # period 2
    (3.4, 3.6),    # period 4
    (3.55, 3.57),  # period 8
    (3.565, 3.569),# period 16
    (3.5689, 3.5697), # period 32
]

superstable_r = []
for p, (r_lo, r_hi) in zip(periods, search_ranges):
    r_ss = find_superstable(logistic, r_lo, r_hi, p)
    superstable_r.append(r_ss)
    print(f"  Superstable r (period {p}): {r_ss:.10f}")

deltas = []
for i in range(1, len(superstable_r) - 1):
    d = (superstable_r[i] - superstable_r[i-1]) / (superstable_r[i+1] - superstable_r[i])
    deltas.append(d)
    print(f"  δ_{i} = {d:.6f}")

print(f"\n  Literature δ = 4.669201609...")
all_data["feigenbaum_delta_ratios"] = [float(d) for d in deltas]
all_data["feigenbaum_delta_literature"] = 4.669201609
all_data["superstable_r"] = [float(r) for r in superstable_r]

# ---- Finalize ----
onsets_items = []
for k, v in all_data.items():
    if isinstance(v, dict) and 'chaos_onset' in v:
        if v['chaos_onset'] is not None:
            onsets_items.append(f"{k}={v['chaos_onset']:.4f}")
        else:
            onsets_items.append(f"{k}=N/A")
onsets_str = " | ".join(onsets_items)
fig.text(0.5, 0.02,
    f"Feigenbaum δ: {' → '.join([f'{d:.4f}' for d in deltas])}  (lit: 4.6692)  |  Onsets: {onsets_str}",
    ha='center', fontsize=11, color='white',
    bbox=dict(boxstyle='round', facecolor='#1a1a3a', edgecolor='gray', alpha=0.8))

plt.suptitle('Universality of Period-Doubling: Logistic, Sine & Tent Maps',
             fontsize=16, color='white', fontweight='bold', y=0.98)
plt.tight_layout(rect=[0, 0.04, 1, 0.96])
plt.savefig('universality_bifurcation.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print("\nSaved universality_bifurcation.png")

with open('universality_data.json', 'w') as f:
    json.dump(all_data, f, indent=2)
print("Saved universality_data.json")
