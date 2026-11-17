#!/usr/bin/env python3
"""Inspect the 24 saved P4 attractors: value structure, even/odd parity,
period-4 closure, shift-lag (traveling wave) test, ASCII render, clustering."""
import numpy as np
def f(x, r): return r * x * (1.0 - x)
def coupled(x, r, eps):
    fx = f(x, r)
    return (1.0 - eps) * fx + 0.5 * eps * (np.roll(fx, 1) + np.roll(fx, -1))

import os
if os.path.exists("p4_attractors_24.npy"):
    P = np.load("p4_attractors_24.npy")
else:
    # re-lock the 24 attractors (same protocol as p4_family_visual.py)
    N = 120
    def _lock(r, eps, N, x0, trans=10000):
        x = x0.copy()
        for _ in range(trans):
            x = coupled(x, r, eps)
        Pm = np.empty((N, 4))
        for k in range(4):
            Pm[:, k] = x
            x = coupled(x, r, eps)
        return Pm
    r, eps = 3.87, 0.136
    rng = np.random.default_rng(7)
    P = np.stack([_lock(r, eps, N, rng.random(N)) for _ in range(24)])
    np.save("p4_attractors_24.npy", P)
N = P.shape[1]
print(f"P shape {P.shape}; min={P.min():.5f} max={P.max():.5f} mean={P.mean():.5f} std={P.std():.5f}")

# value histogram (are values bimodal?)
hist, edges = np.histogram(P, bins=12)
print("value hist:", dict(zip([f"{edges[i]:.2f}-{edges[i+1]:.2f}" for i in range(12)], hist.tolist())))

# --- per-attractor parity structure ---
print("\n--- parity structure (even/odd sites at each t) ---")
parity_stats = []
for a in range(P.shape[0]):
    row = []
    for t in range(4):
        ev, od = P[a, ::2, t], P[a, 1::2, t]
        row.append((ev.mean(), ev.std(), od.mean(), od.std()))
    parity_stats.append(row)
    if a < 4:
        print(f"att {a}: " + " | ".join(
            f"t{t}: ev({row[t][0]:.4f}±{row[t][1]:.2e}) od({row[t][2]:.4f}±{row[t][3]:.2e})"
            for t in range(4)))

# --- period-4 closure: iterate 4 more steps from P[a,:,3], compare to P[a,:,0] ---
print("\n--- period-4 closure (iterate 4 extra steps from t=3 state) ---")
for a in [0, 1, 5, 10]:
    x = P[a, :, 3].copy()
    for _ in range(4):
        x = coupled(x, r, eps)
    print(f"att {a}: max|x(t+4)-x(t)| = {np.max(np.abs(x - P[a, :, 0])):.3e}")

# --- shift-lag test: x_i(t+1) ~ x_{i+s}(t)? find best shift s per t ---
print("\n--- shift-lag test (best s in -4..4 for x[:,t+1] vs roll(x[:,t], s)) ---")
def d_orbit(Pt, Q):
    Nn = Pt.shape[0]; best = np.inf
    for p in range(4):
        Ppr = np.roll(Pt, p, axis=1)
        for s in range(Nn):
            d = float(np.max(np.abs(Ppr - np.roll(Q, s, axis=0))))
            if d < best: best = d
    return best
for a in [0, 1, 5, 10]:
    lags = []
    for t in range(3):
        best_s, best_d = 0, np.inf
        for s in range(-4, 5):
            d = float(np.max(np.abs(P[a, :, t + 1] - np.roll(P[a, :, t], s))))
            if d < best_d: best_d, best_s = d, s
        lags.append((best_s, best_d))
    print(f"att {a}: " + " ".join(f"t{t}->t{t+1}: s={s:+d} d={d:.2e}" for t, (s, d) in enumerate(lags)))

# --- pairwise d_orbit among 24 (full shift quotient) ---
print("\n--- pairwise d_orbit (min over site-shift & time-phase) ---")
D = np.zeros((24, 24))
for a in range(24):
    for b in range(24):
        D[a, b] = d_orbit(P[a], P[b])
off = D[np.triu_indices(24, 1)]
print("pairwise min/median/max:", off.min(), np.median(off), off.max())
# cluster: two attractors 'same' if d_orbit < 0.05
import sys
parent = list(range(24))
def find(i):
    while parent[i] != i: parent[i] = parent[parent[i]]; i = parent[i]
    return i
def uni(i, j):
    ri, rj = find(i), find(j)
    if ri != rj: parent[ri] = rj
for a in range(24):
    for b in range(a + 1, 24):
        if D[a, b] < 0.05: uni(a, b)
groups = {}
for a in range(24):
    groups.setdefault(find(a), []).append(a)
print(f"clusters (d_orbit<0.05): {len(groups)} -> sizes {sorted(len(v) for v in groups.values())}")

# --- ASCII render: 30 sites (every 4th) x 4 t, chars over [0.25, 0.95] ---
chars = " .:-=+*#%@"
def ch(v):
    idx = int(np.clip((v - 0.25) / (0.95 - 0.25), 0, 1) * (len(chars) - 1))
    return chars[idx]
print("\n--- ASCII render, att 0 (30 sites, t rows 0..3) ---")
sel = np.arange(0, N, 4)
for t in range(4):
    print(f"t{t}: " + "".join(ch(P[0, i, t]) for i in sel))
print("\n--- ASCII render, att 1 ---")
for t in range(4):
    print(f"t{t}: " + "".join(ch(P[1, i, t]) for i in sel))

# --- what does 'distinct' mean? compare att0 vs att1 value-by-value after best alignment ---
d01 = D[0, 1]
print(f"\nd_orbit(att0,att1)={d01:.4f}")
# best shift & phase alignment between att0, att1
best = (np.inf, None, None)
for p in range(4):
    P0p = np.roll(P[0], p, axis=1)
    for s in range(N):
        dd = float(np.max(np.abs(P0p - np.roll(P[1], s, axis=0))))
        if dd < best[0]: best = (dd, p, s)
print("best alignment att0 vs att1: d=%.4f p=%d s=%d" % best)
# where do they differ most under that alignment?
P0p = np.roll(P[0], best[1], axis=1)
Q1s = np.roll(P[1], best[2], axis=0)
diff = np.max(np.abs(P0p - Q1s), axis=1)   # per site
top = np.argsort(diff)[::-1][:12]
print("top-12 differing sites:", [(int(i), float(diff[i])) for i in top])
print("n sites with diff>0.1:", int((diff > 0.1).sum()), " / ", N)
np.save("p4_D24.npy", D)
print("saved p4_D24.npy")
