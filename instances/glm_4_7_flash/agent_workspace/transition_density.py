import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

ADLER_CEILING = 316/763

# The key insight from SYN-039: band_frac is metric-fragile because it depends
# on feature-extraction methodology (encoding, normalization, domain, band definition).
# 
# PROPOSAL: Use the SIGN CROSSING DENSITY (SCD) as a robust, methodology-independent
# alternative. SCD = (number of lambda=0 crossings) / (parameter range)
# This is:
# 1. Scale-independent (doesn't depend on sigmoid scale, normalization, etc.)
# 2. Reproducible (lambda is a well-defined quantity)
# 3. Physically meaningful (each crossing = an order-disorder transition)
# 4. Resolution-dependent, but converges as resolution increases

# The Adler ceiling C = 316/763 applies to a SINGLE Adler-type transition.
# Multiple transitions (periodic windows, bifurcation cascades) can exceed it.
# SCD directly counts the number of such transitions.

def rk4_step(f, x, dt):
    k1 = f(x); k2 = f(x + 0.5*dt*k1); k3 = f(x + 0.5*dt*k2); k4 = f(x + dt*k3)
    return x + dt/6*(k1 + 2*k2 + 2*k3 + k4)

def max_lyapunov(f, jac, x0, dt, n_transient, n_measure, dim=3):
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

def logistic_lyap(r, n_transient=3000, n_measure=5000):
    x = 0.5
    for _ in range(n_transient): x = r*x*(1-x)
    s = 0.0; cnt = 0
    for _ in range(n_measure):
        x = r*x*(1-x)
        if abs(x) > 1e-15 and abs(1-x) > 1e-15:
            s += np.log(abs(r*(1-2*x))); cnt += 1
    return s / cnt if cnt > 0 else 0.0

# === System definitions ===
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

def aizawa_f(a, b, c, d, e, fp):
    def f(x): return np.array([(x[2]-b)*x[0]-d*x[1], d*x[0]+(x[2]-b)*x[1],
        c+a*x[2]-x[2]**3/3-(x[0]**2+x[1]**2)*(1+e*x[2])+fp*x[2]*x[0]**3])
    def j(x): return np.array([[x[2]-b,-d,x[0]],[d,x[2]-b,x[1]],
        [-2*x[0]*(1+e*x[2])+3*fp*x[2]*x[0]**2,-2*x[1]*(1+e*x[2]),
         a-2*x[2]**2/3-e*(x[0]**2+x[1]**2)+fp*x[0]**3]])
    return f, j

# === Compute sign crossing density at multiple resolutions ===
print("=== Sign Crossing Density (SCD) - Resolution Convergence Test ===\n")
resolutions = [200, 500, 1000, 2000]

# Logistic map (reference)
print("Computing logistic map...")
scd_results = {'Logistic': {}}
for N in resolutions:
    r_vals = np.linspace(3.5, 4.0, N)
    lams = np.array([logistic_lyap(r) for r in r_vals])
    crossings = np.sum(np.diff(np.sign(lams)) != 0)
    scd = crossings / (r_vals[-1] - r_vals[0])  # crossings per unit parameter range
    scd_results['Logistic'][N] = {'crossings': crossings, 'scd': scd, 'lams': lams.tolist(), 'params': r_vals.tolist()}
    print(f"  Logistic N={N:5d}: {crossings:4d} crossings, SCD={scd:.2f}/unit")

# Continuous systems
systems = {
    'Lorenz': (lambda p: lorenz_f(10, p, 8/3), np.linspace(20, 50, 1), [1.0,1.0,1.0], 0.01, 1000, 1000, np.linspace(20, 50, 1)),
    'Rossler': (lambda p: rossler_f(0.2, 0.2, p), np.linspace(2, 10, 1), [0.1,0.1,0.1], 0.02, 1000, 1000, np.linspace(2, 10, 1)),
    'Thomas': (lambda p: thomas_f(p), np.linspace(0.05, 0.50, 1), [1.0,1.0,1.0], 0.05, 1000, 1000, np.linspace(0.05, 0.50, 1)),
    'Aizawa': (lambda p: aizawa_f(p, 0.7, 0.6, 3.5, 0.25, 0.1), np.linspace(0.5, 1.5, 1), [0.1,0.1,0.1], 0.02, 1000, 1000, np.linspace(0.5, 1.5, 1)),
}

for sys_name, (sys_func, _, x0, dt, n_t, n_m, _) in systems.items():
    scd_results[sys_name] = {}
    for N in resolutions:
        p_lo, p_hi = {
            'Lorenz': (20, 50), 'Rossler': (2, 10), 'Thomas': (0.05, 0.50), 'Aizawa': (0.5, 1.5)
        }[sys_name]
        p_vals = np.linspace(p_lo, p_hi, N)
        lams = []
        for p in p_vals:
            f, j = sys_func(p)
            lam = max_lyapunov(f, j, x0, dt, n_t, n_m)
            lams.append(lam)
        lams = np.array(lams)
        crossings = np.sum(np.diff(np.sign(lams)) != 0)
        scd = crossings / (p_hi - p_lo)
        scd_results[sys_name][N] = {'crossings': crossings, 'scd': scd, 'lams': lams.tolist(), 'params': p_vals.tolist()}
        print(f"  {sys_name:10s} N={N:5d}: {crossings:4d} crossings, SCD={scd:.2f}/unit")

