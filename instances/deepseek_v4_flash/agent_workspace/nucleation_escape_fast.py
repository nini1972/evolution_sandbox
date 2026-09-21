#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Decisive escape-time test -- vectorized integral + small stochastic check.

Q: Is the TREATY-001 'critical band K0 ~ [1.4, 1.8]' an intrinsic barrier, or
is it set by the observation horizon of the experiment?

A (predicted): t_esc(K0) ~ (2/K0)(1/R0 - 1/0.8), a smooth O(1/K0) curve with
NO divergence.  The treaty band is merely where t_esc crosses the run horizon
T.  At T=200, K0=0.2 should synchronize (t_esc~190); at T=50 it should not --
so the same K0 is 'subcritical' in a short run and 'supercritical' in a long
run.  That is protocol dependence, not a bona fide phase transition.
"""
import os, json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = os.path.dirname(os.path.abspath(__file__))

def t_esc_integral(K0, sigma, alpha=1.0, R0=0.05, Rf=0.8):
    """t_esc = int_{R0}^{Rf} dR/f(R), f = OA slow-manifold drift (vectorized)."""
    R = np.geomspace(R0, Rf, 4000)
    f = (K0/2.0)*R**(alpha+1)*(1.0 - R*R) - (sigma**2/2.0)*R
    f = np.clip(f, 1e-12, None)
    return float(np.trapezoid(1.0/f, R))

def escape_time_mc(K0, sigma, alpha=1.0, N=200, dt=0.05, Tmax=200.0,
                   seed=0, Rthr=0.8):
    rng = np.random.RandomState(seed)
    th = rng.uniform(0, 2*math.pi, N)
    sd = math.sqrt(dt)
    nsteps = int(Tmax / dt)
    for s in range(nsteps):
        z = np.mean(np.exp(1j*th))
        R = abs(z)
        if R > Rthr:
            return s*dt
        K = K0 * (R ** alpha)
        th = th + dt*K*np.imag(np.exp(-1j*th)*z) + sd*sigma*rng.randn(N)
    return np.inf

def main():
    K0s = np.logspace(np.log10(0.05), np.log10(4.0), 30)
    sigmas = [0.004, 0.008, 0.01, 0.02]
    res = {}
    print("=== vectorized OA escape-time integrals (R0=0.05 -> 0.8) ===")
    for sig in sigmas:
        ts = [t_esc_integral(K0, sig) for K0 in K0s]
        res['s%.3f' % sig] = {'K0': K0s.tolist(), 't_esc': ts}
        idx = [np.argmin(abs(K0s - v)) for v in (0.1, 0.2, 0.6, 1.0, 1.4, 2.0)]
        print(" sigma=%.3f: " % sig + "  ".join(
            "K0=%.1f:%.0f" % (K0s[i], ts[i]) for i in idx))

    print("\n=== stochastic check (sigma=0.01, N=200, Tmax=200) ===")
    check_pts = [0.2, 0.6, 1.0, 1.4]
    mc = {}
    for K0 in check_pts:
        ts = [escape_time_mc(K0, 0.01, Tmax=200.0, seed=500+se) for se in range(6)]
        fin = [t for t in ts if np.isfinite(t)]
        med = np.median(fin) if fin else np.inf
        mc[K0] = {'ts': ts, 'median': med, 'frac': len(fin)/len(ts)}
        print(" K0=%.1f:  t_esc med=%.0f  frac escaped=%.2f" % (K0, med, mc[K0]['frac']))

    json.dump({'integral': {k: v for k, v in res.items()},
               'mc': {str(k): {kk: (vv if kk != 'ts' else [None if np.isinf(t) else t for t in vv])
                               for kk, vv in v.items()} for k, v in mc.items()}},
              open(os.path.join(OUT, 'nucleation_escape_fast.json'), 'w'), indent=1)

    fig, ax = plt.subplots(figsize=(10, 6))
    for sig in sigmas:
        r = res['s%.3f' % sig]
        ax.plot(r['K0'], r['t_esc'], 'o-', ms=4, label=r'$\sigma$=%.3f' % sig)
    ax.plot(K0s, (2.0/K0s)*(1.0/0.05 - 1.0/0.8), 'k--', lw=1.2,
            label=r'$t_{free}=2(1/R_0-1/0.8)/K_0$')
    # treaty band
    ax.axvspan(1.40, 1.82, color='crimson', alpha=0.15)
    ax.axhline(5, color='grey', ls=':', lw=1.2)
    ax.axhline(50, color='grey', ls=':', lw=1.2)
    ax.text(2.6, 7, 'T=5 run\n(treaty protocol)', fontsize=8, color='grey')
    ax.text(2.6, 70, 'T=50 run', fontsize=8, color='grey')
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlabel(r'$K_0$')
    ax.set_ylabel(r'$t_{esc}$  (OA slow-drift from R=0.05 to R=0.8)')
    ax.set_title('Escape time from incoherence: smooth 1/K0 curve, no divergent barrier\n'
                 'treaty "critical band" = where t_esc crosses the run horizon')
    ax.grid(alpha=0.3, which='both'); ax.legend()
    ax.set_xlim(0.05, 4.0)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, 'nucleation_escape_fast.png'), dpi=140)
    print("saved nucleation_escape_fast.png")

if __name__ == '__main__':
    main()