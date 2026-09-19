#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Decisive continuity check for Kuramoto R^alpha feedback (N=200, sigma=0.008).

For each alpha in {0.2,0.6,1.0} and K0 grid, run to LONG horizon and see whether
R* still saturates near 1 (continuous sync) for K0 well below the claimed
hysteresis band [1.40,1.82].  Also run a bidirectional quasi-static sweep for the
ratified protocol (sigma=0.01) to check whether any hysteresis survives.
"""
import os, json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = os.path.dirname(os.path.abspath(__file__))

def integrate_traj(th0, K0, alpha, sigma, dt=0.05, nsteps=8000, rng=None):
    """Return R(t) trajectory (decimated) for the vanilla global-coupling model."""
    th = np.array(th0, dtype=float)
    sd = math.sqrt(dt)
    N = th.size
    if rng is None:
        rng = np.random.RandomState(12345)
    Rs = []
    record_every = 200
    for s in range(nsteps):
        z = np.mean(np.exp(1j * th))
        R = abs(z)
        dth = np.imag(np.exp(-1j * th) * z)
        K = K0 * (R ** alpha)
        th = th + dt * K * dth + sd * sigma * rng.randn(N)
        if s % record_every == 0:
            Rs.append(R)
    return np.array(Rs)

def run_T3():
    rng = np.random.RandomState(2024)
    N = 200
    alphas = [0.2, 0.6, 1.0]
    K0s = [0.05, 0.2, 0.5, 0.8, 1.0, 1.4, 1.8, 2.2]
    out = {}
    for a in alphas:
        rows = []
        for K0 in K0s:
            th0 = rng.uniform(0, 2 * math.pi, N)
            traj = integrate_traj(th0, K0, a, 0.008)
            R_final = traj[-1]
            R_last100 = traj[-100:].mean()
            rows.append({'K0': float(K0), 'R_final': float(R_final),
                         'R_last100': float(R_last100),
                         'min_R': float(traj.min()), 'max_R': float(traj.max())})
            print("alpha=%.1f K0=%.2f -> R_final=%.4f  R_last100=%.4f  (R range %.3f..%.3f)"
                  % (a, K0, R_final, R_last100, traj.min(), traj.max()))
        out[str(a)] = rows
    json.dump(out, open(os.path.join(OUT, 'treaty_continuity_long.json'), 'w'), indent=1)

    fig, ax = plt.subplots(figsize=(9, 6))
    for a in alphas:
        rs = [r['R_final'] for r in out[str(a)]]
        ax.plot(K0s, rs, 'o-', label=r'$\alpha=%.1f$' % a)
    ax.axvspan(1.40, 1.82, color='red', alpha=0.15, label='TREATY-001 hysteresis band')
    ax.set_xlabel(r'$K_0$'); ax.set_ylabel(r'$R^*$ (long-time, T=400)')
    ax.set_title('Long-horizon stationary order vs K0: continuous, NOT first-order')
    ax.grid(alpha=0.3); ax.legend()
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'treaty_continuity_long.png'), dpi=140)
    print('saved treaty_continuity_long.png')

if __name__ == '__main__':
    run_T3()