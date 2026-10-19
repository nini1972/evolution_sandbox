#!/usr/bin/env python3
"""
Fine sweep around the contested point (r=3.865, eps=0.132) where World B
(EMP-135 / CRT-011) reports a genuine period-4 symbolic orbit, while my
coarse grid found period-2 checkerboard at nearby points.

Discriminating observables (convention-invariant):
  m2, m4 : motif (4-bit) lag-2 / lag-4 consistency at fixed window
  s4     : P(bit(t+2,x) != bit(t,x)) over all sites (0 => P2, ~0.5 => P4)
  d4f    : max_x |x(t+4,x) - x(t,x)|   (float level; ~0 => T=4 orbit)
  d2f    : max_x |x(t+2,x) - x(t,x)|   (float level; ~0 => T=2 orbit)
  diag   : mean_x |x(t+2,x) - x(t,x+1)| / max(mean|x(t+2,x)-x(t,x)|,eps)
           (1.0 => diagonal translation symmetry b(t+2,x)=b(t,x+1):
            the 'diagonal period-4' of CRT-011)
  C1     : spatial corr d=1
"""
import numpy as np
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def step(x, r, eps):
    fx = r * x * (1.0 - x)
    return (1.0 - eps) * fx + 0.5 * eps * (np.roll(fx, 1) + np.roll(fx, -1))

def analyze(r, eps, seed=42, tau=6000, T=1500, N=100, t_probe=1000):
    np.random.seed(seed)
    x = np.random.rand(N)
    for _ in range(tau):
        x = step(x, r, eps)
    # sample a few probe times for float diagnostics
    probes = {}
    traj = []
    for t in range(T):
        x = step(x, r, eps)
        if t in (t_probe, t_probe + 2, t_probe + 4):
            probes[t] = x.copy()
        traj.append(x.copy())
    traj = np.array(traj)
    b = (traj > np.median(traj, axis=(0, 1), keepdims=True)).astype(float)
    motifs = [b[t, :4].tobytes() for t in range(T)]
    m2 = sum(1 for t in range(T - 2) if motifs[t] == motifs[t + 2]) / (T - 2)
    m4 = sum(1 for t in range(T - 4) if motifs[t] == motifs[t + 4]) / (T - 4)
    s4 = float((b[2:] != b[:-2]).mean())
    x4, x2, x0 = probes[t_probe + 4], probes[t_probe + 2], probes[t_probe]
    d4f = float(np.max(np.abs(x4 - x0)))
    d2f = float(np.max(np.abs(x2 - x0)))
    diag_num = float(np.mean(np.abs(x2 - np.roll(x0, -1))))
    same_num = float(np.mean(np.abs(x2 - x0)))
    diag = diag_num / max(same_num, 1e-12)
    C1 = float(np.mean(b[:, :N - 1] * b[:, 1:N]) - 0.25)
    if m2 > 0.99 and s4 < 0.02:
        state = 'P2c' if C1 < -0.08 else 'P2'
    elif m2 < 0.90 and m4 > 0.90 and s4 > 0.3:
        state = 'P4diag'
    elif m2 < 0.90 and m4 > 0.90:
        state = 'P4?'
    else:
        state = 'MIX'
    return dict(r=r, eps=eps, m2=m2, m4=m4, s4=s4, d2f=d2f, d4f=d4f,
                diag=diag, C1=C1, state=state)

if __name__ == '__main__':
    rs = [3.845, 3.855, 3.865, 3.875]
    es = [0.100, 0.115, 0.125, 0.132, 0.140, 0.150]
    rows = []
    for r in rs:
        for e in es:
            d = analyze(r, e)
            rows.append(d)
            print(f"r={d['r']:.3f} eps={d['eps']:.3f}  {d['state']:<8s} "
                  f"m2={d['m2']:.3f} m4={d['m4']:.3f} s4={d['s4']:.3f} "
                  f"d2f={d['d2f']:.3f} d4f={d['d4f']:.3f} "
                  f"diag={d['diag']:.3f} C1={d['C1']:+.3f}")
    with open('fine_sweep.json', 'w') as f:
        json.dump(rows, f, indent=2)

    color = {'P2c': '#1f77b4', 'P2': '#ff7f0e', 'P4diag': '#d62728',
             'P4?': '#ff9896', 'MIX': '#9aa0a6'}
    fig, axes = plt.subplots(1, 3, figsize=(18, 6),
                             gridspec_kw={'width_ratios': [2.2, 1, 1]})
    ax = axes[0]
    for d in rows:
        ax.add_patch(plt.Rectangle((d['eps'] - 0.004, d['r'] - 0.005), 0.008,
                   0.01, facecolor=color[d['state']], edgecolor='k', lw=0.5))
        ax.text(d['eps'], d['r'], d['state'], ha='center', va='center',
                fontsize=7, color='white' if d['state'] != 'MIX' else 'black')
    ax.plot(0.132, 3.865, 'k*', ms=14, mfc='yellow', mec='k',
            label='EMP-135 point')
    ax.set_xlim(0.095, 0.155)
    ax.set_ylim(3.838, 3.882)
    ax.set_xlabel('coupling eps'); ax.set_ylabel('r')
    ax.set_title('Fine sweep: true period-4 tongue vs P2 checkerboard')
    ax.set_xticks(es); ax.set_yticks(rs)
    ax.legend()

    M2 = np.array([[d['m2'] for d in rows if d['r'] == r] for r in rs])
    im1 = axes[1].pcolor(es, rs, M2, shading='auto', cmap='viridis',
                         vmin=0.5, vmax=1.0)
    axes[1].set_title('motif lag-2 match m2')
    axes[1].set_xlabel('eps'); axes[1].set_ylabel('r')
    fig.colorbar(im1, ax=axes[1])

    S4 = np.array([[d['s4'] for d in rows if d['r'] == r] for r in rs])
    im2 = axes[2].pcolor(es, rs, S4, shading='auto', cmap='plasma',
                         vmin=0, vmax=0.6)
    axes[2].set_title('single-site P4 signature s4')
    axes[2].set_xlabel('eps'); axes[2].set_ylabel('r')
    fig.colorbar(im2, ax=axes[2])

    fig.tight_layout()
    fig.savefig('fine_sweep.png', dpi=140, bbox_inches='tight')
    print('saved fine_sweep.png + fine_sweep.json')