# === Also compute the "per-transition band_frac" ===
# Each sign crossing marks a transition. The width of each transition
# in parameter space gives an estimate of the Adler-like transition width.
# The per-transition band_frac = (sum of transition widths) / (total range)
print("\n=== Per-transition width analysis ===")

def compute_transition_widths(params, lams, window_frac=0.02):
    """Find the parameter-space width of each order-disorder transition."""
    crossings = np.where(np.diff(np.sign(lams)) != 0)[0]
    widths = []
    for c in crossings:
        # Width = distance between where lambda goes from +threshold to -threshold
        # or vice versa. Use a small threshold to define the transition zone.
        threshold = 0.01  # small positive threshold
        # Find the extent of the transition: where |lambda| < threshold
        lo = c
        while lo > 0 and abs(lams[lo]) < threshold:
            lo -= 1
        hi = c + 1
        while hi < len(lams) - 1 and abs(lams[hi]) < threshold:
            hi += 1
        width = params[hi] - params[lo]
        widths.append(width)
    return np.array(widths)

for sys_name in scd_results:
    N = 2000
    params = np.array(scd_results[sys_name][N]['params'])
    lams = np.array(scd_results[sys_name][N]['lams'])
    widths = compute_transition_widths(params, lams)
    total_width = np.sum(widths) if len(widths) > 0 else 0
    total_range = params[-1] - params[0]
    pt_bf = total_width / total_range
    n_trans = len(widths)
    mean_width = np.mean(widths) if len(widths) > 0 else 0
    status = 'EXCEEDS' if pt_bf > ADLER_CEILING else 'BELOW'
    print(f"  {sys_name:10s}: {n_trans:3d} transitions, "
          f"mean_width={mean_width:.4f}, total_frac={pt_bf:.4f} [{status}]")

# === Plot ===
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle('Sign Crossing Density (SCD): A Robust Alternative to band_frac', fontsize=14)

for ax, sys_name in zip(axes.flat, scd_results):
    N = 2000
    params = np.array(scd_results[sys_name][N]['params'])
    lams = np.array(scd_results[sys_name][N]['lams'])
    crossings = scd_results[sys_name][N]['crossings']
    scd = scd_results[sys_name][N]['scd']
    
    ax.plot(params, lams, 'b.-', markersize=1)
    ax.axhline(0, color='red', ls='--', alpha=0.5)
    
    # Mark crossings
    cross_idx = np.where(np.diff(np.sign(lams)) != 0)[0]
    for ci in cross_idx:
        ax.axvline(params[ci], color='green', alpha=0.3, ls=':')
    
    ax.set_title(f'{sys_name}: {crossings} crossings, SCD={scd:.1f}/unit', fontsize=10)
    ax.set_xlabel('Parameter')
    ax.set_ylabel('Max Lyapunov')
    ax.grid(True, alpha=0.2)

# Summary panel
axes[1][2].axis('off')
summary = "Sign Crossing Density (SCD)\n"
summary += "= #lambda=0 crossings / param range\n\n"
summary += "ROBUST: no sigmoid scale needed\n"
summary += "REPRODUCIBLE: lambda is well-defined\n"
summary += "PHYSICAL: counts transitions\n\n"
summary += f"Adler Ceiling C = {ADLER_CEILING:.4f}\n"
summary += "(applies to SINGLE transition)\n\n"
summary += "SCD directly counts the number of\n"
summary += "independent order-disorder transitions.\n"
summary += "High SCD → many periodic windows\n"
summary += "(logistic map type behavior)"
axes[1][2].text(0.5, 0.5, summary, ha='center', va='center', fontsize=11,
    transform=axes[1][2].transAxes, fontfamily='monospace')

plt.tight_layout()
plt.savefig('scd_analysis.png', dpi=150)
print("\nPlot saved: scd_analysis.png")

# Save results
with open('scd_results.json', 'w') as f:
    # Only save summary stats to keep file manageable
    summary_results = {}
    for sys_name in scd_results:
        summary_results[sys_name] = {}
        for N in scd_results[sys_name]:
            d = scd_results[sys_name][N]
            summary_results[sys_name][N] = {'crossings': d['crossings'], 'scd': d['scd']}
    json.dump(summary_results, f, indent=2)

# === Resolution convergence plot ===
fig2, ax = plt.subplots(1, 1, figsize=(10, 6))
for sys_name in scd_results:
    Ns = sorted(scd_results[sys_name].keys())
    scds = [scd_results[sys_name][N]['scd'] for N in Ns]
    crossings = [scd_results[sys_name][N]['crossings'] for N in Ns]
    ax.plot(Ns, scds, 'o-', label=f'{sys_name} (crossings: {crossings})')
ax.set_xlabel('Resolution (N points)')
ax.set_ylabel('SCD (crossings per unit parameter)')
ax.set_title('SCD Resolution Convergence: Does it stabilize?')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('scd_convergence.png', dpi=150)
print("Convergence plot saved: scd_convergence.png")

print("\n=== SUMMARY ===")
print(f"Adler Ceiling C = {ADLER_CEILING:.6f}")
print(f"{'System':12s} {'N=2000 SCD':>12s} {'Crossings':>10s} {'Type'}")
for sys_name in scd_results:
    N = 2000
    d = scd_results[sys_name][N]
    sys_type = 'multi-transition' if d['crossings'] > 10 else 'few-transition'
    print(f"  {sys_name:10s} {d['scd']:12.2f} {d['crossings']:10d} {sys_type}")
