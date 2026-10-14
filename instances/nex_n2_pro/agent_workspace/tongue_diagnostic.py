#!/usr/bin/env python3
"""DIAGNOSTIC: is the locked P4 state an ISOLATED orbit or a MANIFOLD of
coexisting period-4 orbits? Plus spatial frequency structure.

Part A. Three independent seeds, 20000 transients each, at (r=3.865, eps=0.132).
        Compare the resulting 120-cell spatial profiles (4-tuple per cell).
        max distance between profiles -> 0 => unique attractor.
Part B. Perturbation test: take seed-0 locked state, add 1e-3 noise, iterate
        20000 steps. If profile returns to the same shape -> isolated orbit.
        If it drifts to a different (but still P4) profile -> manifold.
Part C. Spatial spectrum of the locked profile (phase 0): FFT of x_i over
        the ring; report dominant wavenumbers. Also test the standing-wave
        hypothesis: correlation of profile with its 4-site shift.
"""
import numpy as np

def coupled(x, r, eps):
    f = r*x*(1.0 - x)
    return (1.0 - eps)*f + (eps/2.0)*(np.roll(f,1) + np.roll(f,-1))

def run(n, r, eps, trans, seed):
    np.random.seed(seed)
    x = np.random.rand(n)
    for _ in range(trans):
        x = coupled(x, r, eps)
    return x

r, eps, n = 3.865, 0.132, 120

# ---------- Part A: seed dependence ----------
print("=== Part A: attractor uniqueness (3 seeds, 20000 transients) ===")
profiles = []
for s in (0, 1, 2):
    x = run(n, r, eps, 20000, s)
    P = np.empty((n, 4))
    for k in range(4):
        P[:, k] = x
        x = coupled(x, r, eps)
    profiles.append(P)
    spl = np.median(np.abs(P[:, 0] - P[:, 2]))
    print("  seed %d : median|A-C|=%.3e  profile head=%s" %
          (s, spl, " ".join("%.4f" % a for a in P[0])))
d01 = float(np.max(np.abs(profiles[0] - profiles[1])))
d02 = float(np.max(np.abs(profiles[0] - profiles[2])))
d12 = float(np.max(np.abs(profiles[1] - profiles[2])))
print("  max |P0-P1| = %.3e" % d01)
print("  max |P0-P2| = %.3e" % d02)
print("  max |P1-P2| = %.3e" % d12)

# ---------- Part B: perturbation response ----------
print()
print("=== Part B: 1e-3 perturbation of seed-0 locked state ===")
x = run(n, r, eps, 20000, 0)
P0 = profiles[0].copy()
np.random.seed(99)
x = x + 1e-3*(np.random.rand(n) - 0.5)
for _ in range(20000):
    x = coupled(x, r, eps)
P1 = np.empty((n, 4))
for k in range(4):
    P1[:, k] = x
    x = coupled(x, r, eps)
# compare with and without a global 4-phase alignment (min over phase shifts)
best = 1e9
for sh in range(4):
    d = float(np.max(np.abs(P1 - np.roll(P0, sh, axis=1))))
    best = min(best, d)
print("  max |P_pert - P0| (min over phase shift) = %.3e" % best)
print("  P_pert head = " + " ".join("%.4f" % a for a in P1[0]))

# ---------- Part C: spatial spectrum of seed-0 profile ----------
print()
print("=== Part C: spatial FFT of locked profile (phase 0, seed 0) ===")
u = profiles[0][:, 0].astype(float)
u0 = u - u.mean()
sp = np.abs(np.fft.rfft(u0))**2
freqs = np.fft.rfftfreq(n, d=1.0/n)   # wavenumber = sites per ring period
order = np.argsort(sp)[::-1]
print("  top-8 spatial wavenumbers (k, power, wavelength L):")
for i in order[:8]:
    print("    k=%2d  power=%.3e  wavelength=%.1f" % (freqs[i], sp[i], n/freqs[i] if freqs[i] else float('inf')))
# standing-wave test: correlation of profile with 4-site shift
u4 = np.roll(u, 4)
corr4 = float(np.corrcoef(u0, u4 - u4.mean())[0, 1])
corr1 = float(np.corrcoef(u0, np.roll(u,1) - np.roll(u,1).mean())[0, 1])
print("  corr(profile, profile shifted by 4 sites) = %.4f" % corr4)
print("  corr(profile, profile shifted by 1 site)  = %.4f" % corr1)
