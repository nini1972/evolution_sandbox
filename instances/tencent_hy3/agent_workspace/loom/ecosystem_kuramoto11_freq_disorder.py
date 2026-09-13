# DEFINITIVE: adaptive coupling exponent alpha in FREQUENCY-DISORDERED Kuramoto.
# Non-degenerate (natural frequencies omega ~ uniform[-gamma,gamma]).
# Prediction: alpha=1 is cross-over pivot. alpha<1 -> R^alpha> R -> STRONGER
# coupling when disordered -> LOWER onset K0. alpha>1 -> suppress -> HIGHER onset.
# Proper restart from uniform random phases each K0.
import os, json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def batch(N, gamma, K0, alpha, nseed, dt=0.02, nsteps=700, seed=0):
    rng = np.random.RandomState(seed)
    Rs = []
    for s in range(nseed):
        om = rng.uniform(-gamma, gamma, N)
        th = rng.uniform(0, 2*math.pi, N)
        for t in range(nsteps):
            z = np.mean(np.exp(1j*th))
            R = abs(z); psi = np.angle(z)
            th = th + dt*(om + (K0*R**alpha/N)*np.sin(psi-th))
        # average R over last 100 steps
        for _ in range(100):
            z = np.mean(np.exp(1j*th))
            R = abs(z); psi = np.angle(z)
            th = th + dt*(om + (K0*R**alpha/N)*np.sin(psi-th))
            Rs.append(abs(np.mean(np.exp(1j*th))))
    return np.mean(Rs)

N = 200; gamma = 1.0
alphas = [-0.5, 0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5]
Kgrid = np.linspace(0.2, 8.0, 60)
NSEED = 5
res = []
for a in alphas:
    rngN = np.random.RandomState(13)
    Rmat = np.zeros((NSEED, len(Kgrid)))
    for k, K0 in enumerate(Kgrid):
        Rmat[:, k] = batch(N, gamma, K0, a, 1, seed=rngN.randint(10**9))
    Rm = Rmat.mean(0)
    idx = np.where(Rm > 0.5)[0]
    onset = float(Kgrid[idx[0]]) if len(idx) else float('nan')
    res.append({'alpha': a, 'onset': onset})
    print('alpha=%.2f  onset_K0=%.2f' % (a, onset))

here = os.path.dirname(os.path.abspath(__file__))
json.dump({'N': N, 'gamma': gamma, 'alphas': alphas, 'Kgrid': Kgrid.tolist(), 'res': res},
          open(os.path.join(here, 'ecosystem_kuramoto11_result.json'), 'w'), indent=2)

fig, ax = plt.subplots(figsize=(8,5))
xs=[r['alpha'] for r in res]; ys=[r['onset'] for r in res]
ax.plot(xs, ys, 'o-', color='navy')
ax.axvline(1.0, ls=':', color='gray', label='alpha=1 pivot (Treaty 005: >1 suppresses)')
ax.set_xlabel('coupling exponent alpha (K=K0*R^alpha)')
ax.set_ylabel('onset K0 (steady R>0.5)')
ax.set_title('Frequency-disordered Kuramoto: alpha=1 cross-over (N=%d, gamma=%.1f)'%(N,gamma))
ax.legend(); ax.grid(alpha=0.3); fig.tight_layout()
f=os.path.join(here,'ecosystem_kuramoto11_freq_disorder.png')
fig.savefig(f, dpi=130); print('saved', f)
