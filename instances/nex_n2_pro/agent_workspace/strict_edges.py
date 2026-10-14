#!/usr/bin/env python3
"""STRICT edge scan: count P2 (s2<tol, s4<tol) vs TRUE P4 (s2>=tol, s4<tol)
vs higher/aperiodic. This disambiguates period-4 from period-2 division."""
import numpy as np

def coupled(x, r, eps):
    f = r*x*(1.0 - x)
    return (1.0 - eps)*f + (eps/2.0)*(np.roll(f,1) + np.roll(f,-1))

r, n = 3.865, 120
def scan(eps, seed=0, trans=10000, T=48):
    np.random.seed(seed)
    x = np.random.rand(n)
    for _ in range(trans):
        x = coupled(x, r, eps)
    S = np.empty((T, n))
    for t in range(T):
        x = coupled(x, r, eps); S[t] = x
    s2 = np.max(np.abs(S[2:, :] - S[:-2, :]), axis=0)
    s4 = np.max(np.abs(S[4:, :] - S[:-4, :]), axis=0)
    p2 = int(np.sum((s2 < 1e-9)))
    p4 = int(np.sum((s2 >= 1e-9) & (s4 < 1e-9)))
    higher = int(np.sum((s4 >= 1e-9) & (s8 < 1e-9))) if False else None
    s8 = np.max(np.abs(S[8:, :] - S[:-8, :]), axis=0)
    p8 = int(np.sum((s4 >= 1e-9) & (s8 < 1e-9)))
    aperi = int(np.sum(s8 >= 1e-9))
    return p2, p4, p8, aperi

print("  eps      P2/120  TRUE-P4/120  P8/120  aperi/120")
for e in (0.12, 0.125, 0.127, 0.128, 0.129, 0.13, 0.132, 0.135, 0.14, 0.142, 0.144, 0.145, 0.146, 0.148, 0.15):
    p2, p4, p8, ap = scan(e)
    print("  %-6.3f  %3d/120   %3d/120    %3d/120   %3d/120" % (e, p2, p4, p8, ap))
