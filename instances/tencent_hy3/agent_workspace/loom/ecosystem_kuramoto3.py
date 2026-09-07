'''Finite-size scaling of Treaty-001 explosive synchronization.
Does the ratified bistability band [1.40,1.82] appear for small N?
Exact O(N) all-to-all Kuramoto with feedback K=K0*R**alpha.'''
import os, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def order_param(th):
    z = np.mean(np.exp(1j * np.array(th)))
    return abs(z), np.angle(z)

def kuramoto_sweep(thetas0, K0s, alpha=0.6, dt=0.02, steps_per=30, sigma=0.008, seed=0):
    rng = np.random.RandomState(seed)
    th = np.array(thetas0, dtype=float)
    N = len(th)
    Rs = []
    for K0 in K0s:
        R, psi = order_param(th)
        for _ in range(steps_per):
            dth = N * R * np.sin(psi - th)   # exact all-to-all identity
            K = K0 * (R ** alpha)
            th = th + dt * ((K / N) * dth) + math.sqrt(dt) * sigma * rng.randn(N)
            R, psi = order_param(th)
        Rs.append(R)
    return np.array(Rs)

try:
    trapz = np.trapezoid
except AttributeError:
    trapz = np.trapz

Kgrid = np.linspace(0.2, 3.0, 44)
Kup, Kdown = Kgrid, Kgrid[::-1]
Ns = [10, 15, 25, 40, 60, 100, 150, 200, 300, 400]
rows = []
for N in Ns:
    rng = np.random.RandomState(N + 99)
    th_rand = rng.uniform(0, 2 * math.pi, N)
    R0, _ = order_param(th_rand)
    Rup = kuramoto_sweep(th_rand, Kup, seed=N + 1)
    Rdown = kuramoto_sweep(th_rand, Kdown, seed=N + 2)
    area = float(trapz(Rup - Rdown, Kup))
    idx = np.where(Rup > 0.5)[0]
    kc = float(Kup[idx[0]]) if len(idx) else float('nan')
    rows.append({'N': N, 'R0': float(R0), 'Rmax_up': float(Rup.max()),
                 'Rmax_down': float(Rdown.max()), 'hyst_area': area, 'kc_Rhalf': kc})
    print('N=%4d R0=%.3f Rmax_up=%.3f Rmax_down=%.3f hyst_area=%.4f kc=%.2f' %
          (N, R0, Rup.max(), Rdown.max(), area, kc))

import json
json.dump(rows, open(os.path.join(os.path.dirname(__file__), 'ecosystem_kuramoto3_result.json'), 'w'), indent=2)

# Plot: hysteresis area vs N (log x) and Kc vs N
fig, ax = plt.subplots(1, 2, figsize=(13, 5))
ax[0].semilogx([r['N'] for r in rows], [r['hyst_area'] for r in rows], 'o-', color='crimson')
ax[0].axhline(0.05, color='k', ls=':', label='bistability onset ~0.05')
ax[0].set_xlabel('Population N'); ax[0].set_ylabel('Hysteresis loop area')
ax[0].set_title('Finite-size gating of Treaty-001 explosive sync')
ax[0].legend(fontsize=8); ax[0].grid(alpha=0.3)
kc = [r['kc_Rhalf'] for r in rows]
ax[1].semilogx([r['N'] for r in rows], kc, 's-', color='navy', label='Kc (R=0.5 up)')
ax[1].axhspan(1.40, 1.82, color='green', alpha=0.15, label='Ratified band')
ax[1].set_xlabel('Population N'); ax[1].set_ylabel('Critical coupling Kc')
ax[1].set_title('Critical coupling vs N (NaN = no transition by K0=3)')
ax[1].legend(fontsize=8); ax[1].grid(alpha=0.3)
fig.tight_layout()
out = os.path.join(os.path.dirname(__file__), 'ecosystem_kuramoto3.png')
fig.savefig(out, dpi=130)
print('saved', out)
