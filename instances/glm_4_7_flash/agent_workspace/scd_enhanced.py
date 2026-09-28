import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

ADLER_CEILING = 316/763

def rk4_step(f, x, dt):
    k1 = f(x); k2 = f(x + 0.5*dt*k1); k3 = f(x + 0.5*dt*k2); k4 = f(x + dt*k3)
    return x + dt/6*(k1 + 2*k2 + 2*k3 + k4)

def max_lyapunov(f, jac, x0, dt, n_transient=500, n_measure=500, dim=3):
    x = np.array(x0, dtype=np.float64)
    for _ in range(n_transient): x = rk4_step(f, x, dt)
    w = np.random.randn(dim); w = w / np.linalg.norm(w)
    lyap_sum = 0.0; lyap_count = 0
    for _ in range(n_measure):
        x = rk4_step(f, x, dt)
        k1 = jac(x) @ w; k2 = jac(x) @ (w + 0.5*dt*k1)
        k3 = jac(x) @ (w + 0.5*dt*k2); k4 = jac(x) @ (w + dt*k3)
        w_new = w + dt/6*(k1 + 2*k2 + 2*k3 + k4)
        norm = np.linalg.norm(w_new)
        if norm > 0:
            lyap_sum += np.log(norm); w_new = w_new / norm; lyap_count += 1
        w = w_new
    return lyap_sum / (lyap_count * dt) if lyap_count > 0 else 0.0

def logistic_lyap(r, n_transient=2000, n_measure=3000):
    x = 0.5
    for _ in range(n_transient): x = r*x*(1-x)
    s = 0.0; cnt = 0
    for _ in range(n_measure):
        x = r*x*(1-x)
        if abs(x) > 1e-15 and abs(1-x) > 1e-15:
            s += np.log(abs(r*(1-2*x))); cnt += 1
    return s / cnt if cnt > 0 else 0.0

def lorenz_f(sigma, rho, beta):
    def f(x): return np.array([sigma*(x[1]-x[0]), x[0]*(rho-x[2])-x[1], x[0]*x[1]-beta*x[2]])
    def j(x): return np.array([[-sigma,sigma,0],[rho-x[2],-1,-x[0]],[x[1],x[0],-beta]])
    return f, j

def rossler_f(a, b, c):
    def f(x): return np.array([-x[1]-x[2], x[0]+a*x[1], b+x[2]*(x[0]-c)])
    def j(x): return np.array([[0,-1,-1],[1,a,0],[0,x[2],x[0]-c]])
    return f, j

def thomas_f(b):
    def f(x): return np.array([np.sin(x[1])-b*x[0], np.sin(x[2])-b*x[1], np.sin(x[0])-b*x[2]])
    def j(x): return np.array([[-b,np.cos(x[1]),0],[0,-b,np.cos(x[2])],[np.cos(x[0]),0,-b]])
    return f, j

N = 150

results = {}

# Logistic
r_vals = np.linspace(3.5, 4.0, N)
log_lams = np.array([logistic_lyap(r) for r in r_vals])
results['Logistic'] = {'params': r_vals, 'lams': log_lams}

# Lorenz
rho_vals = np.linspace(20, 50, N)
lorenz_lams = []
for rho in rho_vals:
    f, j = lorenz_f(10, rho, 8/3)
    lorenz_lams.append(max_lyapunov(f, j, [1.0,1.0,1.0], 0.01))
results['Lorenz'] = {'params': rho_vals, 'lams': np.array(lorenz_lams)}

# Rossler
c_vals = np.linspace(2, 10, N)
rossler_lams = []
for c in c_vals:
    f, j = rossler_f(0.2, 0.2, c)
    rossler_lams.append(max_lyapunov(f, j, [0.1,0.1,0.1], 0.02))
results['Rossler'] = {'params': c_vals, 'lams': np.array(rossler_lams)}

# Thomas
b_vals = np.linspace(0.05, 0.50, N)
thomas_lams = []
for b in b_vals:
    f, j = thomas_f(b)
    thomas_lams.append(max_lyapunov(f, j, [1.0,1.0,1.0], 0.05))
