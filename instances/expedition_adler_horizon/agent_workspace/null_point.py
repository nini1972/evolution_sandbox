#!/usr/bin/env python3
"""
null_point.py
=============
DeepSeek V4 Flash — locate exact falsification boundaries:
  * null point  a0: eps_law == 0 (law exact by cancellation)
  * 5%  boundary: |eps_law| == 0.05
  * 2%  boundary: |eps_law| == 0.02
  * structural K0-flatness test: eps independent of K0 (law's 1/K0 scaling)
"""
import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq

R0, Rc = 0.05, 0.90


def I_exact(a, epsabs=1e-12):
    val, _ = quad(lambda R: 1.0 / (R ** (a + 1.0) * (1.0 - R * R)),
                  R0, Rc, epsabs=epsabs, epsrel=1e-12, limit=400)
    return val


def eps_law(a):
    """signed relative error of the plain law (positive => overestimate)."""
    law = (1.0 / a) * R0 ** (-a)
    return (law - I_exact(a)) / I_exact(a)


# ---- 1) null point(s) ----
grid = np.linspace(0.5, 2.0, 601)
eg = np.array([eps_law(a) for a in grid])
sign_flips = np.where(np.diff(np.sign(eg)) != 0)[0]
print("=" * 70)
print("NULL POINTS  (eps_law = 0):")
nulls = []
for i in sign_flips:
    a0 = brentq(eps_law, grid[i], grid[i + 1], xtol=1e-10)
    nulls.append(a0)
    print("    a0 = %.6f   (eps_law changes sign: %+.4e -> %+.4e)"
          % (a0, eg[i], eg[i + 1]))

imin = np.argmin(np.abs(eg))
print("    min |eps_law| in scan: %.5e at a = %.4f" % (np.abs(eg[imin]), grid[imin]))

# ---- 2) falsification boundaries ----
print("\nFALSIFICATION BOUNDARIES (|eps_law| = const):")
for level, name in [(0.05, "5%"), (0.02, "2%"), (0.01, "1%")]:
    crossing = np.where(np.diff(np.sign(np.abs(eg) - level)) != 0)[0]
    for i in crossing:
        f = lambda a: abs(eps_law(a)) - level   # noqa: E731
        b = brentq(f, grid[i], grid[i + 1], xtol=1e-10)
        # classify: low side => dangerous region, high side => safe region
        print("    |eps_law| = %s at a = %.4f   (signed eps = %+.4f%%)"
              % (name, b, eps_law(b) * 100))

# ---- 3) K0-flatness structural test ----
# law predicts t_esc = (2/(a*K0)) R0^{-a}.  If the true escape time has any
# additional K0-dependence (e.g. weak K0 in higher-order terms from finite
# threshold Rc), the *relative residual* would vary with K0 at fixed a.
# Exact true value: t_true = (2/K0) * I(a)  =>  rel.err is K0-independent BY
# CONSTRUCTION of the separable reduction.  The real empirical test is whether
# the FULL ODE (time-marched) also shows K0-flat residuals -> Poolside's RK45
# subset verification.  Here we emit the analytic prediction:
print("\nSTRUCTURAL TEST (analytic): rel. residual of the law = f(a) only,")
print("independent of K0.  Empirically verifiable on RK45 subset.")
print("    t_true(K0,a) = (2/K0) * I(a);   |eps| identical for all K0.")

# Emit grid-ready data for Poolside
Ks = np.linspace(0.5, 5.0, 20)
alphas = np.linspace(0.5, 2.0, 16)
I_vals = np.array([I_exact(a) for a in alphas])
print("\nI(a) for alpha grid (for 2D analytic-surface build):")
for a, Iv in zip(alphas, I_vals):
    print("    a=%5.2f  I=%10.4f  t_true(K0=1)=%10.4f" % (a, Iv, 2.0 * Iv))
np.savez('null_boundaries.npz',
         nulls=np.array(nulls), alphas=alphas, I_vals=I_vals,
         alpha_grid=grid, eps_grid=eg)
print("\nsaved null_boundaries.npz")