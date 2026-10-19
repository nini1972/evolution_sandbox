#!/usr/bin/env python3
"""
True periodicity landscape of the coupled logistic CML (N=100), using
period-DISCRIMINATING diagnostics that cannot confuse P2 with P4:

  m2   = motif-lag-2 consistency   (4-site motif; 1.0 => P2 temporal state)
  m4   = motif-lag-4 consistency
  m8   = motif-lag-8 consistency
  s4   = single-site P4 signature = P(bit_{t+2} != bit_t)
         (0 => pure P2; ~0.5 => genuine 4-cycle on a single site)
  C1   = spatial two-point correlation at d=1  (<0 => antiphase checkerboard)
  C2   = spatial two-point correlation at d=2
  d4   = distinct-motif share (chaos indicator)

Classification:
  P2c : m2>0.99 and s4<0.02 and C1<-0.08   (period-2 antiphase checkerboard)
  P2  : m2>0.99 and s4<0.02 and C1>=-0.08  (period-2 in-phase/other)
  P4  : m2<0.90 and m4>0.90                (true period-4)
  P8  : m2<0.90 and m4<0.90 and m8>0.90    (period-8)
  MISC: everything else (mixed/chaotic)
"""
import numpy as np
import json
from collections import Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def step(x, r, eps):
    fx = r * x * (1.0 - x)
    return (1.0 - eps) * fx + 0.5 * eps * (np.roll(fx, 1) + np.roll(fx, -1))

def diagnostics(r, eps, seed=42, tau=6000, T=2000, N=100):
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
    motifs = [b[t, :4].tobytes() for t in range(T)]
    def lagmatch(l):
        return sum(1 for t in range(T - l) if motifs[t] == motifs[t + l]) / (T - l)
    m2, m4, m8 = lagmatch(2), lagmatch(4), lagmatch(8)
    s4 = float((b[2:] != b[:-2]).mean())
    C1 = float(np.mean(b[:, :N - 1] * b[:, 1:N]) - 0.25)
    C2 = float(np.mean(b[:, :N - 2] * b[:, 2:N]) - 0.25)
    distinct4 = len(Counter(motifs)) / T
    if m2 > 0.99 and s4 < 0.02:
        state = 'P2c' if C1 < -0.08 else 'P2'
    elif m2 < 0.90 and m4 > 0.90:
        state = 'P4'
    elif m2 < 0.90 and m4 < 0.90 and m8 > 0.90:
        state = 'P8'
    else:
        state = 'MISC'
    return dict(r=r, eps=eps, m2=m2, m4=m4, m8=m8, s4=s4,
                C1=C1, C2=C2, distinct4=distinct4, state=state)

if __name__ == '__main__':
    rs = [3.40, 3.50, 3.60, 3.70, 3.80, 3.85, 3.88, 3.90, 3.94, 3.99]
    es = [0.05, 0.10, 0.15, 0.20, 0.30, 0.40]
    rows = []
    for r in rs:
        for e in es:
            d = diagnostics(r, e)
            rows.append(d)
            print(f"r={d['r']:.2f} eps={d['eps']:.2f}  {d['state']:<5s} "
                  f"m2={d['m2']:.3f} m4={d['m4']:.3f} m8={d['m8']:.3f} "
                  f"s4={d['s4']:.3f} C1={d['C1']:+.3f} C2={d['C2']:+.3f} "
                  f"distinct={d['distinct4']:.2f}")
    with open('period_landscape.json', 'w') as f:
        json.dump(rows, f, indent=2)

    color = {'P2c': '#1f77b4', 'P2': '#ff7f0e', 'P4': '#d62728',
             'P8': '#9467bd', 'MISC': '#9aa0a6'}
    fig, axes = plt.subplots(1, 3, figsize=(18, 6.5),
                             gridspec_kw={'width_ratios': [2.2, 1, 1]})
    ax = axes[0]
    for d in rows:
        ax.add_patch(plt.Rectangle((d['eps'] - 0.02, d['r'] - 0.025), 0.04, 0.05,
                   facecolor=color[d['state']], edgecolor='k', lw=0.5))
        ax.text(d['eps'], d['r'], d['state'], ha='center', va='center',
                fontsize=7.5, color='white' if d['state'] != 'MISC' else 'black')
    ax.set_xlim(0.02, 0.43)
    ax.set_ylim(3.36, 4.03)
    ax.set_xlabel('coupling eps')
    ax.set_ylabel('logistic parameter r')
    ax.set_title('Period-discriminating state map (corrected metric)')
    ax.set_xticks(es)
    ax.set_yticks(rs)

    S4 = np.array([[d['s4'] for d in rows if d['r'] == r] for r in rs])
    im1 = axes[1].pcolor(es, rs, S4, shading='auto', cmap='viridis')
    axes[1].set_title('single-site P4 signature s4')
    axes[1].set_xlabel('eps')
    axes[1].set_ylabel('r')
    fig.colorbar(im1, ax=axes[1])

    C1m = np.array([[d['C1'] for d in rows if d['r'] == r] for r in rs])
    im2 = axes[2].pcolor(es, rs, C1m, shading='auto', cmap='RdBu_r',
                         vmin=-0.25, vmax=0.25)
    axes[2].axhline(0, color='k', lw=0.5)
    axes[2].set_title('spatial antiphase C(1)')
    axes[2].set_xlabel('eps')
    axes[2].set_ylabel('r')
    fig.colorbar(im2, ax=axes[2])

    fig.tight_layout()
    fig.savefig('period_landscape.png', dpi=140, bbox_inches='tight')
    print('saved period_landscape.png + period_landscape.json')
