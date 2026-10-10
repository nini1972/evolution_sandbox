"""dt-axis probe: does the inferred 'universal law' depend on the numerical horizon dt?
Thesis: apparent laws are cross-sections of H=(T,N,dt,R0,seeds). If the dt-axis
changes t_esc distribution/systematics, then even our own law is horizon-dependent."""
import numpy as np, json, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = "dt_axis"
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(7)
N = 150; K0 = 5.0; alpha = 2.0; kappa = 1.0; THRESH = 0.8; NSEEDS = 300; TMAX = 200.0

def esc_times_dt(dt, seeds=NSEEDS, tmax=TMAX):
    ns = int(tmax/dt); lts = []
    for s in range(seeds):
        om = rng.uniform(-kappa, kappa, N); th = rng.uniform(0, 2*np.pi, N)
        done = False
        for it in range(ns):
            z = np.mean(np.exp(1j*th)); R = abs(z)
            if R > THRESH: lts.append(it*dt); done = True; break
            K = K0 * R**alpha
            th = th + dt*(om + K*np.sin(np.angle(z) - th))
        if not done: lts.append(tmax+1.0)
    lts = np.array(lts)
    fin = lts[lts <= tmax]
    return lts, fin

dts = [0.002, 0.005, 0.01, 0.02, 0.05, 0.1]
res = {}
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
for ax, col in zip(axes, ['med', 'p10', 'P(1.5)']):
    ys = []
    for dt in dts:
        lts, fin = esc_times_dt(dt)
        med = np.median(fin) if len(fin) else np.nan
        p10 = np.percentile(fin, 10) if len(fin) else np.nan
        P15 = np.mean(lts < 1.5)
        res[dt] = dict(med=med, p10=p10, P15=float(P15), n_fin=len(fin))
        ys.append({'med':med, 'p10':p10, 'P(1.5)':P15}[col])
        print(f"dt={dt}: med={med:.3f} p10={p10:.3f} P(1.5)={P15:.3f} n={len(fin)}", flush=True)
    ax.semilogx(dts, ys, 'o-', lw=2)
    ax.set_xlabel('dt'); ax.set_ylabel(col); ax.set_title(f'{col} vs dt')
    ax.grid(True, which='both', alpha=0.3)
fig.suptitle('dt-axis probe: universal law as cross-section of numerical horizon')
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'dt_axis.png'), dpi=140)

json.dump(res, open(os.path.join(OUT, 'dt_axis.json'), 'w'), indent=1)
print("saved dt_axis.png / dt_axis.json")
