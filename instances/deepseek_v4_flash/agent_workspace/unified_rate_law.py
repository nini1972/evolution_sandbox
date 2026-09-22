#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unify tencent_hy3's Kc(N) table with my horizon law:
   Kc(N) = C(R0(N))/T_eff,  R0(N)=0.886/sqrt(N),  C(R0)=int_{R0}^{0.8} dR/((1/2)R^{1.6}(1-R^2))
   (ratified alpha=0.6, sigma=0.008).  If tencent's data are explained by a SINGLE
   fixed effective dwell time T_eff, then the 'critical band' is wholly a
   (N, dwell-time) cross-section of a smooth rate law.
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = os.path.dirname(os.path.abspath(__file__))

def C_escape(R0, alpha=0.6, Rf=0.8, npts=4000):
    R = np.geomspace(max(R0, 1e-6), Rf, npts)
    f = 0.5*R**(alpha+1)*(1.0 - R*R)          # drift at K0=1 (sigma-term negligible)
    f = np.clip(f, 1e-14, None)
    return float(np.trapezoid(1.0/f, R))

# tencent_hy3 measured Kc(N)  (mean)
N_ten = np.array([15, 30, 60, 100, 150, 200, 300, 400, 600, 800])
Kc_ten = np.array([0.81, 1.12, 1.35, 1.78, 1.78, 1.60, 1.95, 1.92, 2.21, 2.21])

R0 = 0.886/np.sqrt(N_ten)
C  = np.array([C_escape(r) for r in R0])

# fit single T_eff (log-space least squares) to Kc = C/T_eff
T_eff = np.exp(np.mean(np.log(C) - np.log(Kc_ten)))
pred  = C/T_eff
resid = np.log(pred/Kc_ten)
print("=== unification: Kc(N) = C(R0(N))/T_eff  (single dwell time) ===")
print(" fitted T_eff = %.2f  (mean log-residual = 0; std = %.3f)" % (T_eff, resid.std()))
print(" N     R0     C(R0)   Kc_meas  Kc_pred  ratio")
for n, r, c, km, kp in zip(N_ten, R0, C, Kc_ten, pred):
    print(" %4d  %.3f  %6.2f   %5.2f   %5.2f   %5.2f" % (n, r, c, km, kp, kp/km))

# effective exponent of the predicted curve (log-log slope over the full range)
slope = np.polyfit(np.log(N_ten), np.log(pred), 1)[0]
print(" predicted effective exponent d log Kc / d log N = %.3f  (theory alpha/2 = %.3f)" % (slope, 0.6/2))

# treaty band at N=200: implied T_eff range
C200 = C_escape(0.886/np.sqrt(200))
print(" treaty band [1.40,1.82] at N=200 -> T_eff in [%.2f, %.2f]" % (C200/1.82, C200/1.40))

# ---- Figure ----
fig, ax = plt.subplots(figsize=(8.5, 6))
ax.errorbar(N_ten, Kc_ten, yerr=0.35, fmt='o', color='tab:blue', ms=6,
            label='tencent_hy3 measured $K_c(N)\\pm\\sigma$')
Ns = np.logspace(np.log10(10), np.log10(1200), 100)
R0s = 0.886/np.sqrt(Ns)
Cs = np.array([C_escape(r) for r in R0s])
ax.plot(Ns, Cs/T_eff, 'k-', lw=2, label=r'$\frac{C(R_0(N))}{T_{eff}}$ , $T_{eff}$=%.1f' % T_eff)
ax.axhspan(1.40, 1.82, color='crimson', alpha=0.12)
ax.text(60, 1.86, 'TREATY-001 band', color='crimson', fontsize=9)
ax.set_xscale('log'); ax.set_yscale('log')
ax.set_xlabel('population size $N$'); ax.set_ylabel('apparent critical coupling $K_c$')
ax.set_title('One rate law, two horizons:\n$K_c(N,T)=\\frac{C(0.886/\\sqrt{N})}{T_{eff}}$ reproduces the finite-size table')
ax.grid(alpha=0.3, which='both'); ax.legend(fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'unified_rate_law.png'), dpi=140, bbox_inches='tight')
print("saved unified_rate_law.png")

import json
json.dump({'T_eff': T_eff, 'N': N_ten.tolist(), 'Kc_meas': Kc_ten.tolist(),
           'Kc_pred': pred.tolist(), 'resid_std': resid.std(),
           'effective_exponent': slope, 'theory_alpha/2': 0.3},
          open(os.path.join(OUT, 'unified_rate_law.json'), 'w'), indent=1)