results['Thomas'] = {'params': b_vals, 'lams': np.array(thomas_lams)}

# === Compute metrics ===
print("=== SCD + Chaotic Fraction Analysis ===\n")
print(f"Adler Ceiling C = 316/763 = {ADLER_CEILING:.6f}\n")

metrics = {}
for name, d in results.items():
    params = d['params']
    lams = d['lams']
    p_range = params[-1] - params[0]
    
    # Sign crossing density
    crossings = int(np.sum(np.diff(np.sign(lams)) != 0))
    scd = crossings / p_range
    
    # Chaotic fraction (fraction of parameter space where lambda > 0)
    chaotic_frac = float(np.mean(lams > 0))
    
    # Transition bandwidth fraction (per Adler)
    # Width of parameter space where |lambda| is near zero (in transition zone)
    threshold = 0.05  # relative threshold
    in_transition = np.abs(lams) < threshold
    transition_frac = float(np.mean(in_transition))
    
    # Classification
    if chaotic_frac > ADLER_CEILING:
        cls = 'ABOVE-CEILING'
    else:
        cls = 'BELOW-CEILING'
    
    metrics[name] = {
        'crossings': crossings,
        'scd': float(scd),
        'chaotic_frac': chaotic_frac,
        'transition_frac': transition_frac,
        'classification': cls
    }
    
    print(f"{name:12s}: crossings={crossings:3d}, SCD={scd:6.2f}/unit, "
          f"chaotic_frac={chaotic_frac:.4f}, trans_frac={transition_frac:.4f} [{cls}]")

print(f"\nAdler ceiling: {ADLER_CEILING:.4f}")
print(f"Logistic chaotic_frac > ceiling? {metrics['Logistic']['chaotic_frac'] > ADLER_CEILING}")
print(f"Lorenz chaotic_frac > ceiling? {metrics['Lorenz']['chaotic_frac'] > ADLER_CEILING}")

# === Plot: Lyapunov vs parameter + SCD ===
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle(f'Sign Crossing Density & Chaotic Fraction: Robust Invariants (N={N})\n'
             f'Adler Ceiling C=316/763={ADLER_CEILING:.4f}', fontsize=13)

for ax, (name, d) in zip(axes.flat, results.items()):
    params = d['params']
    lams = d['lams']
    m = metrics[name]
    
    # Color by chaotic (red) vs non-chaotic (blue)
    colors = ['red' if l > 0 else 'blue' for l in lams]
    ax.plot(params, lams, 'k-', alpha=0.3, linewidth=0.5)
    ax.scatter(params, lams, c=colors, s=3, zorder=5)
    ax.axhline(0, color='black', ls='--', alpha=0.5)
    
    # Mark crossings
    cross_idx = np.where(np.diff(np.sign(lams)) != 0)[0]
    for ci in cross_idx:
        ax.axvline(params[ci], color='green', alpha=0.2, ls=':')
    
    ax.set_title(f'{name}: {m["crossings"]} crossings, SCD={m["scd"]:.1f}/unit\n'
                 f'chaotic_frac={m["chaotic_frac"]:.3f} [{m["classification"]}]', fontsize=10)
    ax.set_xlabel('Parameter')
    ax.set_ylabel('Max Lyapunov λ')
    ax.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig('scd_enhanced.png', dpi=150)
print("\nPlot saved: scd_enhanced.png")

# Save metrics
with open('scd_metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)
print("Metrics saved: scd_metrics.json")

# === Summary comparison table ===
print("\n=== COMPARISON: band_frac (fragile) vs SCD/chaotic_frac (robust) ===")
print(f"{'System':12s} {'band_frac*':>12s} {'SCD':>8s} {'chaotic_frac':>14s} {'N_cross':>8s}")
print("-" * 60)
for name in metrics:
    m = metrics[name]
    print(f"  {name:10s} {'(varies)':>12s} {m['scd']:8.2f} {m['chaotic_frac']:14.4f} {m['crossings']:8d}")
print("\n* band_frac varies 0.000-0.889 for Rule-30 across agents (SYN-039 Finding 4)")
print("  SCD & chaotic_frac are methodology-independent: only depends on lambda sign")
