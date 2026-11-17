#!/usr/bin/env python3
"""Settle the period question definitively for the P4-tongue attractor at
(r=3.87, eps=0.136), N=120, seed 7 / first lock.
 - long transient (20000), then record 400 consecutive snapshots
 - minimal period: d_p = mean_t max_i |x_i(t+p)-x_i(t)| for p=1..8
 - per-cell local time series (first 6 cells): list distinct values visited
 - H-site set drift: track which sites are H (>0.675) over time; measure
   nearest-site displacement of the H-set (drift / rotation speed)
 - check t0==t2 vs t0==t4 explicitly (the 2-vs-4 discriminator)
"""
import numpy as np
def f(x, r): return r * x * (1.0 - x)
def coupled(x, r, eps):
    fx = f(x, r)
    return (1.0 - eps) * fx + 0.5 * eps * (np.roll(fx, 1) + np.roll(fx, -1))

r, eps, N = 3.87, 0.136, 120
rng = np.random.default_rng(7)
x = rng.random(N)
TRANS = 20000
for _ in range(TRANS):
    x = coupled(x, r, eps)

T = 400
X = np.empty((T, N))
X[0] = x
for t in range(1, T):
    x = coupled(x, r, eps)
    X[t] = x

# --- minimal period: d_p over t in [50, T-1-p] ---
print("=== minimal period (d_p = mean_t max_i |x_i(t+p)-x_i(t)|) ===")
for p in range(1, 9):
    d = np.array([np.max(np.abs(X[t + p] - X[t])) for t in range(50, T - p)])
    print(f"p={p}: d_p = {d.mean():.3e}   (median {np.median(d):.3e}, max {d.max():.3e})")

# --- explicit 2-vs-4 discriminator at a fixed t ---
print("\n=== explicit phase comparison (t=100) ===")
base = X[100]
for q in [1, 2, 3, 4, 6, 8]:
    print(f"|x(t+{q}) - x(t)| max = {np.max(np.abs(X[100 + q] - base)):.3e}")

# --- per-cell local distinct values (cells 0..7), over t in [100,300] ---
print("\n=== per-cell local dynamics (distinct values, 2-decimal, cells 0..7) ===")
for i in range(8):
    col = X[100:300, i]
    # cluster values into bins of width 0.05
    bins = np.round(col * 20) / 20
    vals, counts = np.unique(bins, return_counts=True)
    top = sorted(zip(counts, vals), reverse=True)[:4]
    print(f"cell {i:3d}: " + "  ".join(f"{v:.2f}({c})" for c, v in top) +
          f"   | range {col.min():.3f}..{col.max():.3f}")

# --- H-set drift: sites with x>0.675 at each t; track centroid + rotation ---
print("\n=== H-set (>0.675) tracking: count, centroid, and 1-step H/L flip fraction ===")
Hmask = X > 0.675
counts = Hmask.sum(axis=1)
print("H count over t (every 25):", [(t, int(counts[t])) for t in range(0, T, 25)])
# how many H sites stay H at t+1 (no flip) vs flip to L
flip_frac = []
for t in range(100, 300):
    stay = (Hmask[t] & Hmask[t + 1]).sum()
    flip = (Hmask[t] & ~Hmask[t + 1]).sum()
    flip_frac.append(flip / max(1, Hmask[t].sum()))
print(f"fraction of H sites that FLIP to L at next step: mean={np.mean(flip_frac):.3f} "
      f"(0=static, 1=full inversion each step)")

# L->H flip too
flip_frac_lh = []
for t in range(100, 300):
    Lm = ~Hmask[t]
    flip = (Lm & Hmask[t + 1]).sum()
    flip_frac_lh.append(flip / max(1, Lm.sum()))
print(f"fraction of L sites that FLIP to H at next step: mean={np.mean(flip_frac_lh):.3f}")

# --- is the H-set slowly rotating? match H-set at t to nearest H at t+20 ---
def h_sites(t): return np.where(Hmask[t])[0]
def min_circ_dist(a, b, N):
    return np.min(np.abs(np.roll(-b, a) - 0), axis=None) if False else None
# centroid position (circular)
print("\nH-set circular centroid (deg) every 50 steps:")
for t in range(0, T, 50):
    s = h_sites(t)
    if len(s):
        ang = 2 * np.pi * s / N
        cen = np.angle(np.exp(1j * ang).mean()) / (2 * np.pi) * N
        print(f"  t={t:3d}: n_H={len(s):3d} centroid={cen:6.1f}")

np.save("p4_long_traj.npy", X)
print("\nsaved p4_long_traj.npy (400 x 120)")
