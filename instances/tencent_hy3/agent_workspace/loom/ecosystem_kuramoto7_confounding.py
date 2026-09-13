# Diagnose WHY proper-restart Kc(N) diverges. Hypothesis: naive onset R>0.5
# grows with N because initial R0 ~ 1/sqrt(N); the TRUE jump point is N-independent.
import os, json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def batch_R(N, K0, nseed, alpha=0.6, dt=0.02, nsteps=250, seed=0):
    rng = np.random.RandomState(seed)
    th = rng.uniform(0, 2*math.pi, size=(nseed, N))
    R0 = np.abs(np.mean(np.exp(1j*th), axis=1)).mean()
    for _ in range(nsteps):
        z = np.mean(np.exp(1j*th), axis=1)
        R = np.abs(z); psi = np.angle(z)
        sin = np.sin(psi[:,None]-th)
        dth = N*R[:,None]*sin
        K = K0*(R**alpha)[:,None]
        th = th + dt*((K/N)*dth)
    return np.abs(np.mean(np.exp(1j*th), axis=1)).mean(), R0

Kgrid = np.linspace(0.1, 2.5, 37)
Ns = [15, 30, 60, 100, 150, 200, 300]
NSEED = 12
rows = []
for N in Ns:
    rngN = np.random.RandomState(123+N)
    Rmat = np.zeros((NSEED, len(Kgrid)))
    R0 = None
    for k, K0 in enumerate(Kgrid):
        rmean, R0v = batch_R(N, K0, NSEED, seed=rngN.randint(10**9))
        Rmat[:, k] = rmean
        if k == 0:
            R0 = R0v
    Rm = Rmat.mean(0)
    idx = np.where(Rm > 0.5)[0]
    onset05 = float(Kgrid[idx[0]]) if len(idx) else float('nan')
    dR = np.gradient(Rm, Kgrid)
    onset_jump = float(Kgrid[np.argmax(dR)])
    rows.append({'n': N, 'R0': float(R0), 'onset_R05': onset05, 'onset_jump': onset_jump})
    print('N=%4d R0=%.3f onset_R05=%.2f jump=%.2f' % (N, R0, onset05, onset_jump))

here = os.path.dirname(os.path.abspath(__file__))
json.dump(rows, open(os.path.join(here, 'ecosystem_kuramoto7_result.json'), 'w'), indent=2)

fig, ax1 = plt.subplots(figsize=(8, 5))
ax1.plot([r['n'] for r in rows], [r['onset_R05'] for r in rows], 'o-', color='navy', label='naive onset (R>0.5)')
ax1.plot([r['n'] for r in rows], [r['onset_jump'] for r in rows], 's-', color='crimson', label='true jump (max dR/dK)')
ax1.set_xscale('log'); ax1.set_xlabel('N'); ax1.set_ylabel('Kc')
ax1.axhline(1.6, ls=':', color='green', label='Agora Kc~1.6')
ax2 = ax1.twinx()
ax2.plot([r['n'] for r in rows], [r['R0'] for r in rows], '^-', color='gray', label='initial R0', alpha=0.7)
ax2.set_ylabel('initial R0', color='gray')
ax1.set_title('Why naive Kc(N) diverges: initial R0 ~ 1/sqrt(N) confound')
h1, l1 = ax1.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1+h2, l1+l2, fontsize=8); ax1.grid(alpha=0.3)
fig.tight_layout()
f = os.path.join(here, 'ecosystem_kuramoto7_confounding.png')
fig.savefig(f, dpi=130)
print('saved', f)
