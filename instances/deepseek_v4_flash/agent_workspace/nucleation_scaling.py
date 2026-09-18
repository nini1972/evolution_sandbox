#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NUCLEATION-SCALING TEST OF THE REFLEXIVE KURAMOTO 'EXPLOSIVE TRANSITION'
=========================================================================
Canonical substrate (Treaty-001 alpha studies): zero-frequency noisy mean-field
   dtheta_i = K0 * R^alpha * R * sin(psi - theta_i) dt + sigma*sqrt(dt)*xi_i
   (EXACT solver as in alpha_hysteresis.py: no natural frequencies)

CLAIM UNDER TEST (previous files): the disorder-to-sync transition is explosive
and located at Kc in the ratified band [1.40, 1.82] for alpha=0.6.
CIRCULARITY NOTED: alpha_analysis.py computed Kc_fit AS mean(numeric_kmin * Gmax),
so the 'verified' ratio~1 was built into the fit.

ALTERNATIVE THEORY (this script): the substrate has NO true first-order
transition.  The genuine stationary bifurcation is the mean-field XY one at
Kc_stat = 2*sigma^2 (~1.3e-4 for sigma=0.008) -- continuous.  The apparent
'explosive' threshold at K0~1.4-1.8 is a FIXED-HORIZON NUCLEATION TRANSIENT:
with K_eff = K0*R^alpha and seed disorder R0 ~ 1/sqrt(N), the linearized
growth rate is lambda ~ K0*R0^alpha/2 = K0*N^{-alpha/2}/2, giving

    t_cross  ~  (2/K0) * N^{alpha/2} * ln(0.5/R0)

i.e. universal collapse I = t_cross*K0 / (2*ln(0.5*sqrt(N))*N^{alpha/2}) ~ 1.

TESTS:
  T1  t_cross scaling: I ~ const across (alpha, K0, N) -> nucleation law.
  T2  apparent Kc drifts with horizon T and system size N (transient,
      NOT a genuine bifurcation).  A true transition threshold is T- and
      N-independent in mean field.
  T3  long-time stationary state: R* -> 1 for any K0 >> 2*sigma^2, and
      matches von-Mises self-consistency R = I1(kappa)/I0(kappa),
      kappa = K0*R^{alpha+1}/sigma^2, with the ONLY bifurcation near 2*sigma^2.
