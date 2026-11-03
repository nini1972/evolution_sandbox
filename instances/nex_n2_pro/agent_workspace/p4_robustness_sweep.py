#!/usr/bin/env python3
"""Robustness: is 'float period-4 -> binary(period-2)' a tongue-wide phenomenon?
For a grid of (r,eps) in the P4 window, compute:
  - float period: does S4==S0 (to tol) while S2!=S0?  => genuine P4
  - binary period under global-median thresholding => P2 or P4?
  - the 'degeneracy gap' |S2-S0| (how close the two near-identical states are)
"""
import numpy as np
import json, os

def step(x, r, eps):
    fx = r * x * (1.0 - x)
    return (1.0 - eps) * fx + 0.5 * eps * (np.roll(fx, 1) + np.roll(fx, -1))

N, seed, T_settle, T_rec = 100, 42, 2000, 2000

def analyze(r, eps):
    np.random.seed(seed)
    x = np.random.rand(N)
    for _ in range(T_settle):
        x = step(x, r, eps)
    # record 4 consecutive states for float-period test
    S0 = x.copy(); x=step(x,r,eps); S1=x.copy(); x=step(x,r,eps); S2=x.copy(); x=step(x,r,eps); S3=x.copy()
    x4 = step(step(step(step(S0,r,eps),r,eps),r,eps),r,eps)
    d4 = np.max(np.abs(x4-S0))          # ~0 => returns in 4
    d2 = np.max(np.abs(S2-S0))          # >0 => not period 2
    float_period4 = (d4 < 1e-6) and (d2 > 1e-3)
    # long trajectory for binary (global median) period
    traj = np.empty((T_rec, N))
    t = S3
    for k in range(T_rec):
        t = step(t, r, eps)
        traj[k] = t
    gmed = np.median(traj)
    bits = (traj > gmed)
    # binary lag-match on full bit vector
    m1 = (bits[1:] == bits[:-1]).all(axis=1).mean()
    m2 = (bits[2:] == bits[:-2]).all(axis=1).mean()
    m4 = (bits[4:] == bits[:-4]).all(axis=1).mean()
    binary_period = 1 if m1>0.99 else (2 if m2>0.99 and m1<0.01 else (4 if m4>0.99 and m2<0.5 else 'chaos/mixed'))
    # degenerate gap between the two near-identical states
    degen_gap = d2
    return dict(r=r, eps=eps, float_period4=bool(float_period4), d4=float(d4), d2=float(d2),
                binary_period=binary_period, m1=float(m1), m2=float(m2), m4=float(m4), degen_gap=float(degen_gap))

# Grid across the P4 window. r in [3.86,3.96], eps in [0.12,0.16] (the census P4 region).
rs = [3.860, 3.865, 3.875, 3.900, 3.915, 3.925, 3.940, 3.950, 3.955]
es = [0.120, 0.126, 0.132, 0.138, 0.144, 0.152, 0.158]

results = []
for r in rs:
    for e in es:
        results.append(analyze(r, e))

# Table
print(f"{'r':>6} {'eps':>6} {'floatP4':>8} {'d2(max|S2-S0|)':>14} {'binary':>10} {'m2bin':>7}")
for z in results:
    fp = 'YES' if z['float_period4'] else '-'
    bp = z['binary_period']
    print(f"{z['r']:>6.3f} {z['eps']:>6.3f} {fp:>8} {z['d2']:>14.5f} {str(bp):>10} {z['m2']:>7.3f}")

# Summary statistics
fp_yes = [z for z in results if z['float_period4']]
both = [z for z in results if z['float_period4'] and z['binary_period']==2]
print("\n=== SUMMARY ===")
print(f"total points: {len(results)}")
print(f"float period-4 points: {len(fp_yes)}")
print(f"float P4 AND binary P2 (hidden-P4): {len(both)}")
if both:
    gaps = [z['d2'] for z in both]
    print(f"degeneracy gap |S2-S0|: min={min(gaps):.5f} max={max(gaps):.5f} mean={np.mean(gaps):.5f}")
print("NOTE: float P4 + binary P2 = the signature: binarization HIDES the true period-4.")

os.makedirs('p4_robustness', exist_ok=True)
with open('p4_robustness/p4_float_vs_binary_grid.json','w') as f:
    json.dump(results, f, indent=2)
print("saved p4_robustness/p4_float_vs_binary_grid.json")
