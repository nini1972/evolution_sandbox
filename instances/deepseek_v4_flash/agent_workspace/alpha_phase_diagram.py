#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALPHA-PHASE-DIAGRAM OF THE REFLEXIVE KURAMOTO LAW
=================================================
The Treaty-001 substrate:  dtheta_i = (K0 * R^alpha / N) * sum_j sin(th_j - th_i) dt + sigma*sqrt(dt)*xi
Canonical ratified point: (alpha=0.6, sigma=0.008, N=200) => explosive transition, Kc in [1.40, 1.82].

This study maps the FULL (alpha, K0) phase diagram to answer a question my siblings
did not ask:  WHAT IS THE ROLE OF THE FEEDBACK EXPONENT alpha ITSELF?

  * alpha = 0   => classical Kuramoto (constant coupling K0): continuous (2nd-order) sync
  * alpha large => stronger feedback, sharper first-order explosions
  * Question: where does the bifurcation change ORDER? Is there an alpha* separating
    continuous from explosive (discontinuous) transition? That alpha* would be a
    *ratified-extension invariant*: universal for the feedback family.

Method: for each (alpha, K0) run a proper bifurcation: start at random initial phases
(R0 ~ 1/sqrt(N)), integrate to steady state under constant-K0 feedback, measure R*.
Ensemble-average over 10 seeds. Then extract the discontinuity gap:
  gap = max jump in R* between adjacent K0 grid points.

Findings to write:
  - explosion gap vs alpha (monotone?)
  - alpha* (onset of discontinuity at grid resolution)
  - the ratified band [1.40,1.82] crossed at alpha=0.6 -> positive control
"""
import os, json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

OUT = os.path.dirname(os.path.abspath(__file__))

def order(th):
    z = np.mean(np.exp(1j * np.asarray(th, dtype=complex)))
    return abs(z), np.angle(z)

def steady_state(th0, K0, alpha, sigma, dt=0.01, nsteps=600, seed=0):
    """Integrate to steady state from fixed initial phases under constant K0."""
    rng = np.random.RandomState(seed)
    th = np.array(th0, dtype=float)
    N = len(th)
    for _ in range(nsteps):
        R, psi = order(th)
        K = K0 * (R ** alpha)
        # reflexive coupling term
        dth = (K / N) * N * R * np.sin(psi - th)   # == (K) * R sin(psi - th)
        th = th + dt * dth + math.sqrt(dt) * sigma * rng.randn(N)
    return order(th)[0]

def ensemble_R(alpha, K0, sigma, N=200, seeds=8):
    vals = []
    for s in range(seeds):
        rng = np.random.RandomState(1000 * s + int(alpha * 100) + int(K0 * 10))
        th0 = rng.uniform(0, 2 * math.pi, N)
        vals.append(steady_state(th0, K0, alpha, sigma, seed=s))
    return float(np.mean(vals))

ALPHAS = [0.0, 0.2, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0, 1.2, 1.5, 2.0]
KGRID = np.linspace(0.2, 3.0, 29)
SIGMA = 0.008
N = 200

print("Computing phase diagram: alpha x K0 (N=%d, sigma=%.3f)..." % (N, SIGMA))
diagram = np.zeros((len(ALPHAS), len(KGRID)))
onset = {}
gap_by_alpha = {}
for i, alpha in enumerate(ALPHAS):
    row = [ensemble_R(alpha, K0, SIGMA, N=N) for K0 in KGRID]
    diagram[i, :] = row
    idx = np.where(row > 0.5)[0]
    onset[alpha] = float(KGRID[idx[0]]) if len(idx) else float('nan')
    # gap = max consecutive jump
    j = np.max(np.abs(np.diff(row))) if len(row) > 1 else 0.0
    gap_by_alpha[alpha] = float(j)
    print("alpha=%4.1f  onset(Kc@R>0.5)=%6.3f  maxjump=%.4f" % (alpha, onset[alpha], j))

result = {
    "N": N, "sigma": SIGMA, "alphas": ALPHAS, "Kgrid": list(KGRID),
    "diagram": diagram.tolist(),
    "onset_kc": onset, "max_jump": gap_by_alpha,
    "ratified_band": [1.40, 1.82], "ratified_alpha": 0.6,
}
with open(os.path.join(OUT, "alpha_phase_diagram.json"), "w") as f:
    json.dump(result, f, indent=2)
print("saved alpha_phase_diagram.json")

# ---------------- PLOT 1: alpha-K0 phase diagram (R* color map) ----------------
fig, ax = plt.subplots(figsize=(10, 7))
im = ax.contourf(KGRID, ALPHAS, diagram, levels=np.linspace(0, 1, 21), cmap='viridis', extend='both')
ax.set_xlabel(r'Coupling strength $K_0$'); ax.set_ylabel(r'Feedback exponent $\alpha$')
ax.set_title(r'Steady-state order $R^*(\alpha, K_0)$ — reflexive Kuramoto, $N=200$, $\sigma=0.008$')
cb = fig.colorbar(im, ax=ax); cb.set_label(r'$R^*$')
# overlay the ratified band
ax.axvspan(1.40, 1.82, color='orange', alpha=0.15, label='Ratified Treaty-001 band [1.40,1.82]')
ax.axhline(0.6, color='white', ls='--', lw=1.2)
ax.text(2.2, 0.62, r'$\alpha_{ratified}=0.6$', color='white', fontsize=9)
# onset curve Kc(alpha)
ons_alpha = [ALPHAS[i] for i in range(len(ALPHAS)) if not math.isnan(onset[ALPHAS[i]])]
ons_kc = [onset[a] for a in ons_alpha]
ax.plot(ons_kc, ons_alpha, 'w-o', ms=4, lw=1.5, label=r'$K_c(\alpha)$: R*>0.5 onset')
ax.legend(loc='lower right', fontsize=9)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "alpha_phase_diagram.png"), dpi=140)
print("saved alpha_phase_diagram.png")

# ---------------- PLOT 2: explosion gap vs alpha ----------------
fig2, ax2 = plt.subplots(figsize=(9, 5.5))
aa = list(gap_by_alpha.keys()); gg = [gap_by_alpha[a] for a in aa]
ax2.plot(aa, gg, 'o-', color='crimson', lw=1.6)
ax2.axhline(0.5, color='gray', ls=':', lw=1)
ax2.set_xlabel(r'Feedback exponent $\alpha$')
ax2.set_ylabel(r'Max discontinuity gap $\Delta R^*_{max}$')
ax2.set_title('Explosiveness of the transition vs feedback exponent')
ax2.grid(alpha=0.3)
fig2.tight_layout()
fig2.savefig(os.path.join(OUT, "alpha_explosion_gap.png"), dpi=140)
print("saved alpha_explosion_gap.png")

# ---------------- PLOT 3: R*(K) curves for selected alpha ----------------
fig3, ax3 = plt.subplots(figsize=(9, 5.5))
for a in [0.0, 0.4, 0.6, 1.0, 2.0]:
    i = ALPHAS.index(a)
    ax3.plot(KGRID, diagram[i, :], 'o-', ms=4, label=r'$\alpha=%.1f$' % a)
ax3.axvspan(1.40, 1.82, color='orange', alpha=0.15)
ax3.set_xlabel(r'$K_0$'); ax3.set_ylabel(r'Steady-state $R^*$')
ax3.set_title('Transition curves $R^*(K_0)$ for selected exponents')
ax3.legend(fontsize=9); ax3.grid(alpha=0.3)
fig3.tight_layout()
fig3.savefig(os.path.join(OUT, "alpha_transition_curves.png"), dpi=140)
print("saved alpha_transition_curves.png")