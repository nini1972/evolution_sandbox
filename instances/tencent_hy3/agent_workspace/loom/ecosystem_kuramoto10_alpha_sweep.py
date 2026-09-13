# DEFINITIVE invariant: onset K0 vs coupling exponent alpha, PROPER-RESTART.
# Hypothesis: onset K0 DECREASES as alpha rises 0->1 (adaptive enhances),
# then ABRUPTLY diverges for alpha>=1 (suppression, cf. Agora Treaty 005).
import os, json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def make_uniform(N, rng):
    return rng.uniform(0, 2*math.pi, N)
def R0_of(th):
    return np.abs(np.mean(np.exp(1j*th)))
def batch(N, K0, alpha, nseed, dt=0.02, nsteps=400, seed=0):
    rng = np.random.RandomState(seed)
    th = np.array([make_uniform(N, rng) for _ in range(nseed)])
    for _ in range(nsteps):
        z = np.mean(np.exp(1j*th), axis=1)
        R = np.abs(z); psi = np.angle(z)
        sin = np.sin(psi[:,None]-th)
        K = K0*(R**alpha)[:,None]
        th = th + dt*((K/N)*(N*R[:,None]*sin))
    return np.abs(np.mean(np.exp(1j*th), axis=1)).mean()

N = 100
alphas = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.5]
Kgrid = np.linspace(0.2, 6.0, 60)
NSEED = 8
res = []
for a in alphas:
    rngN = np.random.RandomState(11)
    Rmat = np.zeros((NSEED, len(Kgrid)))
    for k, K0 in enumerate(Kgrid):
        Rmat[:, k] = batch(N, K0, a, NSEED, seed=rngN.randint(10**9))
    Rm = Rmat.mean(0)
    idx = np.where(Rm > 0.5)[0]
    onset = float(Kgrid[idx[0]]) if len(idx) else float('nan')
    res.append({'alpha': a, 'onset': onset})
    print('alpha=%.1f  onset_K0=%.2f' % (a, onset))

here = os.path.dirname(os.path.abspath(__file__))
json.dump({'N': N, 'alphas': alphas, 'Kgrid': Kgrid.tolist(), 'res': res},
          open(os.path.join(here, 'ecosystem_kuramoto10_result.json'), 'w'), indent=2)

fig, ax = plt.subplots(figsize=(8,5))
xs = [r['alpha'] for r in res]; ys = [r['onset'] for r in res]
ax.plot(xs, ys, 'o-', color='navy')
ax.axvline(1.0, ls=':', color='gray', label='alpha=1 (predicted cross-over)')
ax.set_xlabel('coupling exponent alpha (K=K0*R^alpha)')
ax.set_ylabel('onset K0 (R>0.5)')
ax.set_title('Adaptive coupling: enhanced sync for alpha<1, divergent for alpha>=1 (N=%d)'%N)
ax.legend(); ax.grid(alpha=0.3); fig.tight_layout()
f = os.path.join(here, 'ecosystem_kuramoto10_alpha_sweep.png')
fig.savefig(f, dpi=130); print('saved', f)
