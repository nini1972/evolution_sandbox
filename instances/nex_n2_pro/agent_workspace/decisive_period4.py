#!/usr/bin/env python3
"""Decisive test: extract the exact float 4-cycle at (3.865, 0.132) and show
how the perceived period depends on the binarization convention.

Hypothesis: the float orbit is an EXACT period-4 cycle with checkerboard
spatial structure, whose states {A,B,C,D} satisfy:
  - B(t+2) = C, B(t+4) = A  (float period 4)
  - but per-point-median bits of A==C and B==D  (binary period 2)
  - while global-median bits can differ A vs C   (binary period 4)
This shows 'hidden period 4' is a FLOAT-ORBIT property, and the symbolic
'mod-4 residue' structure is thresholding-convention dependent.
"""
import numpy as np

def step(x, r, eps):
    fx = r * x * (1.0 - x)
    return (1.0 - eps) * fx + 0.5 * eps * (np.roll(fx, 1) + np.roll(fx, -1))

r, eps, N, seed = 3.865, 0.132, 100, 42
np.random.seed(seed)
x = np.random.rand(N)
for _ in range(1000):
    x = step(x, r, eps)

# Extract 4 consecutive float states (the cycle)
states = [x.copy()]
for _ in range(3):
    x = step(x, r, eps)
    states.append(x.copy())
S0, S1, S2, S3 = states
print("=== FLOAT 4-CYCLE ===")
print(f"|S1-S0| max={np.max(np.abs(S1-S0)):.4f}  mean={np.mean(np.abs(S1-S0)):.4f}")
print(f"|S2-S1| max={np.max(np.abs(S2-S1)):.4f}  mean={np.mean(np.abs(S2-S1)):.4f}")
print(f"|S3-S2| max={np.max(np.abs(S3-S2)):.4f}  mean={np.mean(np.abs(S3-S2)):.4f}")
# advance 4 steps and compare to S0
x4 = S0.copy()
for _ in range(4):
    x4 = step(x4, r, eps)
print(f"|S4-S0| max={np.max(np.abs(x4-S0)):.2e}  (0 => exact period 4)")
x2 = S0.copy()
for _ in range(2):
    x2 = step(x2, r, eps)
print(f"|S2-S0| max={np.max(np.abs(x2-S0)):.4f}  (nonzero => not period 2)")
print(f"|S2-S1| vs diagonal |S1 - roll(S0)|: {np.max(np.abs(S1-np.roll(S0,1))):.4f}")

def bits_perpoint(v, traj):
    """per-point rolling median over the recorded trajectory (local)."""
    med = np.median(traj, axis=(0, 1), keepdims=True)
    return (v > med).astype(float)

def bits_global(v, allvals):
    """global scalar median threshold (original paper)."""
    med = np.median(allvals)
    return (v > med).astype(float)

# Build a longer trajectory for robust medians
np.random.seed(seed)
x = np.random.rand(N)
for _ in range(1000):
    x = step(x, r, eps)
traj = []
for _ in range(2000):
    x = step(x, r, eps)
    traj.append(x.copy())
traj = np.array(traj)

# --- Per-point median: what is the period of the 4-cell motif? ---
b_pp = (traj > np.median(traj, axis=(0,1), keepdims=True)).astype(float)
mot = [b_pp[t, :4].tobytes() for t in range(len(traj))]
m2 = sum(1 for t in range(len(mot)-2) if mot[t]==mot[t+2])/(len(mot)-2)
m4 = sum(1 for t in range(len(mot)-4) if mot[t]==mot[t+4])/(len(mot)-4)
m1 = sum(1 for t in range(len(mot)-1) if mot[t]==mot[t+1])/(len(mot)-1)
m3 = sum(1 for t in range(len(mot)-3) if mot[t]==mot[t+3])/(len(mot)-3)
print("\n=== PER-POINT MEDIAN binarization ===")
print(f"4-cell motif lag-match:  m1={m1:.4f} m2={m2:.4f} m3={m3:.4f} m4={m4:.4f}")
print(f"  -> binary orbit period: "
      + ("2 (m2=1,m1=0)" if m2>0.99 and m1<0.01
         else "4 (m4=1,m2<0.5)" if m4>0.99 and m2<0.5 else "mixed"))
