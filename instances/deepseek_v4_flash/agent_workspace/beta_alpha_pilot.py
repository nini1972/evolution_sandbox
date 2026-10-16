#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pilot: does escape-time scaling exponent beta depend on feedback exponent alpha?
Hypothesis: with multiplicative feedback K = K0 R^alpha and finite-size self-noise,
  t_esc(N) ~ N^beta(alpha),   beta(0)=0.5 (OA), increasing toward 1 as alpha grows,
  with a nucleation barrier when R0 < R_nuc.
Quick local MC validation before the big World C sweep.
"""
import os, json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = os.path.dirname(os.path.abspath(__file__))

def escape_time_mc(K0, alpha, N, dt=0.02, Tmax=None, seed=0, Rthr=0.8, sigma=0.0):
    rng = np.random.RandomState(seed)
    th = rng.uniform(0, 2*math.pi, N)
    sd = math.sqrt(dt)
    steps = int(Tmax / dt)
    for s in range(steps):
        z = np.mean(np.exp(1j*th))
        R = abs(z)
        if R > Rthr:
            return s*dt
        K = K0 * (R ** alpha)
        th = th + dt*K*np.imag(np.exp(-1j*th)*z) + sd*sigma*rng.randn(N)
    return np.inf

def t_esc_oa(K0, alpha, R0, Rf=0.8, sigma=0.0, npts=4000):
    """OA slow-manifold integral with explicit noise floor sigma."""
    R = np.geomspace(R0, Rf, npts)
    f = (K0/2.0)*R**(alpha+1.0)*(1.0 - R*R) - (sigma**2/2.0)*R
    f = np.clip(f, 1e-12, None)
    return float(np.trapezoid(1.0/f, R))

def main():
    K0 = 5.0
    alphas = [0.0, 0.5, 1.0, 1.5, 2.0]
    Ns = [100, 200, 400, 800]
    sigma = 0.0   # deterministic self-noise only (finite-size)
    Rthr = 0.8

    # OA horizon predictions (R0 = 1/sqrt(N), pure deterministic => use small sigma floor for the integral)
    print("=== OA integral predictions (sigma_floor=0.02, K0=5) ===")
    for a in alphas:
        row = []
        for N in Ns:
            R0 = 1.0/math.sqrt(N)
            row.append(t_esc_oa(K0, a, R0, sigma=0.02))
        print(" alpha=%.1f: " % a + "  ".join("N=%d:%.0f" % (N, t) for N, t in zip(Ns, row)))

    print("\n=== MC check (sigma=0, K0=5, Tmax=600, 12 reps) ===")
    mc = {}
    for a in [0.0, 1.0, 2.0]:
        for N in Ns:
            Tmax = 600.0
            ts = [escape_time_mc(K0, a, N, Tmax=Tmax, seed=1000+se) for se in range(12)]
            fin = [t for t in ts if np.isfinite(t)]
            med = np.median(fin) if fin else np.inf
            frac = len(fin)/len(ts)
            mc[(a, N)] = (med, frac)
            print(" alpha=%.1f N=%4d: med=%8.1f  frac_esc=%.2f" % (a, N, med, frac))

    json.dump({'mc': {("%.1f" % a, N): (med, frac) for (a, N), (med, frac) in mc.items()}},
              open(os.path.join(OUT, 'beta_alpha_pilot.json'), 'w'), indent=1)

    # plot MC medians vs N for each alpha (log-log slope = beta)
    fig, ax = plt.subplots(figsize=(8, 6))
    for a in [0.0, 1.0, 2.0]:
        xs = []; ys = []
        for N in Ns:
            med, frac = mc[(a, N)]
            if np.isfinite(med) and frac > 0.4:
                xs.append(N); ys.append(med)
        if len(xs) >= 3:
            b = np.polyfit(np.log(xs), np.log(ys), 1)[0]
            ax.plot(xs, ys, 'o-', label=r'$\alpha$=%.1f   $\beta$=%.2f' % (a, b))
        else:
            ax.plot(xs, ys, 'o-', label=r'$\alpha$=%.1f (censored)' % a)
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlabel('N'); ax.set_ylabel(r'median $t_{esc}$')
    ax.set_title('Pilot: escape-time scaling exponent vs feedback exponent alpha\n'
                 'Kuramoto + multiplicative feedback K=K0 R^alpha, sigma=0, K0=5, Tmax=600')
    ax.grid(alpha=0.3, which='both'); ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, 'beta_alpha_pilot.png'), dpi=140)
    print("saved beta_alpha_pilot.png")

if __name__ == '__main__':
    main()
