# CORRECTED Kuramoto with adaptive coupling K_eff = K0 * R^alpha (proper factor).
# d(theta_i)/dt = omega_i + K0*R^alpha * sin(psi - theta_i)
# Expect: pivot at alpha=0. alpha<0 boosts nucleation (lower onset K0);
# alpha>0 hinders (bootstrap problem). Validate alpha=0 -> Kc = 4*gamma/pi.
import os, json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def batch(N, gamma, K0, alpha, nseed, dt=0.01, nsteps=1400, seed=0):
    rng = np.random.RandomState(seed)
    Rvals = []
    for s in range(nseed):
        om = rng.uniform(-gamma, gamma, N)
        th = rng.uniform(0, 2*math.pi, N)
        # transient
        for t in range(nsteps):
            z = np.mean(np.exp(1j*th))
            R = abs(z); psi = np.angle(z)
            th = th + dt*(om + (K0*R**alpha)*np.sin(psi-th))
        # measure
        Rm = []
        for t in range(400):
            z = np.mean(np.exp(1j*th))
            R = abs(z); psi = np.angle(z)
            th = th + dt*(om + (K0*R**alpha)*np.sin(psi-th))
            Rm.append(abs(np.mean(np.exp(1j*th))))
        Rvals.append(np.mean(Rm))
    return np.mean(Rvals)

N = 300; gamma = 1.0
alphas = [-0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0, 1.25]
Kgrid = np.linspace(0.3, 9.0, 48)
NSEED = 3
res = []
for a in alphas:
    rngN = np.random.RandomState(17)
    Rmat = np.zeros(len(Kgrid))
    for k, K0 in enumerate(Kgrid):
        Rmat[k] = batch(N, gamma, K0, a, NSEED, seed=rngN.randint(10**9))
    idx = np.where(Rmat > 0.5)[0]
    onset = float(Kgrid[idx[0]]) if len(idx) else float('nan')
    res.append({'alpha': a, 'onset': onset})
    print('alpha=%+.2f  onset_K0=%.2f   (Kc_theory(alpha0)=%.3f)' % (a, onset, 4*gamma/math.pi))

here = os.path.dirname(os.path.abspath(__file__))
json.dump({'N': N, 'gamma': gamma, 'alphas': alphas, 'Kgrid': Kgrid.tolist(),
           'Kc_theory': 4*gamma/math.pi, 'res': res},
          open(os.path.join(here, 'ecosystem_kuramoto12_result.json'), 'w'), indent=2)

fig, ax = plt.subplots(figsize=(8,5))
xs=[r['alpha'] for r in res]; ys=[r['onset'] for r in res]
ax.plot(xs, ys, 'o-', color='navy')
ax.axvline(0.0, ls=':', color='gray', label='alpha=0 (fixed coupling, Kc=%.2f)'%(4*gamma/math.pi))
ax.set_xlabel('coupling exponent alpha (K_eff = K0 * R^alpha)')
ax.set_ylabel('onset K0 (steady R>0.5)')
ax.set_title('CORRECTED: disordered-start adaptive Kuramoto, pivot at alpha=0 (N=%d)'%N)
ax.legend(); ax.grid(alpha=0.3); fig.tight_layout()
f=os.path.join(here,'ecosystem_kuramoto12_corrected.png')
fig.savefig(f, dpi=130); print('saved', f)
