#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HYSTERESIS / IGNITION-BARRIER PROBE
===================================
For the reflexive Kuramoto law, test whether high-alpha regimes have an
UNREACHABLE sync branch (bistability) or truly NO sync state.

Protocol: for each (alpha, K0):
  * LOW-R start: random phases (R0 ~ 1/sqrt(N))
  * HIGH-R start: phases clustered with R0 = 0.85
If R*(high-start) >> R*(low-start) at the same (alpha,K0), the system is
bistable and the sync branch is ignition-suppressed from disorder.
"""
import os, json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = os.path.dirname(os.path.abspath(__file__))

def integrate(th0, K0, alpha, sigma, dt=0.02, nsteps=400, rng=None):
    th = np.array(th0, dtype=float); N = len(th)
    sd = math.sqrt(dt)
    if rng is None: rng = np.random.RandomState(42)
    for _ in range(nsteps):
        z = np.mean(np.exp(1j * th))
        R = abs(z)
        dth = np.imag(np.exp(-1j * th) * z)
        K = K0 * (R ** alpha)
        th = th + dt * (K * dth) + sd * sigma * rng.randn(N)
    return abs(np.mean(np.exp(1j * th)))

def cluster_phases(R0, N, rng):
    """Phases centered at 0 with order R0 (Gaussian concentration)."""
    # draw from von Mises-ish: gaussian on circle
    k = -np.log(max(R0, 1e-3) + 1e-9) if R0 < 1 else 50.0
    # simple: gaussian sigma tuned to R0
    sigma_ph = np.sqrt(-2 * np.log(max(R0, 1e-4)))
    return rng.randn(N) * sigma_ph

def run(alpha, K0, sigma=0.008, N=200, seeds=5):
    lo = []; hi = []
    for s in range(seeds):
        rng = np.random.RandomState(100 * s + 7)
        th_lo = rng.uniform(0, 2 * math.pi, N)
        th_hi = cluster_phases(0.85, N, rng)
        lo.append(integrate(th_lo, K0, alpha, sigma, rng=rng))
        hi.append(integrate(th_hi, K0, alpha, sigma, rng=rng))
    return float(np.mean(lo)), float(np.mean(hi))

ALPHAS = [0.6, 0.8, 1.0, 1.2, 1.5, 2.0]
KGRID = np.linspace(0.5, 4.0, 15)
res = {"alphas": ALPHAS, "kgrid": list(KGRID), "R_low": [], "R_high": []}
for a in ALPHAS:
    rl = []; rh = []
    for K0 in KGRID:
        lo, hi = run(a, K0)
        rl.append(lo); rh.append(hi)
    res["R_low"].append(rl); res["R_high"].append(rh)
    print("alpha=%.1f  Rlow@K0=4: %.3f   Rhigh@K0=4: %.3f   | Rhigh-Rlow max: %.3f"
          % (a, rl[-1], rh[-1], max(np.array(rh) - np.array(rl))))

with open(os.path.join(OUT, "alpha_hysteresis.json"), "w") as f:
    json.dump(res, f, indent=2)

fig, axes = plt.subplots(2, 3, figsize=(14, 8), sharey=True)
for idx, a in enumerate(ALPHAS):
    ax = axes[idx // 3][idx % 3]
    ax.plot(KGRID, res["R_low"][idx], 'o-', color='crimson', ms=4, label='from disorder (R0~0)')
    ax.plot(KGRID, res["R_high"][idx], 's-', color='navy', ms=4, label='from cluster (R0=0.85)')
    ax.set_title(r'$\alpha=%.1f$' % a, fontsize=12)
    ax.set_xlabel(r'$K_0$')
    if idx % 3 == 0: ax.set_ylabel(r'$R^*$')
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7)
fig.suptitle('Ignition-barrier probe: low-R vs high-R initial conditions', fontsize=14)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "alpha_hysteresis.png"), dpi=140)
print("saved alpha_hysteresis.png")