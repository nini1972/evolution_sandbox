#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Trajectory evidence: tencent 'frozen' cells (a=2.0,K0=5; a=1.8,K0=10) and
fast cell (a=1.4,K0=20): R(t) for 12 seeds each, showing algebraic escape to
R~0.8 well within T=100 even for the 'frozen' cells."""
import os, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

rng = np.random.default_rng(20260910)
OUT = os.path.dirname(os.path.abspath(__file__))
N = 150; DT = 0.02; NSEEDS = 12
TMAX = 40.0
cells = [(2.0, 5), (1.8, 10), (1.4, 20)]
omegas = rng.uniform(-1, 1, N)
inits = rng.uniform(0, 2*np.pi, (NSEEDS, N))

def traj(alpha, K0):
    theta = inits.copy()
    nsteps = int(TMAX/DT)
    RT = np.zeros((NSEEDS, nsteps))
    for it in range(nsteps):
        z = np.mean(np.exp(1j*theta), axis=1)
        R = np.abs(z)
        RT[:, it] = R
        K = K0 * R**alpha
        ph = np.angle(z)
        dtheta = omegas[None, :] + K[:, None]*np.sin(ph[:, None] - theta)
        theta = theta + DT*dtheta
    return RT

fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.6), sharey=True)
tt = np.arange(int(TMAX/DT))*DT
for ax, (a, k) in zip(axes, cells):
    RT = traj(a, k)
    for s in range(NSEEDS):
        ax.plot(tt, RT[s], lw=1.0, alpha=0.55,
                color='navy' if RT[s, -1] > 0.8 else 'crimson')
    ax.axhline(0.8, color='k', ls='--', lw=1)
    ax.axvspan(0, 6.45, color='gold', alpha=0.12)
    ax.text(3.2, 0.86, 'horizon 6.45', rotation=0, fontsize=8, color='darkgoldenrod')
    ax.set_xlabel('time $t$')
    Pmap = {(2.0, 5): 0.00, (1.8, 10): 0.25, (1.4, 20): 1.00}
    ax.set_title('$\\alpha$=%.1f, $K_0$=%d\n(tencent P(lock)=%.2f)' %
                 (a, k, Pmap[(a, k)]))
    ax.grid(alpha=0.3)
axes[0].set_ylabel('order parameter $R(t)$')
fig.suptitle('No barrier, no eternal "frozen" state: algebraic escape from the natural seed\n'
             '(N=150, $\\sigma$=0, 12 seeds per cell; dashed = lock threshold R=0.8)',
             fontsize=12)
fig.tight_layout(rect=[0, 0, 1, 0.9])
fig.savefig(os.path.join(OUT, 'alpha_frozen_cells_trajectories.png'), dpi=140)
print("saved alpha_frozen_cells_trajectories.png")