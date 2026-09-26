"""
Adler Ceiling: Sigmoid Scale Sensitivity Analysis
Find the maximum band_frac across sigmoid scales for each system.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

ADLER_CEILING = 316/763
print(f"Adler Ceiling C = 316/763 = {ADLER_CEILING:.10f}")

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

def lyap_to_R(lam, scale):
    return 1.0 / (1.0 + np.exp(lam * scale))

def band_frac_at_scale(lambdas, scale, lo=0.3, hi=0.7):
    R = np.array([lyap_to_R(l, scale) for l in lambdas])
    return np.sum((R >= lo) & (R <= hi)) / len(R)

# Compute Lyapunov spectra (reuse from previous run)
print("Computing Lyapunov spectra...")

# Lorenz
rho_vals = np.linspace(20, 50, 120)
lorenz_lams = []
for rho in rho_vals:
    f, j = lorenz_f(10, rho, 8/3)
    lam = max_lyapunov(f, j, [1.0,1.0,1.0], dt=0.01, n_transient=500, n_measure=500)
    lorenz_lams.append(lam)
print(f"  Lorenz: {len(lorenz_lams)} points, lam range [{min(lorenz_lams):.3f}, {max(lorenz_lams):.3f}]")

# Rossler
c_vals = np.linspace(2, 10, 120)
rossler_lams = []
for c in c_vals:
    f, j = rossler_f(0.2, 0.2, c)
    lam = max_lyapunov(f, j, [0.1,0.1,0.1], dt=0.02, n_transient=500, n_measure=500)
    rossler_lams.append(lam)
print(f"  Rossler: {len(rossler_lams)} points, lam range [{min(rossler_lams):.3f}, {max(rossler_lams):.3f}]")

# Thomas
b_vals = np.linspace(0.05, 0.50, 120)
thomas_lams = []
for b in b_vals:
    f, j = thomas_f(b)
    lam = max_lyapunov(f, j, [1.0,1.0,1.0], dt=0.05, n_transient=500, n_measure=500)
    thomas_lams.append(lam)
print(f"  Thomas: {len(thomas_lams)} points, lam range [{min(thomas_lams):.3f}, {max(thomas_lams):.3f}]")

# Aizawa
a_vals = np.linspace(0.5, 1.5, 120)
aizawa_lams = []
for a in a_vals:
    f, j = aizawa_f(a, 0.7, 0.6, 3.5, 0.25, 0.1)
    lam = max_lyapunov(f, j, [0.1,0.1,0.1], dt=0.02, n_transient=500, n_measure=500)
    aizawa_lams.append(lam)
print(f"  Aizawa: {len(aizawa_lams)} points, lam range [{min(aizawa_lams):.3f}, {max(aizawa_lams):.3f}]")

# Logistic map for reference
print("Computing logistic map Lyapunov spectrum...")
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
print(f"  Logistic: {len(logistic_lams)} points, lam range [{min(logistic_lams):.3f}, {max(logistic_lams):.3f}]")

# Sweep sigmoid scales
scales = np.logspace(-1, 3, 200)  # 0.1 to 1000
systems = {
    'Lorenz': lorenz_lams,
    'Rossler': rossler_lams,
    'Thomas': thomas_lams,
    'Aizawa': aizawa_lams,
    'Logistic': logistic_lams,
}

print("\n=== Band_frac vs Sigmoid Scale ===")
max_bf = {}
for name, lams in systems.items():
    bfs = [band_frac_at_scale(lams, s) for s in scales]
    max_bf[name] = (max(bfs), scales[np.argmax(bfs)])
    print(f"  {name:10s}: max band_frac = {max(bfs):.4f} at scale={scales[np.argmax(bfs)]:.2f}  "
          f"{'EXCEEDS' if max(bfs)>ADLER_CEILING else 'BELOW'} ceiling ({ADLER_CEILING:.4f})")

# Plot
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Left: band_frac vs scale
ax = axes[0]
for name, lams in systems.items():
    bfs = [band_frac_at_scale(lams, s) for s in scales]
    ax.semilogx(scales, bfs, label=f"{name} (max={max(bfs):.3f})", linewidth=2)
ax.axhline(ADLER_CEILING, color='red', ls='--', linewidth=2, label=f'Adler ceiling={ADLER_CEILING:.4f}')
ax.set_xlabel('Sigmoid scale parameter')
ax.set_ylabel('band_frac')
ax.set_title('Band_frac vs Sigmoid Scale')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)

# Right: R vs parameter for best scale of each system
ax = axes[1]
best_configs = {
    'Lorenz': (rho_vals, lorenz_lams, max_bf['Lorenz'][1]),
    'Rossler': (c_vals, rossler_lams, max_bf['Rossler'][1]),
    'Thomas': (b_vals, thomas_lams, max_bf['Thomas'][1]),
    'Aizawa': (a_vals, aizawa_lams, max_bf['Aizawa'][1]),
    'Logistic': (r_vals, logistic_lams, max_bf['Logistic'][1]),
}
for name, (pvals, lams, best_scale) in best_configs.items():
    R = np.array([lyap_to_R(l, best_scale) for l in lams])
    pn = (pvals - pvals[0]) / (pvals[-1] - pvals[0])  # normalize to [0,1]
    ax.plot(pn, R, label=f"{name} (scale={best_scale:.1f})", linewidth=1.5)
ax.axhspan(0.3, 0.7, alpha=0.15, color='green')
ax.set_xlabel('Normalized parameter')
ax.set_ylabel('R (order parameter)')
ax.set_title('Order Parameter Crossover (best scale per system)')
ax.legend(fontsize=8)
ax.set_ylim(-0.05, 1.05)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('adler_ceiling_scale_sensitivity.png', dpi=150)
print("\nPlot saved: adler_ceiling_scale_sensitivity.png")

# Summary
print("\n" + "="*60)
print("MAXIMUM BAND_FRAC SUMMARY (across sigmoid scales)")
print("="*60)
print(f"Adler ceiling: C = 316/763 = {ADLER_CEILING:.6f}")
for name in systems:
    bf, sc = max_bf[name]
    status = 'EXCEEDS ***' if bf > ADLER_CEILING else 'BELOW'
    print(f"  {name:10s}: max band_frac = {bf:.4f} (scale={sc:.2f})  [{status}]")
print("="*60)

results = {name: {'max_band_frac': max_bf[name][0], 'best_scale': max_bf[name][1],
                 'exceeds_ceiling': max_bf[name][0] > ADLER_CEILING,
                 'lambdas': lams} for name, lams in systems.items()}
with open('adler_ceiling_scale_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print("Results saved: adler_ceiling_scale_results.json")
