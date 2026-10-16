#!/usr/bin/env python3
"""Robustness of the P4 checkerboard window:
 (1) (r, eps) tongue map: fraction of cells in strict P4
 (2) N-dependence: N=160, 320 at eps=0.135
 (3) local dynamics: is the P4 orbit stable / what is the cell-level Lyapunov?
"""
import numpy as np, json

def coupled(x, r, eps):
    f = r*x*(1.0 - x)
    return (1.0 - eps)*f + (eps/2.0)*(np.roll(f,1) + np.roll(f,-1))

def period_counts(x, r, eps, trans=10000, T=48, seed=0):
    x = x.copy()
    for _ in range(trans): x = coupled(x, r, eps)
    S = np.empty((T, x.size))
    for t in range(T):
        x = coupled(x, r, eps); S[t] = x
    s2 = np.max(np.abs(S[2:,:] - S[:-2,:]), axis=0)
    s4 = np.max(np.abs(S[4:,:] - S[:-4,:]), axis=0)
    s8 = np.max(np.abs(S[8:,:] - S[:-8,:]), axis=0)
    p2  = int(np.sum(s2 < 1e-9))
    p4  = int(np.sum((s2 >= 1e-9) & (s4 < 1e-9)))
    p8  = int(np.sum((s4 >= 1e-9) & (s8 < 1e-9)))
    ap  = int(np.sum(s8 >= 1e-9))
    return p2, p4, p8, ap

# ---- (1) tongue map: r in [3.8, 3.95], eps in [0.125, 0.15], N=120
rs  = np.arange(3.80, 3.951, 0.01)
eps = np.arange(0.125, 0.151, 0.005)
grid = np.zeros((len(eps), len(rs)))
for i, e in enumerate(eps):
    for j, r in enumerate(rs):
        np.random.seed(42)
        x = np.random.rand(120)
        _, p4, p8, ap = period_counts(x, r, e, trans=6000, T=48)
        grid[i, j] = (p4 + 0.5*p8) / 120.0
np.save("tongue_grid.npy", grid)
print("tongue map (rows=eps, cols=r): P4-equivalent fraction")
print("r     " + "".join("%5.2f" % v for v in rs))
for i, e in enumerate(eps):
    print("%.3f " % e + "".join("%5.2f" % v for v in grid[i]))

# ---- (2) N-dependence at r=3.865, eps=0.135
print("\nN-dependence (r=3.865, eps=0.135):")
nres = {}
for N in (80, 160, 320):
    np.random.seed(0)
    x = np.random.rand(N)
    p2, p4, p8, ap = period_counts(x, 3.865, 0.135, trans=12000, T=48)
    nres[N] = dict(p2=p2, p4=p4, p8=p8, aperiodic=ap, frac_p4=p4/N)
    print("  N=%3d : P4=%d/%d  P8=%d  aperi=%d" % (N, p4, N, p8, ap))

# ---- (3) local stability of the P4 orbit via linearized iteration
#      The lattice map is F(x)_i = (1-eps) f(x_i) + (eps/2)(f(x_{i-1}) + f(x_{i+1})),
#      f = r x (1-x).  Linearize about the period-4 orbit:
#      D(F^4) along the cycle;  eigenvalues of the cycle Jacobian -> max |lambda|.
#      max|lambda| < 1  =>  orbit is locally stable (pure period-4, not chaos).
r, e, N = 3.865, 0.135, 120
np.random.seed(0)
x = np.random.rand(N)
for _ in range(15000): x = coupled(x, r, e)
# sample the 4 phases of the orbit
phases = []
for _ in range(4):
    phases.append(x.copy())
    x = coupled(x, r, e)

def jac(x0):
    # dF_i/dx_j = (1-eps)*f'(x_i) [j=i] + (eps/2)*f'(x_j) [j=i+/-1]
    s = r * (1.0 - 2.0 * x0)
    J = np.diag((1.0 - e) * s)
    J += (e/2.0) * (np.diag(s[1:], 1) + np.diag(s[:-1], -1))
    n = len(s)
    J[0, n-1] += (e/2.0) * s[n-1]
    J[n-1, 0] += (e/2.0) * s[0]
    return J

# Jacobian of F at each phase
Js = [jac(ph) for ph in phases]
Jcycle = Js[3] @ Js[2] @ Js[1] @ Js[0]
evals = np.linalg.eigvals(Jcycle)
lmax = np.max(np.abs(evals))
print("\nPeriod-4 cycle stability (N=120, r=3.865, eps=0.135):")
print("  max |eigenvalue| of cycle Jacobian = %.6f" % lmax)
print("  -> %s" % ("STABLE period-4 orbit (pure periodicity, not chaos)" if lmax < 1.0 else "UNSTABLE (chaotic/strange)"))
print("\nsaved tongue_grid.npy; N results:", json.dumps(nres))
