#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nucleation/escape-time measurement for Kuramoto K0*R^alpha feedback.

Measures the median time t_esc(K0, sigma) for a system started incoherently
(R~0) to escape to synchrony (R>0.8), across K0 and sigma, using N=200,
alpha=1.0, Euler-Maruyama dt=0.02, many seeds.

Hypothesis to test:
  H_artifact: t_esc ~ C(T)/K0 with mild sigma dependence -> apparent K_lock
              set by observation horizon, not intrinsic. "Bifurcation" at
              [1.40,1.82] is an artifact of short runs.
  H_intrinsic: t_esc diverges as K0 -> Kc(sigma) from above (true barrier).
"""
import os, json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = os.path.dirname(os.path.abspath(__file__))

def escape_time_seed(K0, sigma, alpha=1.0, N=200, dt=0.02, Tmax=2000.0,
                     seed=0, Rthr=0.8, rng=None):
    """Return escape time (T units) or np.inf. Vectorized over N oscillators."""
    if rng is None:
        rng = np.random.RandomState(seed)
    th = rng.uniform(0, 2*math.pi, N)
    sd = math.sqrt(dt)
    nsteps = int(Tmax / dt)
    R = abs(np.mean(np.exp(1j*th)))
    K = K0 * (R ** alpha)
    zi = np.exp(-1j*th)
    for s in range(nsteps):
        z = np.mean(np.exp(1j*th))
        R = abs(z)
        if R > Rthr:
            return s * dt
        K = K0 * (R ** alpha)
        th = th + dt*K*np.imag(np.exp(-1j*th)*z) + sd*sigma*rng.randn(N)
    return np.inf

def median_esc(K0, sigma, nseeds=12, Tmax=2000.0, Rthr=0.8):
    ts = []
    for sd_i in range(nseeds):
        t = escape_time_seed(K0, sigma, Rthr=Rthr, Tmax=Tmax, seed=1000+7*sd_i)
        ts.append(t)
    arr = np.array(ts)
    fin = arr[np.isfinite(arr)]
    if len(fin) == 0:
        return np.inf, 1.0, arr     # none escaped
    med = np.median(fin)
    frac = len(fin)/nseeds
    return med, frac, arr

def main():
    K0s = np.array([0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.2, 3.0])
    sigmas = [0.004, 0.008, 0.01, 0.02]
    Tmax = 2000.0
    nseeds = 10
    results = {}
    for sig in sigmas:
        out = {'K0': K0s.tolist(), 't_med': [], 'frac_esc': []}
        for K0 in K0s:
            med, frac, _ = median_esc(K0, sig, nseeds=nseeds, Tmax=Tmax)
            out['t_med'].append(med if np.isfinite(med) else None)
            out['frac_esc'].append(float(frac))
            print("sigma=%.3f K0=%.2f  t_med=%s  frac=%.2f"
                  % (sig, K0, ("%.1f" % med) if np.isfinite(med) else "inf", frac))
        results[str(sig)] = out
    json.dump(results, open(os.path.join(OUT, 'nucleation_escape_times.json'), 'w'), indent=1)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for sig in sigmas:
        out = results[str(sig)]
        ts = [np.inf if v is None else v for v in out['t_med']]
        axes[0].plot(out['K0'], ts, 'o-', label=r'$\sigma$=%.3f' % sig)
    axes[0].set_xscale('log'); axes[0].set_yscale('log')
    axes[0].set_xlabel(r'$K_0$'); axes[0].set_ylabel(r'median $t_{esc}$ (escape to R>0.8)')
    axes[0].set_title('Escape time vs K0 (N=200, alpha=1)')
    axes[0].grid(alpha=0.3, which='both'); axes[0].legend()
    # reference line t = 38/K0
    xx = np.array([0.05, 3.0])
    axes[0].plot(xx, 38/xx, 'k--', lw=1, label=r'$t=38/K_0$ (free-growth scaling)')

    for sig in sigmas:
        out = results[str(sig)]
        axes[1].plot(out['K0'], out['frac_esc'], 'o-', label=r'$\sigma$=%.3f' % sig)
    axes[1].set_xlabel(r'$K_0$'); axes[1].set_ylabel('escape fraction (T=2000)')
    axes[1].set_title('Escape fraction within T=2000')
    axes[1].grid(alpha=0.3); axes[1].legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, 'nucleation_escape_times.png'), dpi=140)
    print("saved nucleation_escape_times.png")

if __name__ == '__main__':
    main()