#!/usr/bin/env python3
"""
debug_residual_shape.py
=======================
DeepSeek V4 Flash — why did the log-log slope fit fail? Print raw e(R0), detect
(a) sign change of delta(a) across the crossover, (b) non-power-law curvature,
(c) possible log-resonance near alpha=2.

delta(R0) = t_quad - t_ana  [sign tells over/under-estimate]
theory:    delta_oo = lim_{R0->0} delta  = -(2/(aK)) R_esc^{-a}
                                    + (1/K) sum_{k>=1} R_esc^{2k-a}/(k - a/2)
Resonance: alpha = 2k, k in Z+  =>  pole in the k-th series term (log divergence).
"""
import numpy as np
from scipy.integrate import quad as quad1d

R_ESC = 0.90
K0 = 1.0

def integrand(R, a, K0):
    return 2.0 / (K0 * R**(a + 1.0) * (1.0 - R * R))

def t_quad(R0, a):
    val, _ = quad1d(integrand, R0, R_ESC, args=(a, K0),
                    epsabs=1e-13, epsrel=1e-13, limit=2000)
    return val

def t_ana(R0, a):
    return 2.0 / (a * K0) * R0**(-a)

# --- exact series delta_oo (as R0->0) from the truncated series, for sign map
def delta_oo_series(a, kmax=400):
    s = -(2.0 / (a * K0)) * R_ESC**(-a)
    for k in range(1, kmax):
        s += R_ESC**(2.0 * k - a) / (k - a / 2.0) / K0
    return s

print("=" * 72)
print("delta sign map: delta_oo(a) = lim_{R0->0}[t_quad - t_ana]")
print("=" * 72)
aa = np.linspace(0.25, 2.5, 19)
print(f"{'a':>6} {'delta_oo':>12} {'sign':>6} {'near-resonance?':>15}")
for a in aa:
    d = delta_oo_series(a)
    nk = np.round(a / 2.0)
    res = ("RES 2k=%d" % (int(2 * nk))) if abs(a - 2 * nk) < 0.05 else ""
    print(f"{a:6.2f} {d:12.5f} {'+' if d > 0 else '-'} {res:>15}")

# --- raw e(R0) curves, log-log ---------------------------------------------
R0s = np.geomspace(1e-4, 2e-2, 40)
print()
print("=" * 72)
print("raw relative error e(R0) [%]  (log-spaced R0, 8 samples shown)")
print("=" * 72)
for a in [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]:
    es = []
    for R0 in R0s:
        tq = t_quad(R0, a)
        ta = t_ana(R0, a)
        es.append((ta - tq) / tq)   # signed!
    es = np.array(es)
    show = es[np.linspace(0, len(es) - 1, 8, dtype=int)]
    print(f"a={a:4.2f}: " + " ".join(f"{100*v:8.4f}" for v in show))
    # windowed slope: last 4 points (asymptotic)
    lr, le = np.log10(R0s[-4:]), np.log10(np.abs(es[-4:]))
    sw = np.polyfit(lr, le, 1)[0]
    print(f"        windowed slope (asymptotic tail) = {sw:+.3f}  | theory +{a:.2f}")

# --- resonance check: alpha near 2.0, log slope of e ------------------------
print()
print("=" * 72)
print("near-resonance alpha = 2.0: e(R0) ~ R0^2 * log(1/R0)?  (slope -> 2 slowly)")
print("=" * 72)
for a in [2.0, 1.98]:
    lr, le = [], []
    for R0 in np.geomspace(1e-4, 1e-2, 20):
        tq = t_quad(R0, a)
        ta = t_ana(R0, a)
        lr.append(np.log10(R0)); le.append(np.log10(abs(ta - tq) / tq))
    lr, le = np.array(lr), np.array(le)
    b, m = np.polyfit(lr, le, 1)
    print(f"a={a:.3f}: slope={m:+.3f} (asymptotic ~2.0), intercept=10^{b:.3f}")
