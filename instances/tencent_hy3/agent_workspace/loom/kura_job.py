# Per-alpha job; appends onset to results JSON (lightweight, <15s each).
import os, sys, json, math
import numpy as np

def batch(N, gamma, K0, alpha, nseed, dt=0.01, nsteps=900, seed=0):
    rng = np.random.RandomState(seed)
    Rvals = []
    for s in range(nseed):
        om = rng.uniform(-gamma, gamma, N)
        th = rng.uniform(0, 2*math.pi, N)
        for t in range(nsteps):
            z = np.mean(np.exp(1j*th)); R = abs(z); psi = np.angle(z)
            th = th + dt*(om + (K0*R**alpha)*np.sin(psi-th))
        Rm = []
        for t in range(250):
            z = np.mean(np.exp(1j*th)); R = abs(z); psi = np.angle(z)
            th = th + dt*(om + (K0*R**alpha)*np.sin(psi-th))
            Rm.append(abs(np.mean(np.exp(1j*th))))
        Rvals.append(np.mean(Rm))
    return np.mean(Rvals)

N = 200; gamma = 1.0
alpha = float(sys.argv[1])
Kgrid = np.linspace(0.4, 9.0, 30)
NSEED = 2
here = os.path.dirname(os.path.abspath(__file__))
rj = os.path.join(here, 'ecosystem_kuramoto12_result.json')
res = json.load(open(rj)) if os.path.exists(rj) else {'N': N, 'gamma': gamma,
      'Kgrid': Kgrid.tolist(), 'Kc_theory': 4*gamma/math.pi, 'res': []}
rngN = np.random.RandomState(17)
Rmat = np.zeros(len(Kgrid))
for k, K0 in enumerate(Kgrid):
    Rmat[k] = batch(N, gamma, K0, alpha, NSEED, seed=rngN.randint(10**9))
idx = np.where(Rmat > 0.5)[0]
onset = float(Kgrid[idx[0]]) if len(idx) else float('nan')
res['res'].append({'alpha': alpha, 'onset': onset})
json.dump(res, open(rj, 'w'), indent=2)
print('alpha=%+.2f  onset_K0=%.2f' % (alpha, onset))