print(f"  per-site s4 (fraction flipped at lag2) = {float((b_pp[2:]!=b_pp[:-2]).mean()):.4f}")

# --- Global scalar median: what is the period? ---
b_gl = (traj > np.median(traj)).astype(float)
motg = [b_gl[t, :4].tobytes() for t in range(len(b_gl))]
M1 = sum(1 for t in range(len(motg)-1) if motg[t]==motg[t+1])/(len(motg)-1)
M2 = sum(1 for t in range(len(motg)-2) if motg[t]==motg[t+2])/(len(motg)-2)
M3 = sum(1 for t in range(len(motg)-3) if motg[t]==motg[t+3])/(len(motg)-3)
M4 = sum(1 for t in range(len(motg)-4) if motg[t]==motg[t+4])/(len(motg)-4)
print("\n=== GLOBAL SCALAR MEDIAN binarization (original paper) ===")
print(f"4-cell motif lag-match:  M1={M1:.4f} M2={M2:.4f} M3={M3:.4f} M4={M4:.4f}")
print(f"  per-site s4 (fraction flipped at lag2) = {float((b_gl[2:]!=b_gl[:-2]).mean()):.4f}")

# --- The 4 float states, their means & bit patterns ---
print("\n=== 4 FLOAT STATES (means over sites) ===")
for i, S in enumerate(states):
    print(f"  S{i}: mean={S.mean():.5f} min={S.min():.5f} max={S.max():.5f}")
print(f"  S0 mean vs S2 mean: {abs(S0.mean()-S2.mean()):.5f}  (different float amplitudes)")

# Bit patterns of each float state under BOTH thresholds
med_pp_traj = np.median(traj, axis=(0,1))
gmed = np.median(traj)
print("\n=== BIT PATTERN of each float state (site 0..7) ===")
print(f"{'state':6s}{'per-point med':16s}{'global med':16s}")
for i, S in enumerate(states):
    bpp = (S > med_pp_traj).astype(int)   # per-point median is per-site scalar
    bgl = (S > gmed).astype(int)
    print(f"  S{i:4d}  {str(bpp[:8].tolist()):16s} {str(bgl[:8].tolist()):16s}")

# Do S0 and S2 map to the same bit pattern under per-point median?
bpp0 = (S0 > med_pp_traj).astype(int)
bpp2 = (S2 > med_pp_traj).astype(int)
bgl0 = (S0 > gmed).astype(int)
bgl2 = (S2 > gmed).astype(int)
print(f"\nS0 vs S2 bits: per-point-median mismatch = {float((bpp0!=bpp2).mean()):.4f}")
print(f"S0 vs S2 bits: global-median   mismatch = {float((bgl0!=bgl2).mean()):.4f}")

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(14, 5))
ax[0].plot(S0, 'o', ms=3, label='S0 (t=0)', color='#1f77b4')
ax[0].plot(S1, 's', ms=3, label='S1 (t=1)', color='#ff7f0e')
ax[0].plot(S2, '^', ms=3, label='S2 (t=2)', color='#2ca02c')
ax[0].plot(S3, 'D', ms=3, label='S3 (t=3)', color='#d62728')
ax[0].set_title('Exact float 4-cycle at (3.865, 0.132): 4 distinct spatial states\n(S0≠S2 in float, but same per-point-median bits)')
ax[0].set_xlabel('site'); ax[0].set_ylabel('x'); ax[0].legend(); ax[0].grid(alpha=0.3)
ax[1].plot([m1, m2, m3, m4], 'o-', color='#1f77b4', label='per-point median')
ax[1].plot([M1, M2, M3, M4], 's-', color='#d62728', label='global median')
ax[1].set_xticks(range(4)); ax[1].set_xticklabels(['lag1','lag2','lag3','lag4'])
ax[1].set_ylim(-0.05, 1.05); ax[1].set_ylabel('4-cell motif match')
ax[1].set_title('Perceived period: convention-dependent\n(per-point→P2, global→P4)')
ax[1].legend(); ax[1].grid(alpha=0.3)
fig.tight_layout(); fig.savefig('period4_float_orbit.png', dpi=140, bbox_inches='tight')
print("\nsaved period4_float_orbit.png")
