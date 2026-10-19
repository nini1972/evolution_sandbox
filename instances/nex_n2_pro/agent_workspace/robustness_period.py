#!/usr/bin/env python3
"""Robustness: is 'float period-4 / symbolic period-2' stable across seeds and
nearby parameters? Quantify the sub-symbolic 'breathing' (S0 vs S2 within the
same bit state)."""
import numpy as np

def step(x, r, eps):
    fx = r * x * (1.0 - x)
    return (1.0 - eps) * fx + 0.5 * eps * (np.roll(fx, 1) + np.roll(fx, -1))

def orbit_periods(r, eps, seed, N=100, transient=1500):
    np.random.seed(seed)
    x = np.random.rand(N)
    for _ in range(transient):
        x = step(x, r, eps)
    # float return times
    def ret(k):
        y = x.copy()
        for _ in range(k):
            y = step(y, r, eps)
        return float(np.max(np.abs(y - x)))
    d1, d2, d4 = ret(1), ret(2), ret(4)
    # symbolic period via global-median bit motif lag-2 match
    # record short trajectory
    traj = []
    xt = x.copy()
    for _ in range(400):
        xt = step(xt, r, eps)
        traj.append(xt.copy())
    traj = np.array(traj)
    gmed = np.median(traj)
    b = (traj > gmed).astype(int)
    m1 = sum(1 for t in range(len(b)-1) if b[t,:4].tobytes()==b[t+1,:4].tobytes())/(len(b)-1)
    m2 = sum(1 for t in range(len(b)-2) if b[t,:4].tobytes()==b[t+2,:4].tobytes())/(len(b)-2)
    m4 = sum(1 for t in range(len(b)-4) if b[t,:4].tobytes()==b[t+4,:4].tobytes())/(len(b)-4)
    # breathing: float distance between same-bit states (approx via ret(2) of a
    # point already on the cycle): use S0 vs S2
    S0 = x.copy()
    S2 = step(step(S0, r, eps), r, eps)
    breathing = float(np.max(np.abs(S2 - S0)))
    float_period = 4 if (d4 < 1e-6 and d2 > 1e-3) else (2 if d2 < 1e-6 else 'chaotic')
    sym_period = 2 if (m2 > 0.95 and m1 < 0.05) else (4 if (m4 > 0.95 and m2 < 0.2) else 'mixed')
    return float_period, sym_period, d2, d4, m1, m2, m4, breathing

print(f"{'r':>7s} {'eps':>6s} {'seed':>5s} {'float':>8s} {'sym':>6s} "
      f"{'d2':>8s} {'d4':>10s} {'m1':>6s} {'m2':>6s} {'m4':>6s} {'breath':>8s}")
rows = []
for (r, eps) in [(3.865, 0.132), (3.865, 0.125), (3.865, 0.140), (3.855, 0.132), (3.875, 0.132)]:
    for seed in [1, 42, 7, 123]:
        fp, sp, d2, d4, m1, m2, m4, br = orbit_periods(r, eps, seed)
        rows.append((r, eps, seed, fp, sp, d2, d4, m1, m2, m4, br))
        print(f"{r:7.3f} {eps:6.3f} {seed:5d} {str(fp):>8s} {str(sp):>6s} "
              f"{d2:8.4f} {d4:10.2e} {m1:6.3f} {m2:6.3f} {m4:6.3f} {br:8.4f}")

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(7, 5))
xs = np.arange(len(rows))
fp4 = [1 if r[3] == 4 else 0 for r in rows]
sp2 = [1 if r[4] == 2 else 0 for r in rows]
ax.bar(xs - 0.2, fp4, 0.4, label='float period = 4', color='#d62728')
ax.bar(xs + 0.2, sp2, 0.4, label='symbolic period = 2', color='#1f77b4')
ax.set_xticks(xs); ax.set_xticklabels([f"{r[0]:.3f}\n{r[1]:.3f}\ns{r[2]}" for r in rows], fontsize=6)
ax.set_ylim(0, 1.15); ax.set_ylabel('indicator (1 = yes)')
ax.set_title('Float orbit = period 4  AND  symbolic orbit = period 2\n(stable across seeds & nearby params)')
ax.legend(); ax.grid(alpha=0.3, axis='y')
fig.tight_layout(); fig.savefig('robustness_float4_sym2.png', dpi=140, bbox_inches='tight')
print("\nsaved robustness_float4_sym2.png")