"""
import os, json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.special import i0, i1

OUT = os.path.dirname(os.path.abspath(__file__))
SIGMA = 0.008
DT = 0.04

def step(th, K0, alpha, sigma, dt, rng):
    """Single canonical step (vectorized over seeds axis 0)."""
    z = np.mean(np.exp(1j * th), axis=1)          # (S,)
    R = np.abs(z)
    dth = np.imag(np.exp(-1j * th) * z[:, None])  # (S, N)
    K = K0 * (R ** alpha)
    th = th + dt * (K[:, None] * dth) + math.sqrt(dt) * sigma * rng.randn(*th.shape)
    return th, R

def run_cross(alpha, K0, N, seeds=8, Tmax=64.0, rng=None):
    """Time (in same units as dt) for mean order to first cross 0.5 from disorder."""
    if rng is None:
        rng = np.random.RandomState(1234 + int(alpha * 100) + int(K0 * 10) + N)
    th = rng.uniform(0, 2 * math.pi, (seeds, N))
    nsteps = int(Tmax / DT)
    R_prev = np.abs(np.mean(np.exp(1j * th), axis=1)).mean()
    t_prev = 0.0
    for s in range(1, nsteps + 1):
        th, R = step(th, K0, alpha, SIGMA, DT, rng)
        Rm = float(np.mean(R))
        if Rm >= 0.5:
            # linear interpolation between previous and current step
            frac = (0.5 - R_prev) / max(Rm - R_prev, 1e-12)
            return min(t_prev + DT * frac, Tmax)
        R_prev, t_prev = Rm, s * DT
    return float('nan')  # never crossed within horizon

def stationary_R(alpha, K0, N=200, seeds=6, T=800.0):
    """Long-time order from disorder seed (true stationary estimate)."""
    rng = np.random.RandomState(999 + N)
    th = rng.uniform(0, 2 * math.pi, (seeds, N))
    nsteps = int(T / DT)
    R_last = []
    for s in range(nsteps):
        th, R = step(th, K0, alpha, SIGMA, DT, rng)
    for _ in range(50):                      # average over tail
        th, R = step(th, K0, alpha, SIGMA, DT, rng)
        R_last.append(float(np.mean(R)))
    return float(np.mean(R_last))

def vonmises_selfconsistent(alpha, K0, sigma=SIGMA):
    """Solve R = I1(kappa)/I0(kappa), kappa = K0*R^{alpha+1}/sigma^2, R>0."""
    s2 = sigma * sigma
    R = 0.99
    for _ in range(200):
        k = K0 * (R ** (alpha + 1)) / s2
        Rnew = i1(k) / i0(k)
        R = 0.5 * R + 0.5 * Rnew
    return float(R)

# ------------------------------------------------------------------
print("=" * 74)
print("T1: universal nucleation collapse  I = t_cross*K0/(2 ln(0.5 sqrt N) N^(a/2))")
print("=" * 74)
ALPHAS = [0.2, 0.6, 1.0, 1.5]
K0S = [0.8, 1.2, 1.6, 2.2]
NS = [100, 200, 400]
rows = []
for a in ALPHAS:
    for K0 in K0S:
        for N in NS:
            tc = run_cross(a, K0, N)
            if math.isnan(tc):
                continue
            I = tc * K0 / (2.0 * math.log(0.5 * math.sqrt(N)) * (N ** (a / 2.0)))
            rows.append((a, K0, N, tc, I))
            print("alpha=%4.1f K0=%4.1f N=%3d  t_cross=%6.2f  I=%.3f" % (a, K0, N, tc, I))
Is = np.array([r[4] for r in rows])
print("-" * 74)
print("collapse I: mean=%.3f  median=%.3f  std=%.3f  min=%.3f  max=%.3f  (n=%d)"
      % (Is.mean(), np.median(Is), Is.std(), Is.min(), Is.max(), len(Is)))
per_alpha = {a: [r[4] for r in rows if r[0] == a] for a in ALPHAS}
for a, v in per_alpha.items():
    print("  alpha=%.1f: mean I=%.3f  std=%.3f  (n=%d)" % (a, np.mean(v), np.std(v), len(v)))

# ------------------------------------------------------------------
print()
print("=" * 74)
print("T2: apparent threshold Kc (R>0.5 onset) drifts with horizon T and N")
print("=" * 74)
def apparent_kc(alpha, T, N, Kgrid, seeds=8):
    """Smallest K0 whose disorder-seeded order after time T exceeds 0.5."""
    rng = np.random.RandomState(int(77 * T + N))
    prev = None
    for K0 in Kgrid:
        th = rng.uniform(0, 2 * math.pi, (seeds, N))
        nsteps = int(T / DT)
        for s in range(nsteps):
            th, R = step(th, K0, alpha, SIGMA, DT, rng)
        if float(np.mean(R)) > 0.5:
            return float(K0)
    return float('nan')

T2_alpha = 0.6
T2 = {}
for T in [4.0, 8.0, 16.0]:
    for N in [100, 400]:
        kc = apparent_kc(T2_alpha, T, N, np.linspace(0.4, 3.0, 27))
        T2[(T, N)] = kc
        print("alpha=0.6 N=%3d T=%5.0f  apparent Kc=%.3f" % (N, T, kc))

# ------------------------------------------------------------------
print()
print("=" * 74)
print("T3: true stationary state vs von-Mises self-consistency (Kc_stat=2*sigma^2)")
print("=" * 74)
T3 = {}
for a in [0.0, 0.6, 1.0]:
    for K0 in [0.05, 0.2, 1.0, 1.6, 2.5]:
        Rnum = stationary_R(a, K0)
        Ran = vonmises_selfconsistent(a, K0)
        T3[(a, K0)] = (Rnum, Ran)
        print("alpha=%3.1f K0=%5.2f  R_num(long-time)=%.4f  R_vonMises=%.4f"
              % (a, K0, Rnum, Ran))
print("Kc_stat(all alpha) = 2*sigma^2 =", 2 * SIGMA ** 2)

# ------------------------------------------------------------------
# FIGURES
# ------------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# Fig1: collapse I vs K0 for each (alpha, N)
ax = axes[0]
markers = ['o', 's', 'd']
for ai, a in enumerate(ALPHAS):
    for ni, N in enumerate(NS):
        sub = [(r[1], r[4]) for r in rows if r[0] == a and r[2] == N]
        if sub:
            x, y = zip(*sub)
            ax.plot(x, y, markers[ni], ms=5, label=r'$\alpha=%.1f$,$N=%d$' % (a, N))
ax.axhline(1.0, color='gray', ls='--', lw=1, label='theory I=1')
ax.axhline(np.mean(Is), color='crimson', ls=':', lw=1, label='mean I=%.2f' % np.mean(Is))
ax.set_xlabel(r'$K_0$')
ax.set_ylabel(r'$I = t_{cross}K_0/(2\ln(0.5\sqrt{N})N^{\alpha/2})$')
ax.set_title('T1: Universal nucleation collapse')
ax.set_ylim(0, 2.2)
ax.legend(fontsize=6, ncol=2); ax.grid(alpha=0.3)

# Fig2: apparent Kc vs horizon T at two N
ax = axes[1]
for N in [100, 400]:
    Ts = sorted([t for (t, n) in T2 if n == N])
    kcs = [T2[(t, N)] for t in Ts]
    ax.plot(Ts, kcs, 'o-', label='N=%d' % N)
ax.axhspan(1.40, 1.82, color='orange', alpha=0.2, label='ratified band')
ax.set_xlabel(r'horizon $T$'); ax.set_ylabel(r'apparent $K_c$ (R>0.5)')
ax.set_title('T2: Apparent threshold drifts with horizon')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

# Fig3: stationary R* vs K0, numeric vs von-Mises
ax = axes[2]
aa3 = sorted(set(k[0] for k in T3))
for a in aa3:
    pts = sorted([(k[1], v[0]) for k, v in T3.items() if k[0] == a])
    xs, ys = zip(*pts)
    ax.plot(xs, ys, 'o-', label=r'$\alpha=%.1f$ numeric' % a)
    pts2 = sorted([(k[1], v[1]) for k, v in T3.items() if k[0] == a])
    xs2, ys2 = zip(*pts2)
    ax.plot(xs2, ys2, '--', lw=1, alpha=0.7)
ax.axvline(2 * SIGMA ** 2, color='gray', ls='--', lw=1, label=r'$2\sigma^2$')
ax.set_xlabel(r'$K_0$'); ax.set_ylabel(r'stationary $R^*$')
ax.set_title('T3: Stationary state (dashed = von-Mises theory)')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

fig.suptitle('The reflexive-Kuramoto "explosive transition" is a fixed-horizon nucleation transient',
             fontsize=13)
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(os.path.join(OUT, "nucleation_scaling.png"), dpi=140)
print("saved nucleation_scaling.png")

result = {
    "model": "zero-frequency mean-field XY with feedback alpha, sigma=0.008, dt=0.04",
    "Kc_stationary_theory": 2 * SIGMA ** 2,
    "collapse_rows": [{"alpha": r[0], "K0": r[1], "N": r[2], "t_cross": r[3], "I": r[4]}
                      for r in rows],
    "collapse_summary": {"mean": float(Is.mean()), "median": float(np.median(Is)),
                         "std": float(Is.std()), "min": float(Is.min()), "max": float(Is.max())},
    "apparent_kc_T2": {f"{t}_{n}": v for (t, n), v in T2.items()},
    "stationary_T3": {f"{a}_{k}": {"R_num": v[0], "R_vonMises": v[1]}
                      for (a, k), v in T3.items()},
}
with open(os.path.join(OUT, "nucleation_scaling.json"), "w") as f:
    json.dump(result, f, indent=1)
print("saved nucleation_scaling.json")