"""
Adler Ceiling Test for Continuous Chaotic Systems (Pure NumPy RK4)
Tests whether Lorenz, Rossler, Thomas, and Aizawa attractors exceed
the Adler ceiling C = 316/763 on the band_frac metric.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

ADLER_CEILING = 316/763
print(f"Adler Ceiling C = 316/763 = {ADLER_CEILING:.10f}")

def rk4_step(f, x, dt):
    k1 = f(x)
    k2 = f(x + 0.5*dt*k1)
    k3 = f(x + 0.5*dt*k2)
    k4 = f(x + dt*k3)
    return x + dt/6*(k1 + 2*k2 + 2*k3 + k4)

def max_lyapunov(f, jac, x0, dt, n_transient, n_measure, dim=3):
    x = np.array(x0, dtype=np.float64)
    for _ in range(n_transient):
        x = rk4_step(f, x, dt)
    w = np.random.randn(dim)
    w = w / np.linalg.norm(w)
    lyap_sum = 0.0
    lyap_count = 0
    for _ in range(n_measure):
        # Integrate state
        x = rk4_step(f, x, dt)
        # Integrate tangent vector
        k1 = jac(x) @ w
        k2 = jac(x) @ (w + 0.5*dt*k1)
        k3 = jac(x) @ (w + 0.5*dt*k2)
        k4 = jac(x) @ (w + dt*k3)
        w_new = w + dt/6*(k1 + 2*k2 + 2*k3 + k4)
        norm = np.linalg.norm(w_new)
        if norm > 0:
            lyap_sum += np.log(norm)
            w_new = w_new / norm
            lyap_count += 1
        w = w_new
    if lyap_count == 0:
        return 0.0
    return lyap_sum / (lyap_count * dt)

# System definitions: f(x) and jac(x)
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

def aizawa_f(a, b, c, d, e, f_param):
    def f(x):
        return np.array([
            (x[2]-b)*x[0]-d*x[1],
            d*x[0]+(x[2]-b)*x[1],
            c+a*x[2]-x[2]**3/3-(x[0]**2+x[1]**2)*(1+e*x[2])+f_param*x[2]*x[0]**3
        ])
    def j(x):
        return np.array([
            [x[2]-b, -d, x[0]],
            [d, x[2]-b, x[1]],
            [-2*x[0]*(1+e*x[2])+3*f_param*x[2]*x[0]**2,
             -2*x[1]*(1+e*x[2]),
             a-2*x[2]**2/3-e*(x[0]**2+x[1]**2)+f_param*x[0]**3]
        ])
    return f, j

def lyap_to_R(lam, scale=50.0):
    return 1.0 / (1.0 + np.exp(lam * scale))

def compute_band_frac(lambdas, lo=0.3, hi=0.7):
    R = np.array([lyap_to_R(l) for l in lambdas])
    band = np.sum((R >= lo) & (R <= hi))
    return band / len(R), R

print("\n=== Testing Continuous Chaotic Systems vs Adler Ceiling ===\n")
results = {}

# 1. Lorenz: sweep rho
print("1. Lorenz attractor (sweeping rho from 20 to 50)...")
rho_vals = np.linspace(20, 50, 80)
lorenz_lams = []
for rho in rho_vals:
    f, j = lorenz_f(10, rho, 8/3)
    lam = max_lyapunov(f, j, [1.0,1.0,1.0], dt=0.01, n_transient=500, n_measure=500)
    lorenz_lams.append(lam)
    print(f"  rho={rho:.1f} -> lam1={lam:.4f}")
bf_lorenz, R_lorenz = compute_band_frac(lorenz_lams)
results['lorenz'] = {'param':'rho','range':[20,50],'n':len(rho_vals),'band_frac':bf_lorenz,'lambdas':lorenz_lams}
print(f"  Lorenz band_frac = {bf_lorenz:.4f} {'EXCEEDS' if bf_lorenz>ADLER_CEILING else 'BELOW'}\n")

# 2. Rossler: sweep c
print("2. Rossler attractor (sweeping c from 2 to 10)...")
c_vals = np.linspace(2, 10, 80)
rossler_lams = []
for c in c_vals:
    f, j = rossler_f(0.2, 0.2, c)
    lam = max_lyapunov(f, j, [0.1,0.1,0.1], dt=0.02, n_transient=500, n_measure=500)
    rossler_lams.append(lam)
    print(f"  c={c:.2f} -> lam1={lam:.4f}")
bf_rossler, R_rossler = compute_band_frac(rossler_lams)
results['rossler'] = {'param':'c','range':[2,10],'n':len(c_vals),'band_frac':bf_rossler,'lambdas':rossler_lams}
print(f"  Rossler band_frac = {bf_rossler:.4f} {'EXCEEDS' if bf_rossler>ADLER_CEILING else 'BELOW'}\n")

# 3. Thomas: sweep b
print("3. Thomas attractor (sweeping b from 0.05 to 0.50)...")
b_vals = np.linspace(0.05, 0.50, 80)
thomas_lams = []
for b in b_vals:
    f, j = thomas_f(b)
    lam = max_lyapunov(f, j, [1.0,1.0,1.0], dt=0.05, n_transient=500, n_measure=500)
    thomas_lams.append(lam)
    print(f"  b={b:.3f} -> lam1={lam:.4f}")
bf_thomas, R_thomas = compute_band_frac(thomas_lams)
results['thomas'] = {'param':'b','range':[0.05,0.50],'n':len(b_vals),'band_frac':bf_thomas,'lambdas':thomas_lams}
print(f"  Thomas band_frac = {bf_thomas:.4f} {'EXCEEDS' if bf_thomas>ADLER_CEILING else 'BELOW'}\n")

# 4. Aizawa: sweep a
print("4. Aizawa attractor (sweeping a from 0.5 to 1.5)...")
a_vals = np.linspace(0.5, 1.5, 80)
aizawa_lams = []
for a in a_vals:
    f, j = aizawa_f(a, 0.7, 0.6, 3.5, 0.25, 0.1)
    lam = max_lyapunov(f, j, [0.1,0.1,0.1], dt=0.02, n_transient=500, n_measure=500)
    aizawa_lams.append(lam)
    print(f"  a={a:.3f} -> lam1={lam:.4f}")
bf_aizawa, R_aizawa = compute_band_frac(aizawa_lams)
results['aizawa'] = {'param':'a','range':[0.5,1.5],'n':len(a_vals),'band_frac':bf_aizawa,'lambdas':aizawa_lams}
print(f"  Aizawa band_frac = {bf_aizawa:.4f} {'EXCEEDS' if bf_aizawa>ADLER_CEILING else 'BELOW'}\n")

# Plotting
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Adler Ceiling Test: Band Fraction for Chaotic Systems', fontsize=14)
systems = [('lorenz', rho_vals, 'rho', 'Lorenz'),
           ('rossler', c_vals, 'c', 'Rossler'),
           ('thomas', b_vals, 'b', 'Thomas'),
           ('aizawa', a_vals, 'a', 'Aizawa')]
for ax, (key, pvals, pname, label) in zip(axes.flat, systems):
    lams = results[key]['lambdas']
    R = np.array([lyap_to_R(l) for l in lams])
    bf = results[key]['band_frac']
    ax.plot(pvals, R, 'b.-', markersize=3)
    ax.axhspan(0.3, 0.7, alpha=0.2, color='green', label='Intermediate band [0.3,0.7]')
    ax.axhline(ADLER_CEILING, color='red', ls='--', label=f'Adler ceiling={ADLER_CEILING:.3f}')
    ax.set_xlabel(pname)
    ax.set_ylabel('R (order parameter)')
    status = 'EXCEEDS' if bf > ADLER_CEILING else 'BELOW'
    ax.set_title(f'{label}: band_frac={bf:.3f} ({status})')
    ax.legend(fontsize=8)
    ax.set_ylim(-0.05, 1.05)
plt.tight_layout()
plt.savefig('adler_ceiling_chaotic_systems.png', dpi=150)
print("Plot saved: adler_ceiling_chaotic_systems.png")

print("\n" + "="*60)
print("ADLER CEILING TEST SUMMARY")
print("="*60)
print(f"Ceiling: C = 316/763 = {ADLER_CEILING:.6f}")
for key in ['lorenz','rossler','thomas','aizawa']:
    bf = results[key]['band_frac']
    status = 'EXCEEDS' if bf > ADLER_CEILING else 'BELOW'
    print(f"  {key:10s}: band_frac = {bf:.4f}  [{status}]")
print("="*60)

with open('adler_ceiling_results.json', 'w') as f:
    json.dump({k: {kk: vv for kk, vv in v.items()} for k, v in results.items()}, f, indent=2)
print("Results saved: adler_ceiling_results.json")
