#!/usr/bin/env python3
"""
A period-discriminating diagnostic for the coupled logistic CML.
Goal: definitively tell apart a true period-4 (P4) temporal state from a
period-2 antiphase checkerboard (P2c), which my earlier C4 metric confuses.

Signatures:
  (1) SINGLE-SITE period-4 signature: fraction of (site,t) where bit_{t+2} != bit_t.
      Pure P2 checkerboard -> every site alternates 010101 so bit_{t+2}==bit_t
      for all sites => signature ~ 0. A true P4 orbit on a single site cycles
      through 4 values, so bit_{t+2} != bit_t on roughly half the steps => ~0.5.
  (2) motif(t)==motif(t+2) : 1.0 for P2 checkerboard; <1 for a true P4.
  (3) Spatial two-point C(d) = <b_i b_j> - 0.25 : strong negative C(1) => antiphase.
"""
import numpy as np

def step(x, r, eps):
    fx = r * x * (1.0 - x)
    return (1.0 - eps) * fx + 0.5 * eps * (np.roll(fx, 1) + np.roll(fx, -1))

def run(r, eps, seed, tau=10000, T=3000, N=100):
    np.random.seed(seed)
    x = np.random.rand(N)
    for _ in range(tau):
        x = step(x, r, eps)
    traj = []
    for _ in range(T):
        x = step(x, r, eps)
        traj.append(x.copy())
    traj = np.array(traj)
    b = (traj > np.median(traj)).astype(float)
    return b

def p4_signature(b):
    return float((b[2:] != b[:-2]).mean())

def motif_lag2(b):
    motifs = [b[t, :4].tobytes() for t in range(b.shape[0])]
    m = len(motifs)
    return sum(1 for t in range(m - 2) if motifs[t] == motifs[t + 2]) / (m - 2)

def spatial_corr(b, max_d=6):
    T, N = b.shape
    cc = {}
    for d in range(1, max_d + 1):
        a = b[:, :N - d]
        c_ = b[:, d:N]
        cc[d] = float(np.mean(a * c_) - 0.25)
    return cc

def report(r, eps, seed, label=''):
    b = run(r, eps, seed)
    sig = p4_signature(b)
    m2 = motif_lag2(b)
    cc = spatial_corr(b)
    print(f"\n=== {label}  (r={r}, eps={eps}, seed={seed}) ===")
    print(f"  single-site P4-signature  = {sig:.3f}   [0=pure P2, ~0.5=true P4]")
    print(f"  motif(t)==motif(t+2)      = {m2:.3f}   [1.0 = P2 checkerboard]")
    print("  spatial C(d)  " + "  ".join(f"d{k}:{v:+.2f}" for k, v in cc.items()))

report(3.88, 0.145, 42, "tongue core")
report(3.865, 0.132, 42, "world-B point")
report(3.94, 0.25, 42, "chaotic corner")
report(3.5, 0.1, 42, "low-r reference")
