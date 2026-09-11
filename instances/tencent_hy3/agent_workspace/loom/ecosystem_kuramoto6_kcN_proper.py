# Re-derive finite-size Kc(N) with PROPER RESTART at each K0 (corrects the
# cumulative-sweep method used in kuramoto4 / dossier-kuramoto1).
# Uses random uniform initial phases (matches dossier). Confirms whether the
# transmitted law Kc(N)=0.496*N^0.235 survives correct bifurcation protocol.
import os, math, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def order(th):
    z = np.mean(np.exp(1j * np.array(th)))
    return abs(z), np.angle(z)

def steady_rand(N, K0, alpha=0.6, sigma=0.0, dt=0.02, nsteps=500, seed=0):
    rng = np.random.RandomState(seed)
    th = rng.uniform(0, 2 * math.pi, N)
    for _ in range(nsteps):
        R, psi = order(th)
        dth = N * R * np.sin(psi - th)
        K = K0 * (R ** alpha)
        th = th + dt * ((K / N) * dth) + math.sqrt(dt) * sigma * rng.randn(N)
    return order(th)[0]

Kgrid = np.linspace(0.1, 2.5, 49)
Ns = [15, 30, 60, 100, 150, 200, 300]
SEED = 8
rows = []
for N in Ns:
    rngN = np.random.RandomState(123 + N)
    onsets = []
    for sd in range(SEED):
        RbyK = [steady_rand(N, K0, seed=rngN.randint(10**9)) for K0 in Kgrid]
        RbyK = np.array(RbyK)
        idx = np.where(RbyK > 0.5)[0]
        if len(idx):
            onsets.append(float(Kgrid[idx[0]]))
    rows.append({'N': N, 'kc_mean': float(np.mean(onsets)),
                 'kc_std': float(np.std(onsets)), 'n_rep': len(onsets)})
    print('N=%4d  Kc_proper=%.3f +/- %.3f (n=%d)' % (
        N, rows[-1]['kc_mean'], rows[-1]['kc_std'], rows[-1]['n_rep']))

# Fit Kc = a * N**b
Ns_ok = np.array([r['N'] for r in rows])
Kcs = np.array([r['kc_mean'] for r in rows])
b, ln_a = np.polyfit(np.log(Ns_ok), np.log(Kcs), 1)
a = np.exp(ln_a)
print('FIT: Kc(N) = %.4f * N**%.3f' % (a, b))
for r in rows:
    r['kc_fit'] = float(a * (r['N'] ** b))

here = os.path.dirname(os.path.abspath(__file__))
out = {'rows': rows, 'fit_a': float(a), 'fit_b': float(b)}
json.dump(out, open(os.path.join(here, 'ecosystem_kuramoto6_result.json'), 'w'), indent=2)

fig, ax = plt.subplots(figsize=(8, 5.5))
ax.errorbar(Ns_ok, Kcs, yerr=[r['kc_std'] for r in rows], fmt='o', color='navy',
            capsize=3, label='proper-restart Kc (R=0.5)')
ax.plot(Ns_ok, [r['kc_fit'] for r in rows], '-', color='crimson',
        label='fit %.3f*N^%.3f' % (a, b))
ax.axhline(1.40, ls=':', color='green', label='Treaty-001 band lower=1.40')
ax.set_xscale('log'); ax.set_yscale('log')
ax.set_xlabel('Population N'); ax.set_ylabel('Critical coupling Kc')
ax.set_title('PROPER finite-size scaling of Treaty-001 explosive-sync onset')
ax.legend(fontsize=9); ax.grid(alpha=0.3)
fig.tight_layout()
f = os.path.join(here, 'ecosystem_kuramoto6_kcN_proper.png')
fig.savefig(f, dpi=130)
print('saved', f)
