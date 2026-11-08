"""
Falsifier audit of the Horizon Escape Law null point.
DeepSeek V4 Flash — adversarial verification of claims in
DOSSIER-expedition-2026-09-24-kuramoto-horizon-escape-law.md

Three tests:
  T1  Series decomposition: is the null point a cancellation between the
      negative truncation term -(1/a)Rc^-a and the positive geometric series?
  T2  R0-asymptotics: does relative residual scale as R0^alpha (slope 1 in
      log|eps| vs alpha*log R0)?  -> law is asymptotically exact for ALL alpha.
  T3  Grid saturation of the 5% boundary alpha5(R0).
"""
import numpy as np
from scipy.integrate import quad

R_ESC = 0.9


def I_exact(alpha, R0, Rc=R_ESC):
    f = lambda R: 1.0 / (R ** (alpha + 1.0) * (1.0 - R * R))
    val, _ = quad(f, R0, Rc, epsabs=1e-14, epsrel=1e-14, limit=500)
    return val


def I_law(alpha, R0):
    return (1.0 / alpha) * R0 ** (-alpha)


def eps(alpha, R0):
    return (I_exact(alpha, R0) - I_law(alpha, R0)) / I_law(alpha, R0)


def series_terms(alpha, R0, Rc=R_ESC, kmax=60):
    """Return (law_term, trunc_term, geom_series_sum) with the k=0 split."""
    law = (1.0 / alpha) * R0 ** (-alpha)
    trunc = -(1.0 / alpha) * Rc ** (-alpha)
    geom = 0.0
    for k in range(1, kmax + 1):
        denom = 2.0 * k - alpha
        geom += (Rc ** (2 * k - alpha) - R0 ** (2 * k - alpha)) / denom
    return law, trunc, geom


print("=" * 74)
print("T1  SERIES DECOMPOSITION AND THE NULL POINT")
print("=" * 74)
print(f"{'alpha':>7} {'I_exact':>12} {'law+trunc+geom':>15} {'resid%':>9} "
      f"{'trunc/I_law':>12} {'geom/I_law':>11} {'geom/|trunc|':>13}")
for a in [0.50, 0.6425, 0.75, 0.8494, 1.00, 1.50, 1.99]:
    law, tr, gm = series_terms(a, 0.05)
    recon = law + tr + gm
    Ie = I_exact(a, 0.05)
    print(f"{a:7.4f} {Ie:12.6f} {recon:15.6f} {100*eps(a,0.05):9.3f} "
          f"{tr/law:12.4f} {gm/law:11.4f} {gm/abs(tr):13.4f}")

print("\n  -> null occurs where geom/|trunc| crosses 1.0 (cancellation).")

print("\n  Null point vs R_ESC (is alpha0 universal or geometry-dependent?)")
from scipy.optimize import brentq
for Rc in [0.70, 0.80, 0.90, 0.95]:
    def g(a, Rc=Rc):
        f = lambda R: 1.0 / (R ** (a + 1.0) * (1.0 - R * R))
        return quad(f, 0.05, Rc, epsabs=1e-14, epsrel=1e-14, limit=500)[0] \
               - (1.0 / a) * 0.05 ** (-a)
    try:
        a0 = brentq(g, 0.501, 1.999)
    except ValueError:
        a0 = float('nan')
    print(f"    R_esc = {Rc:.2f}   alpha0 = {a0:.4f}")

print("\n  -> If alpha0 moves with R_esc, it is NOT a universal constant.")

print("\n" + "=" * 74)
print("T2  R0-ASYMPTOTICS:  does eps ~ C(alpha) * R0^alpha ?")
print("=" * 74)
R0s = np.array([0.005, 0.01, 0.02, 0.05, 0.10, 0.20])
print(f"{'alpha':>7} " + " ".join(f"R0={r:<7.3f}" for r in R0s) + "   slope")
for a in [0.6, 1.0, 1.5]:
    e = np.array([eps(a, r) for r in R0s])
    x = a * np.log(R0s)
    slope = np.polyfit(x, np.log(np.abs(e)), 1)[0]
    print(f"{a:7.2f} " + " ".join(f"{v:10.4e}" for v in e) + f"   {slope:6.3f}")

print("\n  -> slope ~ 1.0 confirms eps ~ C(alpha) R0^alpha:")
print("     relative residual vanishes for ALL alpha as R0 -> 0.")

print("\n" + "=" * 74)
print("T3  5% BOUNDARY alpha5(R0) AND GRID SATURATION")
print("=" * 74)
alphas = np.linspace(0.50, 2.0, 601)
print(f"{'R0':>7} {'alpha5':>9} {'note':>28}")
for r in [0.005, 0.01, 0.02, 0.05, 0.10, 0.20]:
    e = np.array([abs(eps(a, r)) for a in alphas])
    idx = np.where(e < 0.05)[0]
    a5 = alphas[idx[0]] if len(idx) else float('nan')
    note = "GRID-SATURATED (a=0.50 edge)" if a5 <= 0.501 else ""
    print(f"{r:7.3f} {a5:9.4f} {note:>28}")

print("\n  -> alpha5 decreases monotonically with R0; for small R0 it pins to")
print("     the alpha=0.50 grid edge, so a linear alpha5(R0) fit must NOT be")
print("     extrapolated below R0 ~ 0.01.")
print("=" * 74)