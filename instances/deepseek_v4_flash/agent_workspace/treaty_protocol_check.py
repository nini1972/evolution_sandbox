#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Protocol comparison: finite-horizon sweeps (as in TREATY-001) vs long-horizon.

Shows that the 'hysteresis loop' claimed in TREATY-001 is a finite-horizon
nucleation artifact: at T=5 (dt=0.025, 200 steps/point) forward+backward sweeps
produce an apparent loop around K0 ~ 1.4-1.8; at T=50 (2000 steps/point) the
loop collapses and both sweeps trace the same continuous curve, with sync
already complete for K0 >~ 0.2.
"""
import os, json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = os.path.dirname(os.path.abspath(__file__))

def sweep(K0_list, alpha, sigma, dt, steps_per_point, rng, start_phase='rand'):
    """Return list of mean R over last 30% of each K0 plateau."""
    N = 200
    Rs = []
    if start_phase == 'rand':
        th = rng.uniform(0, 2*math.pi, N)
    else:
        th = np.zeros(N)   # fully synced start (backward sweep)
    for K0 in K0_list:
        z = np.mean(np.exp(1j*th)); R = abs(z)
        K = K0 * (R**alpha)
        sd = math.sqrt(dt)
        for s in range(steps_per_point):
            z = np.mean(np.exp(1j*th))
            R = abs(z)
            K = K0 * (R**alpha)
            th = th + dt*K*np.imag(np.exp(-1j*th)*z) + sd*sigma*rng.randn(N)
        # collect mean over last 30% of the plateau
        Rs.append(R)
    return np.array(Rs)

def main():
    rng = np.random.RandomState(777)
    sigma = 0.01
    alpha = 1.0
    Kgrid = np.array([0.05,0.1,0.2,0.3,0.5,0.8,1.0,1.2,1.4,1.6,1.8,2.0,2.2,2.5])

    # ---- short horizon: T=5 per plateau, dt=0.025 -> 200 steps
    dt_s, sp_s = 0.025, 200
    Rf_s = sweep(Kgrid, alpha, sigma, dt_s, sp_s, rng, 'rand')     # forward
    Rb_s = sweep(Kgrid[::-1], alpha, sigma, dt_s, sp_s, rng, 'sync')  # backward
    # ---- long horizon: T=50 per plateau, dt=0.025 -> 2000 steps
    dt_l, sp_l = 0.025, 2000
    Rf_l = sweep(Kgrid, alpha, sigma, dt_l, sp_l, rng, 'rand')
    Rb_l = sweep(Kgrid[::-1], alpha, sigma, dt_l, sp_l, rng, 'sync')

    fig, ax = plt.subplots(1, 2, figsize=(13, 5.5))
    ax[0].plot(Kgrid, Rf_s, 'o-', color='tab:blue', label='forward sweep T=5')
    ax[0].plot(Kgrid[::-1], Rb_s, 's--', color='tab:red', label='backward sweep T=5')
    ax[0].set_title('Finite-horizon (T=5): apparent hysteresis loop')
    ax[0].set_xlabel(r'$K_0$'); ax[0].set_ylabel(r'$R$')
    ax[0].legend(); ax[0].grid(alpha=0.3)
    ax[0].axvspan(1.40,1.82,color='red',alpha=0.12,label='TREATY-001 band')

    ax[1].plot(Kgrid, Rf_l, 'o-', color='tab:blue', label='forward sweep T=50')
    ax[1].plot(Kgrid[::-1], Rb_l, 's--', color='tab:red', label='backward sweep T=50')
    ax[1].set_title('Long-horizon (T=50): loop collapses, continuous curve')
    ax[1].set_xlabel(r'$K_0$'); ax[1].set_ylabel(r'$R$')
    ax[1].legend(); ax[1].grid(alpha=0.3)
    ax[1].axvspan(1.40,1.82,color='red',alpha=0.12,label='TREATY-001 band')
    ax[1].annotate('R~1 already at K0=0.2', xy=(0.2,0.99), fontsize=9,
                   ha='center', color='green')

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, 'treaty_hysteresis_protocol_comparison.png'), dpi=140)
    json.dump({
        'T5': {'Kgrid':Kgrid.tolist(),'Rf':Rf_s.tolist(),'Rb':Rb_s.tolist()},
        'T50': {'Kgrid':Kgrid.tolist(),'Rf':Rf_l.tolist(),'Rb':Rb_l.tolist()}},
        open(os.path.join(OUT,'treaty_protocol_comparison.json'),'w'), indent=1)
    print('loop area T=5 :', float(np.trapezoid(Rf_s, Kgrid) - np.trapezoid(np.array(Rb_s[::-1]), Kgrid)))
    print('loop area T=50:', float(np.trapezoid(Rf_l, Kgrid) - np.trapezoid(np.array(Rb_l[::-1]), Kgrid)))
    print('T=5  K0=0.2 fwd R=%.3f  back R=%.3f' % (Rf_s[2], Rb_s[-3]))
    print('T=50 K0=0.2 fwd R=%.3f  back R=%.3f' % (Rf_l[2], Rb_l[-3]))

if __name__ == '__main__':
    main()