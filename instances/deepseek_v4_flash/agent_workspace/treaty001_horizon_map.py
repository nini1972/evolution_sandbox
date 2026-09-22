#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Decisive test of TREATY-001 under RATIFIED parameters (alpha=0.6, sigma=0.008).

Shows: t_esc(K0) is a smooth C(alpha,R0)/K0 curve with NO divergent critical point,
so the 'explosive critical band [1.40,1.82]' is an observation-horizon cross-section,
not an intrinsic bifurcation.  Second axis: K_app(T) = C/T law.
"""
import os, json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = os.path.dirname(os.path.abspath(__file__))

def t_esc_integral(K0, sigma, alpha, R0, Rf=0.8, npts=4000):
    """t_esc = int_{R0}^{Rf} dR / f(R);  f = OA slow-manifold drift."""
    R = np.geomspace(R0, Rf, npts)
    f = (K0/2.0)*R**(alpha+1)*(1.0 - R*R) - (sigma**2/2.0)*R
    f = np.clip(f, 1e-14, None)
    return float(np.trapezoid(1.0/f, R))

def t_esc_mc(K0, sigma, alpha=0.6, N=200, dt=0.025, Tmax=300.0, seed=0, Rthr=0.8):
    rng = np.random.RandomState(seed)
    th = rng.uniform(0, 2*math.pi, N)
    sd = math.sqrt(dt)
    nsteps = int(Tmax / dt)
    for s in range(nsteps):
        z = np.mean(np.exp(1j*th)); R = abs(z)
        if R > Rthr: return s*dt
        K = K0 * (R ** alpha)
        th = th + dt*K*np.imag(np.exp(-1j*th)*z) + sd*sigma*rng.randn(N)
    return np.inf

def main():
    ALPHA, SIG = 0.6, 0.008          # RATIFIED treaty parameters
    K0s = np.logspace(np.log10(0.03), np.log10(5.0), 40)
    res = {'alpha': ALPHA, 'sigma': SIG, 'runs': {}}

    print("=== OA escape-time integrals (ratified alpha=0.6, sigma=0.008) ===")
    curves = {}
    for R0 in (0.02, 0.05, 0.07, 0.10):     # init-radius protocol knob
        ts = np.array([t_esc_integral(K0, SIG, ALPHA, R0) for K0 in K0s])
        curves[R0] = ts
        res['runs']['R0=%.2f' % R0] = {'K0': K0s.tolist(), 't_esc': ts.tolist()}
        for K0v in (0.1, 0.2, 0.5, 1.0, 1.4, 2.0, 3.0):
            i = np.argmin(abs(K0s - K0v))
            print(" R0=%.2f K0=%.1f -> t_esc=%.1f" % (R0, K0s[i], ts[i]))

    print("\n=== stochastic confirmation (N=200, R0 from uniform random phases, Tmax=300) ===")
    mc_rows = []
    for K0 in (0.1, 0.3, 0.7, 1.2, 1.6, 2.2):
        ts = [t_esc_mc(K0, SIG, nsteps_check=True) for _ in ()]  # placeholder
    for K0 in (0.1, 0.3, 0.7, 1.2, 1.6, 2.2):
        ts = [t_esc_mc(K0, SIG, Tmax=300.0, seed=700+se) for se in range(8)]
        fin = [t for t in ts if np.isfinite(t)]
        med = np.median(fin) if fin else np.inf
        mc_rows.append((K0, med, len(fin)/len(ts)))
        print(" K0=%.1f: median=%.0f  frac-in-300=%.2f" % (K0, med, len(fin)/len(ts)))

    json.dump({**res, 'stochastic': [{'K0': k, 'median': m, 'frac': f} for k, m, f in mc_rows]},
              open(os.path.join(OUT, 'horizon_map.json'), 'w'), indent=1)

    # ---- Figure: two panels ----
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    # Left: t_esc(K0) curves for several R0, treaty band + horizons
    colors = {0.02:'tab:blue', 0.05:'tab:green', 0.07:'tab:orange', 0.10:'tab:red'}
    for R0, ts in curves.items():
        ax1.plot(K0s, ts, '-', lw=1.6, color=colors[R0], label=r'$R_0$=%.2f' % R0)
    ax1.axvspan(1.40, 1.82, color='crimson', alpha=0.15)
    ax1.text(1.60, 300, 'TREATY-001\n"critical band"', ha='center', fontsize=9, color='crimson')
    for T in (5, 50, 400):
        ax1.axhline(T, color='grey', ls=':', lw=1)
    ax1.text(2.6, 5.5, 'T=5', fontsize=8, color='grey')
    ax1.text(2.6, 55, 'T=50', fontsize=8, color='grey')
    ax1.text(2.6, 440, 'T=400', fontsize=8, color='grey')
    ax1.set_xscale('log'); ax1.set_yscale('log')
    ax1.set_xlim(0.03, 5.0); ax1.set_ylim(3, 2000)
    ax1.set_xlabel(r'$K_0$'); ax1.set_ylabel(r'$t_{esc}$ (OA drift $R_0\!\to\!0.8$)')
    ax1.set_title(r'No divergence: $t_{esc}=C(\alpha,R_0)/K_0$  ($\alpha$=0.6, $\sigma$=0.008)')
    ax1.grid(alpha=0.3, which='both'); ax1.legend(fontsize=8)

    # Right: apparent critical coupling vs observation horizon (K_app = C/T)
    R0_ref = 0.07
    C = np.array([t_esc_integral(1.0, SIG, ALPHA, R0_ref)])[0]   # = integral at K0=1 = C
    Ts = np.logspace(np.log10(2), np.log10(800), 80)
    K_app = C / Ts
    ax2.plot(Ts, K_app, 'k-', lw=2, label=r'$K_{app}(T)=C/T$,  $C$=%.1f' % C)
    ax2.axhspan(1.40, 1.82, color='crimson', alpha=0.15)
    ax2.text(500, 1.55, 'TREATY-001 band', fontsize=9, color='crimson', ha='center')
    # where does the band map to in T?
    T_low, T_high = C/1.82, C/1.40
    ax2.axvspan(T_low, T_high, color='tab:orange', alpha=0.20)
    ax2.text(T_low*1.1, 6, 'T≈%.0f–%.0f\n(protocol dwell)' % (T_low, T_high),
             fontsize=8, color='tab:orange')
    ax2.plot([T_high, T_high], [1.40, 1.82], 'o', color='crimson', ms=5)
    ax2.set_xscale('log'); ax2.set_yscale('log')
    ax2.set_xlabel(r'observation horizon $T$'); ax2.set_ylabel(r'apparent $K_{app}$ where escape seen')
    ax2.set_title('The "critical coupling" is a running clock:\n$K_{app}(T)\propto 1/T$')
    ax2.grid(alpha=0.3, which='both'); ax2.legend(fontsize=9)

    fig.suptitle('TREATY-001 under ratified parameters: escape is a smooth rate, horizon sets the "bifurcation"',
                 fontsize=12, y=1.00)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, 'treaty001_horizon_map.png'), dpi=140, bbox_inches='tight')
    print("saved treaty001_horizon_map.png")

if __name__ == '__main__':
    main()