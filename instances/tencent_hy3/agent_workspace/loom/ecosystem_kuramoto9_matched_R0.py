# Corroborate across N: matched-R0 control, multimodal vs unimodal.
import os, json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

CLUSTERS8 = (np.array([0.0,0.785,1.571,2.356,3.927,4.712,5.498,6.283])) % (2*math.pi)

def make_semantic(N, rng):
    return np.tile(CLUSTERS8, N//8+1)[:N].astype(float)
def make_vonmises(N, rng, kappa):
    return rng.vonmises(0.0, kappa, N)
def R0_of(th):
    return np.abs(np.mean(np.exp(1j*th)))

def batch(th0fn, N, K0, nseed, alpha=0.6, dt=0.02, nsteps=350, seed=0):
    rng = np.random.RandomState(seed)
    th = np.array([th0fn(N, rng) for _ in range(nseed)])
    for _ in range(nsteps):
        z = np.mean(np.exp(1j*th), axis=1)
        R = np.abs(z); psi = np.angle(z)
        sin = np.sin(psi[:,None]-th)
        K = K0*(R**alpha)[:,None]
        th = th + dt*((K/N)*(N*R[:,None]*sin))
    return np.abs(np.mean(np.exp(1j*th), axis=1)).mean()

rng_t = np.random.RandomState(1)
sem_R0 = np.mean([R0_of(make_semantic(80, rng_t)) for _ in range(300)])
target = sem_R0
ks = np.linspace(0.2, 4.0, 200)
vm_R0 = np.array([np.mean([R0_of(make_vonmises(80, rng_t, k)) for _ in range(15)]) for k in ks])
kappa = ks[np.argmin(np.abs(vm_R0-target))]

Ns = [80, 160, 320]
Kgrid = np.linspace(0.05, 2.5, 45)
NSEED = 8
conds = {'A_semantic': lambda N,r: make_semantic(N,r),
         'B_vonMises': lambda N,r: make_vonmises(N,r,kappa)}
rows = []
for N in Ns:
    entry = {'N': N}
    for name, f in conds.items():
        rngN = np.random.RandomState(7)
        Rmat = np.zeros((NSEED, len(Kgrid)))
        R0s = []
        for k, K0 in enumerate(Kgrid):
            Rmat[:, k] = batch(f, N, K0, NSEED, seed=rngN.randint(10**9))
            if k == 0:
                R0s.append(np.mean([R0_of(f(N, rngN)) for _ in range(NSEED)]))
        Rm = Rmat.mean(0)
        idx = np.where(Rm > 0.5)[0]
        onset = float(Kgrid[idx[0]]) if len(idx) else float('nan')
        entry[name] = {'R0': float(np.mean(R0s)), 'onset': onset}
    rows.append(entry)
    print('N=%3d  semantic onset=%.2f(R0=%.2f)  vonMises onset=%.2f(R0=%.2f)' % (
        N, entry['A_semantic']['onset'], entry['A_semantic']['R0'],
        entry['B_vonMises']['onset'], entry['B_vonMises']['R0']))

here = os.path.dirname(os.path.abspath(__file__))
json.dump({'semantic_R0_target': sem_R0, 'kappa': float(kappa),
           'Kgrid': Kgrid.tolist(), 'rows': rows},
          open(os.path.join(here,'ecosystem_kuramoto9_result.json'),'w'), indent=2)

fig, ax = plt.subplots(figsize=(8,5))
for entry in rows:
    ax.plot(entry['A_semantic']['onset'], entry['N'], 'o', color='navy', label='semantic' if entry['N']==rows[0]['N'] else None)
    ax.plot(entry['B_vonMises']['onset'], entry['N'], 's', color='crimson', label='vonMises(same R0)' if entry['N']==rows[0]['N'] else None)
ax.set_yscale('log'); ax.set_ylabel('N'); ax.set_xlabel('onset K0 (R>0.5)')
ax.set_title('Matched-R0: multimodal vs unimodal synchronize identically (N-sweep)')
ax.legend(); ax.grid(alpha=0.3); fig.tight_layout()
f = os.path.join(here,'ecosystem_kuramoto9_matched_R0.png')
fig.savefig(f, dpi=130); print('saved', f)
