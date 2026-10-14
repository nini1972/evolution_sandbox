#!/usr/bin/env python3
"""
test_next_order_scaling.py
==========================
DeepSeek V4 Flash — falsification of the next-order correction.

Next-order theory: t_esc ~ (2/(a*K0))*R0^(-a) * [1 - C(a)*(R0/R_esc)^a],  C(a)>0.
Predictions under test:
  P1. Relative error of the raw law, e(R0) = |t_ana - t_quad|/t_quad, follows
      log-log slope = a  exactly:  e(R0) ~ C(a) (R0/R_esc)^a  as R0 -> 0.
  P2. The error amplitude C(a) is independent of K0 (both terms are ~1/K0),
      i.e. e(K0) is FLAT across K0 at fixed (a, R0).
  P3. The finite-threshold theory prediction of the slope: at fixed a, R0,
      e(K0_1)/e(K0_2) = 1 (K0 cancels identically).
"""
import numpy as np
from scipy.integrate import quad as quad1d

R_ESC = 0.90
ALPHA_SWEEP = np.array([0.5, 0.75, 1.0, 1.25, 1.5, 2.0])
K0_SWEEP = np.array([0.5, 1.0, 2.0, 5.0])

def integrand(R, a, K0):
    return 2.0 / (K0 * R**(a+1.0) * (1.0 - R*R))

def t_quad(R0, a, K0):
    """scalar reference quadrature (for per-point falsification)."""
    val, _ = quad1d(integrand, R0, R_ESC, args=(a, K0),
                    epsabs=1e-12, epsrel=1e-12, limit=2000)
    return val

def t_ana(R0, a, K0):
    return 2.0 / (a * K0) * R0**(-a)

# ---------------- P1: log-log slope of residual vs R0 (fixed a, K0) ------
K0_fixed = 1.0
R0_range = np.geomspace(1e-4, 2e-2, 40)
print("="*70)
print("P1: log-log slope of relative error e(R0) vs R0  (theory: slope = a)")
print("="*70)
print(f"{'a':>5}  {'fitted slope':>13}  {'theory=a':>9}  {'C(a)':>8}  {'R^2':>7}")
slopes = {}
Cs = {}
for a in ALPHA_SWEEP:
    es = []
    for R0 in R0_range:
        tq = t_quad(R0, a, K0_fixed)
        ta = t_ana(R0, a, K0_fixed)
        es.append(abs(ta - tq) / tq)
    es = np.array(es)
    # fit log e = b + a*log R0
    lr = np.log10(R0_range)
    le = np.log10(es)
    b, m = np.polyfit(lr, le, 1)
    pred = b + m*lr
    ss_res = np.sum((le - pred)**2)
    ss_tot = np.sum((le - le.mean())**2)
    r2 = 1 - ss_res/ss_tot
    C = 10**b / R_ESC**a   # amplitude definition: e ~ C*(R0/R_esc)^a
    slopes[a] = m
    Cs[a] = C
    print(f"{a:5.2f}  {m:13.4f}  {a:9.2f}  {C:8.4f}  {r2:7.5f}")

# ---------------- P2/P3: K0-independence -----------------------------------
print()
print("="*70)
print("P2/P3: relative error e(K0) at fixed (a, R0) — theory predicts FLAT")
print("="*70)
R0_p2 = 0.02
print(f"{'a':>5}  " + "  ".join(f"K0={k:.1f}" for k in K0_SWEEP) + "   | spread")
for a in ALPHA_SWEEP:
    es = []
    for k0 in K0_SWEEP:
        tq = t_quad(R0_p2, a, k0)
        ta = t_ana(R0_p2, a, k0)
        es.append(abs(ta - tq) / tq)
    es = np.array(es)
    spread = (es.max() - es.min()) / es.mean() * 100
    print(f"{a:5.2f}  " + "  ".join(f"{e*100:7.3f}%" for e in es) +
          f"   | {spread:6.2f}%")

# ---------------- cross-check: amplitude ratio prediction ------------------
print()
print("="*70)
print("Amplitude consistency: theory C(a) should be same at K0=特拉 vs K0=1")
print("="*70)
for a in [1.0, 1.5]:
    es = []
    for k0 in K0_SWEEP:
        tq = t_quad(R0_p2, a, k0)
        ta = t_ana(R0_p2, a, k0)
        es.append((abs(ta-tq)/tq) * (R_ESC/R0_p2)**a)  # C= e*(R_esc/R0)^a
    es = np.array(es)
    print(f"a={a:.2f}: C(a) from each K0 = " +
          ", ".join(f"{c:.4f}" for c in es) +
          f"  | relative spread = {(es.max()-es.min())/es.mean()*100:.2f}%")

print()
if all(abs(slopes[a] - a) < 0.08 for a in slopes):
    print("CONFIRMED (P1): slope(e vs R0) == a within 0.08 for all a")
else:
    print("FALSIFIED (P1): some slopes deviate from a by >0.08")
