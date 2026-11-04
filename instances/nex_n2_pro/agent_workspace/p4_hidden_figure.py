#!/usr/bin/env python3
"""Decisive figure: the HIDDEN period-4 mechanism.
The float P4 orbit is a 'two pairs of near-degenerate states':
  S0 ~ S2  (same checkerboard orientation, slightly different amplitude)
  S1 ~ S3  (opposite checkerboard orientation, slightly different amplitude)
Median binarization sees only checkerboard ORIENTATION (flips each step -> P2),
NOT the amplitude modulation -> it collapses P4 to P2. This is the 'hidden P4'.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

def step(x, r, eps):
    fx = r * x * (1.0 - x)
    return (1.0 - eps) * fx + 0.5 * eps * (np.roll(fx, 1) + np.roll(fx, -1))

N, r, eps, seed = 100, 3.865, 0.132, 42
np.random.seed(seed)
x = np.random.rand(N)
for _ in range(2000):
    x = step(x, r, eps)

# Four cycle states
S = [x.copy()]
for _ in range(3):
    x = step(x, r, eps); S.append(x.copy())
S0,S1,S2,S3 = S

gmed = np.median([np.median(v) for v in S])
# single-site time series (site 30, an even site) for ~8 periods
i = 30
ts = [S0[i], S1[i], S2[i], S3[i]]
# extend: step forward more
tss = [S0[i]]
cur = S0
for _ in range(15):
    cur = step(cur, r, eps); tss.append(cur[i])

fig, axes = plt.subplots(1, 3, figsize=(16, 5.2))

# --- Panel A: the four spatial states, two near-degenerate pairs ---
ax = axes[0]
idx = np.arange(N)
ax.plot(idx, S0, lw=1.6, color='#1f77b4', label=f'S0  (med {np.median(S0):.3f})')
ax.plot(idx, S2, lw=1.6, color='#1f77b4', ls='--', label=f'S2  (med {np.median(S2):.3f})  ≈ S0')
ax.plot(idx, S1, lw=1.6, color='#d62728', label=f'S1  (med {np.median(S1):.3f})')
ax.plot(idx, S3, lw=1.6, color='#d62728', ls='--', label=f'S3  (med {np.median(S3):.3f})  ≈ S1')
ax.set_title('A. Four float cycle states\n(blue pair ≈, red pair ≈ — "two near-identical states")', fontsize=10)
ax.set_xlabel('site'); ax.set_ylabel('x_i')
ax.set_ylim(0.3, 0.95); ax.legend(fontsize=8); ax.grid(alpha=0.3)

# --- Panel B: single-site time series: float P4 vs median-binarized P2 ---
ax = axes[1]
t = np.arange(len(tss))
ax.plot(t, tss, 'o-', color='#1f77b4', lw=1.6, ms=4, label='float x_30(t) — period 4')
ax.axhline(gmed, color='gray', ls=':', lw=1, label=f'median level {gmed:.3f}')
# binarized
bits = (np.array(tss) > gmed).astype(float)
ax.step(t, bits*0.0+0.5, where='post', color='none')
ax.plot(t, bits*0.55+0.40, lw=4, alpha=0.5, color='#d62728', label='median-binarized — period 2')
ax.set_title('B. One site, time axis\nfloat = 4 distinct levels; binary = only 2', fontsize=10)
ax.set_xlabel('time'); ax.set_ylabel('value / bit')
ax.set_ylim(0.30, 0.95); ax.legend(fontsize=8); ax.grid(alpha=0.3)
# annotate the 4 levels
for k,v in enumerate([ts[0],ts[1],ts[2],ts[3]]):
    ax.annotate(f'{v:.4f}', (k, v), textcoords='offset points', xytext=(6,6), fontsize=7, color='#1f77b4')

# --- Panel C: the collapse diagram ---
ax = axes[2]
ax.set_xlim(0,10); ax.set_ylim(0,10); ax.axis('off')
ax.set_title('C. Why binarization HIDES the period-4', fontsize=10)
# boxes for S0..S3
boxes = {
 'S0':(1.2,8.2,'#1f77b4'),'S2':(4.2,8.2,'#1f77b4'),
 'S1':(1.2,4.2,'#d62728'),'S3':(4.2,4.2,'#d62728')}
for name,(cx,cy,c) in boxes.items():
    ax.add_patch(plt.Rectangle((cx, cy), 2.2, 1.4, facecolor=c, alpha=0.85, ec='k', lw=1))
    ax.text(cx+1.1, cy+0.7, name, ha='center', va='center', color='white', fontsize=12, weight='bold')
# arrows to bit levels
def arrow(x0,y0,x1,y1,color):
    ax.add_patch(FancyArrowPatch((x0,y0),(x1,y1), arrowstyle='-|>', mutation_scale=16, color=color, lw=2))
arrow(2.3,8.2,7.0,9.0,'#1f77b4')   # S0 -> low
arrow(5.3,8.2,7.0,9.0,'#1f77b4')   # S2 -> low
arrow(2.3,4.2,7.0,5.0,'#d62728')   # S1 -> high
arrow(5.3,4.2,7.0,5.0,'#d62728')   # S3 -> high
# bit boxes
ax.add_patch(plt.Rectangle((7.0, 8.3), 2.4, 1.4, facecolor='white', ec='k', lw=1))
ax.text(8.2, 9.0, 'bit LOW', ha='center', va='center', fontsize=11, weight='bold')
ax.add_patch(plt.Rectangle((7.0, 4.3), 2.4, 1.4, facecolor='white', ec='k', lw=1))
ax.text(8.2, 5.0, 'bit HIGH', ha='center', va='center', fontsize=11, weight='bold')
ax.text(5.0, 2.3, 'S0≈S2  and  S1≈S3 differ only in AMPLITUDE;\n'
                 'the median threshold splits by VALUE, so each near-degenerate\n'
                 'pair lands on the SAME bit  →  symbolic orbit = period 2,\n'
                 'while the float orbit is period 4.',
        ha='center', va='center', fontsize=9, style='italic',
        bbox=dict(boxstyle='round,pad=0.4', fc='#fff7e6', ec='#e0a800', lw=1))

plt.tight_layout()
out = 'p4_hidden_mechanism.png'
plt.savefig(out, dpi=130, bbox_inches='tight')
print('saved', out)
print(f"median level = {gmed:.4f}")
print(f"4 float levels (site 30): {['%.4f'%v for v in ts]}")
print(f"|S2-S0|max = {np.max(np.abs(S2-S0)):.5f}  |S3-S1|max = {np.max(np.abs(S3-S1)):.5f}")
print(f"|S0-S1|max = {np.max(np.abs(S0-S1)):.5f}  (the two ANTI-correlated states are far apart)")
