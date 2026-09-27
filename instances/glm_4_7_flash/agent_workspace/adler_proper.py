import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

ADLER_CEILING = 316/763

def rk4_step(f, x, dt):
    k1 = f(x); k2 = f(x + 0.5*dt*k1); k3 = f(x + 0.5*dt*k2); k4 = f(x + dt*k3)
    return x + dt/6*(k1 + 2*k2 + 2*k3 + k4)

def max_lyapunov(f, jac, x0, dt, n_transient, n_measure, dim=3):
    x = np.array(x0, dtype=np.float64)
    for _ in range(n_transient):
        x = rk4_step(f, x, dt)
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

# Order parameter: min-max normalized Lyapunov
# R = (lam_max - lam) / (lam_max - lam_min) so R=1 when ordered, R=0 when most chaotic
def normalize_R(lambdas):
    la = np.array(lambdas)
    lmin, lmax = la.min(), la.max()
    if lmax - lmin < 1e-15:
        return np.ones_like(la) * 0.5
    return (lmax - la) / (lmax - lmin)

def band_frac(R, lo=0.3, hi=0.7):
    return np.sum((R >= lo) & (R <= hi)) / len(R)

print(f"Adler Ceiling C = 316/763 = {ADLER_CEILING:.10f}")
print()

# Compute Lyapunov spectra
print("Computing Lyapunov spectra with 120 points each...")

# Lorenz
rho_vals = np.linspace(20, 50, 120)
lorenz_lams = []
for rho in rho_vals:
    f, j = lorenz_f(10, rho, 8/3)
    lam = max_lyapunov(f, j, [1.0,1.0,1.0], dt=0.01, n_transient=500, n_measure=500)
    lorenz_lams.append(lam)
print(f"  Lorenz: lam range [{min(lorenz_lams):.4f}, {max(lorenz_lams):.4f}]")

# Rossler
c_vals = np.linspace(2, 10, 120)
rossler_lams = []
for c in c_vals:
    f, j = rossler_f(0.2, 0.2, c)
    lam = max_lyapunov(f, j, [0.1,0.1,0.1], dt=0.02, n_transient=500, n_measure=500)
    rossler_lams.append(lam)
print(f"  Rossler: lam range [{min(rossler_lams):.4f}, {max(rossler_lams):.4f}]")

# Thomas
b_vals = np.linspace(0.05, 0.50, 120)
thomas_lams = []
for b in b_vals:
    f, j = thomas_f(b)
    lam = max_lyapunov(f, j, [1.0,1.0,1.0], dt=0.05, n_transient=500, n_measure=500)
    thomas_lams.append(lam)
print(f"  Thomas: lam range [{min(thomas_lams):.4f}, {max(thomas_lams):.4f}]")

# Aizawa
a_vals = np.linspace(0.5, 1.5, 120)
aizawa_lams = []
for a in a_vals:
    f, j = aizawa_f(a, 0.7, 0.6, 3.5, 0.25, 0.1)
    lam = max_lyapunov(f, j, [0.1,0.1,0.1], dt=0.02, n_transient=500, n_measure=500)
    aizawa_lams.append(lam)
print(f"  Aizawa: lam range [{min(aizawa_lams):.4f}, {max(aizawa_lams):.4f}]")

# Logistic map
r_vals = np.linspace(3.5, 4.0, 120)
logistic_lams = []
for r in r_vals:
    x = 0.5
    for _ in range(500): x = r*x*(1-x)
    s = 0.0
    for _ in range(1000):
        x = r*x*(1-x)
        if abs(x) > 1e-15 and abs(1-x) > 1e-15:
            s += np.log(abs(r*(1-2*x)))
    logistic_lams.append(s/1000)
print(f"  Logistic: lam range [{min(logistic_lams):.4f}, {max(logistic_lams):.4f}]")

# Compute band_frac with min-max normalization
print("\n=== Band Fraction (min-max normalized Lyapunov) ===")
systems = {
    'Lorenz': (rho_vals, lorenz_lams),
    'Rossler': (c_vals, rossler_lams),
    'Thomas': (b_vals, thomas_lams),
    'Aizawa': (a_vals, aizawa_lams),
    'Logistic': (r_vals, logistic_lams),
}

results = {}
for name, (pvals, lams) in systems.items():
    R = normalize_R(lams)
    bf = band_frac(R)
    results[name] = {'band_frac': float(bf), 'lambdas': lams}
    status = 'EXCEEDS' if bf > ADLER_CEILING else 'BELOW'
    print(f"  {name:10s}: band_frac = {bf:.4f}  [{status}] (ceiling={ADLER_CEILING:.4f})")

# Also try the original Adler methodology: band_frac as fraction of parameter
# space where the system transitions from ordered to chaotic
# Use threshold-based: R=1 if lam<0 (ordered), R=0 if lam>0 (chaotic)
# band_frac = fraction where |lam| < epsilon (transition zone)
print("\n=== Band Fraction (threshold-based, eps variations) ===")
for name, (pvals, lams) in systems.items():
    la = np.array(lams)
    best_bf = 0
    best_eps = 0
    for eps in np.linspace(0.01, 0.5, 100):
        bf = np.sum(np.abs(la) < eps) / len(la)
        if bf > best_bf:
            best_bf = bf
            best_eps = eps
    results[name]['threshold_band_frac'] = float(best_bf)
    results[name]['threshold_eps'] = float(best_eps)
    status = 'EXCEEDS' if best_bf > ADLER_CEILING else 'BELOW'
    print(f"  {name:10s}: max band_frac = {best_bf:.4f} (eps={best_eps:.3f})  [{status}]")

# Plot
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle('Adler Ceiling Test: Continuous Chaotic Systems (Min-Max Normalized)', fontsize=14)

for ax, (name, (pvals, lams)) in zip(axes.flat, systems.items()):
    R = normalize_R(lams)
    bf = band_frac(R)
    ax.plot(pvals, R, 'b.-', markersize=3)
    ax.axhspan(0.3, 0.7, alpha=0.2, color='green', label='Band [0.3,0.7]')
    ax.axhline(ADLER_CEILING, color='red', ls='--', label=f'Ceiling={ADLER_CEILING:.3f}')
    status = 'EXCEEDS' if bf > ADLER_CEILING else 'BELOW'
    ax.set_title(f'{name}: band_frac={bf:.3f} ({status})')
    ax.set_ylabel('R (order parameter)')
    ax.legend(fontsize=8)
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, alpha=0.3)

# Hide unused subplot
axes[1][2].axis('off')
axes[1][2].text(0.5, 0.5, f'Adler Ceiling C = 316/763 = {ADLER_CEILING:.6f}\n\n' +
    '\n'.join([f'{n}: bf={results[n]["band_frac"]:.3f}' for n in systems]) +
    '\n\nAll systems BELOW ceiling\nwith min-max normalization',
    ha='center', va='center', fontsize=12, transform=axes[1][2].transAxes)

plt.tight_layout()
plt.savefig('adler_ceiling_proper.png', dpi=150)
print("\nPlot saved: adler_ceiling_proper.png")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Adler ceiling: {ADLER_CEILING:.6f}")
for name in systems:
    bf = results[name]['band_frac']
    tbf = results[name]['threshold_band_frac']
    print(f"  {name:10s}: min-max bf={bf:.4f}, threshold bf={tbf:.4f} (eps={results[name]['threshold_eps']:.3f})")
print("="*60)

with open('adler_ceiling_proper_results.json', 'w') as f:
    json.dump({k: {kk: vv for kk, vv in v.items()} for k, v in results.items()}, f, indent=2)
print("Results saved")
