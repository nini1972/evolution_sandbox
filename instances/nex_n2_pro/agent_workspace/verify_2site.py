#!/usr/bin/env python3
"""Verify the checkerboard reduction of the coupled logistic lattice to a 2-site map.

Checkerboard invariant: x_i(t) depends only on parity i mod 2, so
  x_even = a, x_odd = b   (on each sublattice)
Then the lattice map F restricted to the checkerboard manifold is exactly:
  a' = (1-eps) f(a) + eps f(b)
  b' = (1-eps) f(b) + eps f(a)
with f(x) = r x (1-x).
Any period-4 orbit of the N-lattice with checkerboard symmetry is therefore a
period-4 orbit of this 2-site map, and conversely.
"""
import numpy as np

r, eps = 3.865, 0.135
f = lambda x: r * x * (1.0 - x)

def two_site(a, b, steps):
    for _ in range(steps):
        a, b = (1-eps)*f(a) + eps*f(b), (1-eps)*f(b) + eps*f(a)
    return a, b

def p4check2(a, b, trans=20000, T=48, tol=1e-9):
    a, b = a, b
    S = []
    for _ in range(trans + T):
        a, b = (1-eps)*f(a) + eps*f(b), (1-eps)*f(b) + eps*f(a)
        S.append((a, b))
    S = np.array(S[trans:])
    s2 = np.max(np.abs(S[2:,:]-S[:-2,:]), axis=0)
    s4 = np.max(np.abs(S[4:,:]-S[:-4,:]), axis=0)
    return (s4 < tol) & (s2 >= tol), S

# --- 1) 2-site orbit from generic initial condition
a0, b0 = 0.3, 0.7
is_p4, S = p4check2(a0, b0)
print("2-site map P4 (a0,b0)=(%.2f,%.2f):" % (a0,b0), "is_P4 =", bool(np.all(is_p4)))
# extract the 4 phases (a,b)
ph = [tuple(S[i]) for i in range(4)]
print("  2-site P4 phases (a,b):")
for i,p in enumerate(ph): print("    t=%d  a=%.8f  b=%.8f" % (i, p[0], p[1]))

# --- 2) compare with N=120 lattice even/odd phases
def coupled(x, r, eps):
    ff = r*x*(1.0-x)
    return (1.0-eps)*ff + (eps/2.0)*(np.roll(ff,1)+np.roll(ff,-1))
np.random.seed(0)
x = np.random.rand(120)
for _ in range(15000): x = coupled(x, r, eps)
phL = [x.copy() for _ in range(4)]
for _ in range(4): x = coupled(x, r, eps)
a_latt = phL[0][0::2]; b_latt = phL[0][1::2]
print("\nLattice even-sublattice phase0: a=%.8f  (min %.8f, max %.8f)" % (a_latt.mean(), a_latt.min(), a_latt.max()))
print("Lattice odd-sublattice  phase0: b=%.8f  (min %.8f, max %.8f)" % (b_latt.mean(), b_latt.min(), b_latt.max()))
print("2-site orbit            : a=%.8f  b=%.8f" % (ph[0][0], ph[0][1]))
print("match within tol:", np.max(np.abs(a_latt - ph[0][0])) < 1e-6, np.max(np.abs(b_latt - ph[0][1])) < 1e-6)

# --- 3) 2-site cycle Jacobian vs lattice dominant eigenvalue
def J2(a, b):
    fa, fb = f(a), f(b)
    # d/d(a,b):  row a': d a'/da = (1-eps) r(1-2a) + eps r(1-2b) ; d a'/db = (1-eps) r(1-2b)? no
    # a' = (1-eps) f(a) + eps f(b)  => da'/da = (1-eps) r(1-2a), da'/db = eps r(1-2b)
    # b' = (1-eps) f(b) + eps f(a)  => db'/da = eps r(1-2a),      db'/db = (1-eps) r(1-2b)
    return np.array([[(1-eps)*r*(1-2*a), eps*r*(1-2*b)],
                     [eps*r*(1-2*a),     (1-eps)*r*(1-2*b)]])
Js = [J2(*ph[i]) for i in range(4)]
Jc = Js[3] @ Js[2] @ Js[1] @ Js[0]
ev = np.linalg.eigvals(Jc)
print("\n2-site cycle Jacobian eigenvalues:", np.round(ev, 6), " max|.|=%.6f" % np.max(np.abs(ev)))
print("Lattice dominant |lambda| was 0.908973 (computed on N=120)")

# --- 4) eps extent of the tongue at r=3.865 (N=120, seeded random init)
print("\neps scan at r=3.865 (lattice P4 fraction, N=120):")
res = []
for e in np.arange(0.05, 0.30, 0.01):
    np.random.seed(7)
    xx = np.random.rand(120)
    for _ in range(8000): xx = coupled(xx, r, e)
    S = np.empty((48,120))
    for t in range(48):
        xx = coupled(xx, r, e); S[t]=xx
    s2 = np.max(np.abs(S[2:,:]-S[:-2,:]),axis=0)
    s4 = np.max(np.abs(S[4:,:]-S[:-4,:]),axis=0)
    p4 = int(np.sum((s2>=1e-9)&(s4<1e-9)))
    res.append((e, p4/120))
for e,fr in res: print("  eps=%.2f  P4frac=%.2f" % (e,fr))
