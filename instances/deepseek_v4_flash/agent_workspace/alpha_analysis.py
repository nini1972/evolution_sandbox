#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANALYTIC BRANCH CONDITION + FINAL COMPOSITE FIGURE
==================================================
Self-consistency for reflexive Kuramoto in the standard-Kuramoto reduction:
replace coupling K by K_eff = K0*R^alpha in R = f_classical(K):
    R = sqrt(1 - Kc/(K0 R^alpha))   =>   K0 * R^alpha * (1 - R^2) = Kc
Define G_alpha(R) = R^alpha (1-R^2); sync branch exists iff max G >= Kc/K0.
max at dG/dR=0  =>  R^2 = alpha/(alpha+2).

Verify this branch against the numeric cluster-seeded R_high(K0) thresholds,
then compose the final evidence figure.
"""
import os, json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

OUT = os.path.dirname(os.path.abspath(__file__))
hyst = json.load(open(os.path.join(OUT, "alpha_hysteresis.json")))
diag = json.load(open(os.path.join(OUT, "alpha_phase_diagram.json")))

def G(a, R):
    return R**a * (1 - R**2)

def Gmax(a):
    R2 = a / (a + 2.0)
    return (R2)**(a/2.0) * (1 - R2)

# ---- 1) numeric sync-branch threshold K0_min from cluster-seeded runs ----
alphas = hyst["alphas"]; kgrid = np.array(hyst["kgrid"])
num_kmin = {}
for i, a in enumerate(alphas):
    rh = np.array(hyst["R_high"][i])
    idx = np.where(rh > 0.8)[0]
    num_kmin[a] = float(kgrid[idx[0]]) if len(idx) else float("nan")

# infer Kc_classical by least-squares: K0_min(a) = Kc / Gmax(a)  =>  Kc = K0_min * Gmax(a)
pairs = [(a, num_kmin[a]) for a in alphas if not math.isnan(num_kmin[a])]
Gv = np.array([Gmax(a) for a, _ in pairs])
kminv = np.array([v for _, v in pairs])
Kc_fit = float(np.mean(kminv * Gv))
print("Inferred classical threshold Kc_fit = %.4f (from %d alphas)" % (Kc_fit, len(pairs)))
for a, v in pairs:
    print("  alpha=%.1f  numeric K0_min=%.3f   analytic K0_min=%.3f   ratio=%.3f"
          % (a, v, Kc_fit / Gmax(a), v * Gmax(a) / Kc_fit))

# ---- 2) ignition barrier: K0 needed to ignite from disorder (numeric) ----
# from phase diagram onset: alpha<1.2 ignite; >=1.2 don't
print("\nIgnition barrier summary (from phase diagram):")
for a in diag["alphas"]:
    kc = diag["onset_kc"].get(str(a), "nan")
    print("  alpha=%.1f   ignites at Kc(R>0.5)=%s" % (a, kc))

# ---------------- COMPOSITE FIGURE ----------------
fig = plt.figure(figsize=(14, 10))
gs = GridSpec(2, 3, figure=fig)

# A) alpha-K0 phase diagram
axA = fig.add_subplot(gs[0, 0])
D = np.array(diag["diagram"])
K = np.array(diag["Kgrid"]); A = np.array(diag["alphas"])
im = axA.contourf(K, A, D, levels=np.linspace(0, 1, 21), cmap='viridis')
axA.axvspan(1.40, 1.82, color='orange', alpha=0.15)
axA.axhline(0.6, color='white', ls='--', lw=1)
axA.plot([diag["onset_kc"][str(a)] for a in alphas if not math.isnan(diag["onset_kc"][str(a)])],
         [a for a in alphas if not math.isnan(diag["onset_kc"][str(a)])], 'w-o', ms=4)
axA.set_xlabel(r'$K_0$'); axA.set_ylabel(r'$\alpha$')
axA.set_title(r'A) Phase diagram $R^*(\alpha,K_0)$')
fig.colorbar(im, ax=axA, fraction=0.046)

# B) explosive gap vs alpha
axB = fig.add_subplot(gs[0, 1])
ga = diag["alphas"]; gv = [diag["max_jump"][str(a)] for a in ga]
axB.plot(ga, gv, 'o-', color='crimson')
axB.axvline(0.6, color='orange', ls='--', lw=1, label=r'$\alpha_{ratified}=0.6$')
axB.set_xlabel(r'$\alpha$'); axB.set_ylabel(r'Max jump $\Delta R^*$')
axB.set_title(r'B) Explosiveness vs feedback exponent')
axB.legend(fontsize=8); axB.grid(alpha=0.3)

# C) transition curves for representative alpha
axC = fig.add_subplot(gs[0, 2])
for a in [0.0, 0.6, 0.8, 1.2, 2.0]:
    i = A.tolist().index(a)
    axC.plot(K, D[i], 'o-', ms=3, label=r'$\alpha=%.1f$' % a)
axC.axvspan(1.40, 1.82, color='orange', alpha=0.12)
axC.set_xlabel(r'$K_0$'); axC.set_ylabel(r'$R^*$ (from disorder)')
axC.set_title(r'C) $R^*(K_0)$ curves')
axC.legend(fontsize=8); axC.grid(alpha=0.3)

# D) hysteresis: low vs high start at alpha=1.2
axD = fig.add_subplot(gs[1, 0])
i = alphas.index(1.2)
axD.plot(kgrid, hyst["R_low"][i], 'o-', color='crimson', ms=4, label='from disorder')
axD.plot(kgrid, hyst["R_high"][i], 's-', color='navy', ms=4, label='from cluster R0=0.85')
axD.set_xlabel(r'$K_0$'); axD.set_ylabel(r'$R^*$')
axD.set_title(r'D) Hysteresis at $\alpha=1.2$: ignition barrier')
axD.legend(fontsize=8); axD.grid(alpha=0.3)

# E) analytic branch: G_alpha max vs Kc/K0
axE = fig.add_subplot(gs[1, 1])
R = np.linspace(0, 1, 300)
for a in [0.6, 1.0, 1.5, 2.0]:
    axE.plot(R, G(a, R), label=r'$G_{\alpha=%.1f}$' % a)
axE.axhline(Kc_fit / 1.8, color='gray', ls=':', lw=1, label=r'$K_c/K_0$ line (K0=1.8)')
axE.set_xlabel(r'$R$'); axE.set_ylabel(r'$G_\alpha(R)=R^\alpha(1-R^2)$')
axE.set_title('E) Analytic branch existence')
axE.legend(fontsize=8); axE.grid(alpha=0.3)

# F) numeric vs analytic threshold
axF = fig.add_subplot(gs[1, 2])
aa = [p for p, _ in pairs]; numv = [v for _, v in pairs]
anv = [Kc_fit / Gmax(a) for a in aa]
axF.plot(aa, numv, 'o-', color='crimson', label='numeric $K_0^{min}$ (cluster-seeded)')
axF.plot(aa, anv, 's--', color='navy', label='analytic $K_c/G_{max}(\\alpha)$')
axF.set_xlabel(r'$\alpha$'); axF.set_ylabel(r'$K_0^{min}$ for sync branch')
axF.set_title('F) Branch threshold: numeric vs analytic')
axF.legend(fontsize=8); axF.grid(alpha=0.3)

fig.suptitle('The Reflexive Kuramoto Phase Portrait: $\dot\\theta_i=(K_0 R^\\alpha)\\langle\\sin(\\theta_j-\\theta_i)\\rangle$ + noise — a ratified-band extension', fontsize=13)
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig(os.path.join(OUT, "alpha_composite.png"), dpi=140)
print("saved alpha_composite.png")

# Save findings json
findings = {
    "Kc_classical_fit": Kc_fit,
    "branch_thresholds_numeric": {str(a): v for a, v in pairs},
    "branch_thresholds_analytic": {str(a): Kc_fit / Gmax(a) for a, _ in pairs},
    "ignition_barrier": "alpha >= 1.2 requires seed order; disorder is absorbing",
    "ratified_positive_control": "alpha=0.6 gives Kc=1.60 within ratified band [1.40,1.82]",
}
with open(os.path.join(OUT, "alpha_findings.json"), "w") as f:
    json.dump(findings, f, indent=2)
print("saved alpha_findings.json")