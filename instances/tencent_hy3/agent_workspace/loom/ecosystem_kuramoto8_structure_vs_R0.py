# Clean head-to-head: is low-Kc due to STRUCTURE or just high R0?
# A: semantic clusters (R0~0.38, structured)
# B: narrow-arc random (same R0~0.38, but NO cluster structure)
# C: pure uniform random (R0~1/sqrt(N), unstructured)
import os, json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

CLUSTERS8 = np.array([0.0, 0.785, 1.571, 2.356, 3.927, 4.712, 5.498, 6.283]) % (2*math.pi)

def make_A(N, rng):  # semantic clusters, R0 high
    return np.tile(CLUSTERS8, N//8 + 1)[:N].astype(float)
def make_B(N, rng):  # narrow arc random, matched R0~0.38
    # choose arc half-width w so that expected R0 ~ 0.38 -> w via R0=2/(w)*sin(w/2)~? use w=1.0
    w = 1.0
    return rng.uniform(-w/2, w/2, N) + 0.0
def make_C(N, rng):
    return rng.uniform(0, 2*math.pi, N)

def batch_R(th0fn, N, K0, nseed, alpha=0.6, dt=0.02, nsteps=300, seed=0):
    rng = np.random.RandomState(seed)
    th = np.array([th0fn(N, rng) for _ in range(nseed)])
    for _ in range(nsteps):
        z = np.mean(np.exp(1j*th), axis=1)
        R = np.abs(z); psi = np.angle(z)
        sin = np.sin(psi[:,None]-th)
        dth = N*R[:,None]*sin
        K = K0*(R**alpha)[:,None]
        th = th + dt*((K/N)*dth)
    Rf = np.abs(np.mean(np.exp(1j*th), axis=1))
    R0 = np.abs(np.mean(np.exp(1j*np.array([th0fn(N, rng) for _ in range(nseed)])), axis=1)).mean()
    return Rf.mean(), R0

N = 80
Kgrid = np.linspace(0.05, 2.5, 50)
NSEED = 10
conds = {'A_semantic': make_A, 'B_narrow_random': make_B, 'C_uniform_random': make_C}
results = {}
for name, f in conds.items():
    rngN = np.random.RandomState(7)
    Rmat = np.zeros((NSEED, len(Kgrid)))
    R0s = []
    for k, K0 in enumerate(Kgrid):
        rmean, R0 = batch_R(f, N, K0, NSEED, seed=rngN.randint(10**9))
        Rmat[:, k] = rmean
        if k == 0:
            R0s.append(R0)
    Rm = Rmat.mean(0)
    idx = np.where(Rm > 0.5)[0]
    onset = float(Kgrid[idx[0]]) if len(idx) else float('nan')
    results[name] = {'R0': float(np.mean(R0s)), 'onset': onset,
                     'Rmean': Rm.tolist()}
    print('%-18s R0=%.3f onset_K0=%.2f' % (name, results[name]['R0'], onset))

here = os.path.dirname(os.path.abspath(__file__))
json.dump({'N': N, 'Kgrid': Kgrid.tolist(), 'results': results},
          open(os.path.join(here, 'ecosystem_kuramoto8_result.json'), 'w'), indent=2)

fig, ax = plt.subplots(figsize=(8, 5))
cols = {'A_semantic': 'navy', 'B_narrow_random': 'crimson', 'C_uniform_random': 'gray'}
for name, c in cols.items():
    ax.plot(Kgrid, results[name]['Rmean'], '-', color=c, label='%s (R0=%.2f)' % (name, results[name]['R0']))
ax.axhline(0.5, ls=':', color='k')
ax.set_xlabel('K0'); ax.set_ylabel('steady <R>')
ax.set_title('Structure vs R0: which lowers Kc? (N=%d)' % N)
ax.legend(fontsize=9); ax.grid(alpha=0.3)
fig.tight_layout()
f = os.path.join(here, 'ecosystem_kuramoto8_structure_vs_R0.png')
fig.savefig(f, dpi=130)
print('saved', f)
