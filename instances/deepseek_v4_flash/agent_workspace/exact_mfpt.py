"""
EXACT MEAN-FIRST-PASSAGE TIME for the reflexive-noise barrier SDE  (deepseek_v4_flash)
=====================================================================================
Model (same as km_barrier_corrected.py):
    dR = 0.5*R*(K0*R^alpha*(1-R^2) - sigma^2) dt + (sigma/sqrt(N)) dW
    R reflected at 0, absorbing at R_c (small root of K0 R^a (1-R^2) = sigma^2).
    initial R0 = 0.2 * R_c.

Additive noise (coefficient sigma/sqrt(N) is constant), so the MFPT is EXACT:

    m(x0) = (2/D) * int_{x0}^{Rc} exp(-2B(y)/D) * A(y) dy
    A(y)  =        int_0^{y}   exp( 2B(z)/D) dz
    B(x)  = int_0^x b(u) du   (analytic!)
    D     = sigma^2 / N

This replaces Monte-Carlo (with its censoring & 6-point ceiling) by quadrature:
arbitrarily many N values, zero sampling noise.  Goal: test whether the
"crossover" law ln(rate) = c0 - c1*N - b*ln N is REAL or a 6-point artifact.
"""
import numpy as np
import json, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ---------------- model parameters (identical to km_barrier_corrected.py) ------
K0 = 1.0
ALPHA = 1.5
SIG = 0.25
S2 = SIG * SIG

def Rc_small(K0, a, sig):
    lo, hi = 1e-12, 1.0
    for _ in range(200):
        m = 0.5 * (lo + hi)
        if K0 * m**a * (1.0 - m * m) - sig * sig < 0:
            lo = m
        else:
            hi = m
    return 0.5 * (lo + hi)

RC = Rc_small(K0, ALPHA, SIG)

def b(x):
    """drift coefficient"""
    return 0.5 * x * (K0 * x**ALPHA * (1.0 - x * x) - S2)

def B(x):
    """analytic antiderivative of b, B(0)=0"""
    return 0.5 * (K0 * x**(ALPHA + 2) / (ALPHA + 2)
                  - K0 * x**(ALPHA + 4) / (ALPHA + 4)
                  - S2 * x * x / 2.0)

def mfpt_log(N, x0_frac=0.2, npts=400001, p=2.0):
    """log of exact mean first-passage time from x0=x0_frac*RC to RC."""
    D = S2 / N
    x0 = x0_frac * RC
    # nonuniform grid clustered near 0 (where exp(2B/D) peaks) and near RC
    t = np.linspace(0.0, 1.0, npts)
    x = RC * t**p
    Bx = B(x)
    # phi = exp(2B/D)  (<=1, may underflow far from 0 -> fine)
    with np.errstate(under='ignore', over='ignore'):
        phi = np.exp(2.0 * Bx / D)
        # A(y) = cumulative trapezoid of phi from 0
        dx = np.diff(x)
        A = np.concatenate([[0.0], np.cumsum(0.5 * (phi[1:] + phi[:-1]) * dx)])
        # factor out exp(-2B(RC)/D) to keep w = exp(-2(B-B(RC))/D) <= 1
        w = np.exp(-2.0 * (Bx - Bx[-1]) / D)
    i0 = np.searchsorted(x, x0)
    J = np.trapz(w[i0:] * A[i0:], x[i0:])
    lnI = -2.0 * Bx[-1] / D + np.log(J)
    lnm = np.log(2.0 / D) + lnI
    return lnm

def rate_of_N(N):
    """exact exponential rate ~ 1/MFPT"""
    return -mfpt_log(N)   # ln(rate) = -ln(m)

if __name__ == "__main__":
    print(f"RC = {RC:.6f}   B(RC) = {B(RC):.6e}   |B(RC)|/S2 = {abs(B(RC))/S2:.6e}")
    print(f"b'(RC) = {0.5*(K0*RC**ALPHA*(ALPHA-(ALPHA+2)*RC*RC)):.6e}  (curvature at barrier)")
    print()
    # validate against the 6 finite MC rates in km_barrier_corrected.json
    d = json.load(open('km_barrier_corrected.json'))
    print(f"{'N':>6} {'MC_rate':>12} {'exact_rate':>12} {'ratio':>8} {'lnMC':>9} {'lnExact':>9}")
    mc = {}
    for row in d['rows']:
        N = row['N']; r = row['rate']
        if r and r > 0:
            mc[N] = r
            er = math.exp(rate_of_N(N))
            print(f"{N:>6} {r:>12.5e} {er:>12.5e} {er/r:>8.3f} {math.log(r):>9.4f} {math.log(er):>9.4f}")
    print()
    # dense N sweep
    Ns = np.unique(np.round(np.geomspace(40, 20000, 60)).astype(int))
    lnrate = np.array([rate_of_N(N) for N in Ns])
    np.save('exact_Ns.npy', Ns); np.save('exact_lnrate.npy', lnrate)
    print("dense sweep saved:", Ns[0], "...", Ns[-1], "  npts=", len(Ns))
