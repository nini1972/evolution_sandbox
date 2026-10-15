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

# ---- (3) cell-level: for a P4-locked lattice, measure local slope product
#     around the orbit (stability of period-4 orbit in lattice coordinates)
r, e, N = 3.865, 0.135, 120
np.random.seed(0)
x = np.random.rand(N)
for _ in range(15000): x = coupled(x, r, e)
# record orbit
orb = [x.copy() for _ in range(4)]
for _ in range(4): x = coupled(x, r, e)
# perturbation growth over one 4-period cycle
d = np.zeros(N); d[60] = 1e-12
for _ in range(4):
    # linearize: f' = r(1-2x), coupling: (1-eps)*f' + eps/2*(shifts of f')
    x0 = coupled(x, r, e)  # actual next point (x updated implicitly via orbit)
# simpler: re-run from x0 and x0+d
x0 = coupled(np.random.seed(0) or np.random.rand(1) and x, r, e)  # placeholder no-op guard
print("\nsaved tongue_grid.npy; N results:", json.dumps(nres))
