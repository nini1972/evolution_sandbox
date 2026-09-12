# PROPER finite-size Kc(N) with vectorized batched seeds (fast).
# Restart at each K0; random uniform inits. Re-derives Treaty-001 scaling
# under correct bifurcation protocol to check the dossier I already sent.
import os, math, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def batch_R(N, K0, nseed, alpha=0.6, sigma=0.0, dt=0.02, nsteps=250, seed=0):
    rng = np.random.RandomState(seed)
    th = rng.uniform(0, 2 * math.pi, size=(nseed, N))
    for _ in range(nsteps):
        z = np.mean(np.exp(1j * th), axis=1)
        R = np.abs(z); psi = np.angle(z)
        sin = np.sin(psi[:, None] - th)
        dth = N * R[:, None] * sin
        K = K0 * (R ** alpha)[:, None]
        th = th + dt * ((K / N) * dth) + math.sqrt(dt) * sigma * rng.randn(nseed, N)
    z = np.mean(np.exp(1j * th), axis=1)
    return np.abs(z)

Kgrid = np.linspace(0.1, 2.5, 37)
Ns = [15, 30, 60, 100, 150, 200, 300]
NSEED = 12
rows = []
for N in Ns:
    rngN = np.random.RandomState(123 + N)
    Rmat = np.zeros((NSEED, len(Kgrid)))
    for k, K0 in enumerate(Kgrid):
        Rmat[:, k] = batch_R(N, K0, NSEED, seed=rngN.randint(10**9))
    onsets = []
    for s in range(NSEED):
        idx = np.where(Rmat[s] > 0.5)[0]
        if len(idx):
            onsets.append(float(Kgrid[idx[0]]))
    rows.append({'n': N, 'kc_mean': float(np.mean(onsets)),
                 'kc_std': float(np.std(onsets)), 'n_rep': len(onsets)})
    print('N=%4d  Kc_proper=%.3f +/- %.3f (n=%d)' % (
        N, rows[-1]['kc_mean'], rows[-1]['kc_std'], rows[-1]['n_rep']))

Ns_ok = np.array([r['n'] for r in rows])
Kcs = np.array([r['kc_mean'] for r in rows])
b, ln_a = np.polyfit(np.log(Ns_ok), np.log(Kcs), 1)
a = np.exp(ln_a)
print('FIT: Kc(N) = %.4f * N**%.3f' % (a, b))
for r in rows:
    r['kc_fit'] = float(a * (r['n'] ** b))

here = os.path.dirname(os.path.abspath(__file__))
json.dump({'rows': rows, 'fit_a': float(a), 'fit_b': float(b)},
          open(os.path.join(here, 'ecosystem_kuramoto6_result.json'), 'w'), indent=2)

fig, ax = plt.subplots(figsize=(8, 5.5))
ax.errorbar(Ns_ok, Kcs, yerr=[r['kc_std'] for r in rows], fmt='o', color='navy',
            capsize=3, label='proper-restart Kc (R=0.5)')
ax.plot(Ns_ok, [r['kc_fit'] for r in rows], '-', color='crimson',
        label='fit %.3f*N^%.3f' % (a, b))
ax.axhline(1.40, ls=':', color='green', label='Treaty-001 band lower=1.40')
ax.set_xscale('log'); ax.set_yscale('log')
ax.set_xlabel('Population N'); ax.set_ylabel('Critical coupling Kc')
ax.set_title('PROPER finite-size scaling of Treaty-001 onset')
ax.legend(fontsize=9); ax.grid(alpha=0.3)
fig.tight_layout()
f = os.path.join(here, 'ecosystem_kuramoto6_kcN_proper.png')
fig.savefig(f, dpi=130)
print('saved', f)
