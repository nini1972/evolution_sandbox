#!/usr/bin/env python3
"""
Local instrument test: what does binarized phase-velocity LZ complexity
ACTUALLY do across K, with a working guard and a working LZ76?

Signals compared per K:
  A. mean-removed increments  sign(dtheta_i - mean_j dtheta_j)  (physical intent)
  B. lab-frame increments     sign(dtheta_i)                     (Entry #001's math)

Entry #001 claimed LZ == 0 exactly for ALL K ("flatline phenomenon").
We test whether ANY working instrument reproduces that.
"""
import numpy as np

def lz76(sequence):
    s = ''.join(map(str, sequence))
    n = len(s)
    if n <= 1:
        return 0.0
    seen, w, c = set(), '', 0
    for ch in s:
        if w + ch in seen:
            w += ch
        else:
            seen.add(w + ch); c += 1; w = ch
    return c / (n / np.log2(n))

def run_kuramoto(K, N=50, T=100.0, dt=0.01, sigma=0.1, seed=42):
    rng = np.random.default_rng(seed)
    omega = rng.normal(0.0, sigma, N)
    th = rng.uniform(0, 2 * np.pi, N)
    steps = int(T / dt)
    incs = np.empty((steps, N))
    for s in range(steps):
        z = np.mean(np.exp(1j * th)); psi = np.angle(z); R = np.abs(z)
        dth = omega + K * R * np.sin(psi - th)
        th = th + dth * dt
        incs[s] = dth
    return incs, th

def to_bits(mask):
    return ''.join('1' if v else '0' for v in mask.ravel())

Ks = [0.0, 0.1, 0.2, 0.5, 1.0, 2.0]
print(f"{'K':>5} {'R':>6} {'A_rel_inc':>10} {'B_lab_inc':>10}")
for K in Ks:
    incs, th = run_kuramoto(K)
    incs = incs[int(len(incs) * 0.66):]      # drop transient
    mean_inc = incs.mean(axis=1, keepdims=True)
    A = lz76(to_bits(incs - mean_inc > 0))
    B = lz76(to_bits(incs > 0))
    R = abs(np.mean(np.exp(1j * th)))
    print(f"{K:5.2f} {R:6.3f} {A:10.4f} {B:10.4f}")

print()
print("Entry #001 reported: LZ == 0.0000 exactly at every K.")
print("Working instruments give the values above (no flatline at 0).")