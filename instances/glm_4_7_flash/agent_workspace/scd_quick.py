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

# Systems
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

N = 150  # Quick resolution

print("=== Sign Crossing Density (SCD) Analysis ===\n")
print(f"Resolution: N={N} per system\n")

results = {}

# Logistic
r_vals = np.linspace(3.5, 4.0, N)
log_lams = np.array([logistic_lyap(r) for r in r_vals])
log_cross = np.sum(np.diff(np.sign(log_lams)) != 0)
log_scd = log_cross / 0.5
results['Logistic'] = {'crossings': log_cross, 'scd': log_scd, 'params': r_vals.tolist(), 'lams': log_lams.tolist()}
print(f"Logistic: {log_cross} crossings, SCD={log_scd:.1f}/unit")

# Lorenz
rho_vals = np.linspace(20, 50, N)
lorenz_lams = []
for rho in rho_vals:
    f, j = lorenz_f(10, rho, 8/3)
    lorenz_lams.append(max_lyapunov(f, j, [1.0,1.0,1.0], 0.01))
lorenz_lams = np.array(lorenz_lams)
lorenz_cross = np.sum(np.diff(np.sign(lorenz_lams)) != 0)
lorenz_scd = lorenz_cross / 30.0
results['Lorenz'] = {'crossings': lorenz_cross, 'scd': lorenz_scd, 'params': rho_vals.tolist(), 'lams': lorenz_lams.tolist()}
print(f"Lorenz: {lorenz_cross} crossings, SCD={lorenz_scd:.1f}/unit")

# Rossler
c_vals = np.linspace(2, 10, N)
rossler_lams = []
for c in c_vals:
    f, j = rossler_f(0.2, 0.2, c)
    rossler_lams.append(max_lyapunov(f, j, [0.1,0.1,0.1], 0.02))
rossler_lams = np.array(rossler_lams)
rossler_cross = np.sum(np.diff(np.sign(rossler_lams)) != 0)
rossler_scd = rossler_cross / 8.0
results['Rossler'] = {'crossings': rossler_cross, 'scd': rossler_scd, 'params': c_vals.tolist(), 'lams': rossler_lams.tolist()}
print(f"Rossler: {rossler_cross} crossings, SCD={rossler_scd:.1f}/unit")

# Thomas
b_vals = np.linspace(0.05, 0.50, N)
thomas_lams = []
for b in b_vals:
    f, j = thomas_f(b)
    thomas_lams.append(max_lyapunov(f, j, [1.0,1.0,1.0], 0.05))
thomas_lams = np.array(thomas_lams)
thomas_cross = np.sum(np.diff(np.sign(thomas_lams)) != 0)
thomas_scd = thomas_cross / 0.45
results['Thomas'] = {'crossings': thomas_cross, 'scd': thomas_scd, 'params': b_vals.tolist(), 'lams': thomas_lams.tolist()}
print(f"Thomas: {thomas_cross} crossings, SCD={thomas_scd:.1f}/unit")

# === Plot ===
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle(f'Sign Crossing Density (SCD): Robust Transition Counting (N={N})\nAdler Ceiling C=316/763={ADLER_CEILING:.4f}', fontsize=13)

for ax, (name, d) in zip(axes.flat, results.items()):
    params = np.array(d['params'])
    lams = np.array(d['lams'])
    ax.plot(params, lams, 'b.-', markersize=2)
    ax.axhline(0, color='red', ls='--', alpha=0.5)
    cross_idx = np.where(np.diff(np.sign(lams)) != 0)[0]
    for ci in cross_idx:
        ax.axvline(params[ci], color='green', alpha=0.3, ls=':')
    ax.set_title(f'{name}: {d["crossings"]} crossings, SCD={d["scd"]:.1f}/unit', fontsize=11)
    ax.set_xlabel('Parameter')
    ax.set_ylabel('Max Lyapunov λ')
    ax.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig('scd_analysis.png', dpi=150)
print("\nPlot saved: scd_analysis.png")

with open('scd_results.json', 'w') as f:
    summary = {k: {'crossings': v['crossings'], 'scd': v['scd']} for k, v in results.items()}
    json.dump(summary, f, indent=2)

print("\n=== SUMMARY ===")
print(f"Adler Ceiling C = {ADLER_CEILING:.6f}")
print(f"{'System':12s} {'Crossings':>10s} {'SCD':>8s}")
for name, d in results.items():
    print(f"  {name:10s} {d['crossings']:10d} {d['scd']:8.1f}")
print("\nKey insight: SCD is methodology-independent (no sigmoid scale needed)")
print("High SCD = many periodic windows (logistic map behavior)")
print("Low SCD = single smooth transition (continuous systems)")
