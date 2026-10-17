#!/usr/bin/env python3
"""
Settling-time hypothesis test for the P4 symbolic parity contrast C4.

Hypothesis (H1): The symbolic period-4 parity contrast C4 is NOT a settled
invariant at (r, eps) where the lattice is mostly chaotic; it is a function
of the transient length tau, dominated by pre-settling transient smoothing.
This would explain the discrepancy between the original Frontier measurement
(C4 = 0.828, seed 42, tau=1000, T=2000, N=100) and World B's replica
(C4 = 0.257, N=100, T=2000, EMP-135).

Control point: deep in the P4 tongue where nearly all seeds settle onto the
stable P4 orbit; there C4 should approach ~1 at long tau and be seed-robust.

Protocol (exactly replicating periodicity_archaeology.py):
  N = 100, f(x) = r x (1-x), coupling (1-eps) f(x) + eps/2 (f(x_{i-1})+f(x_{i+1}))
  x0 = np.random.seed(seed); np.random.rand(N)
  evolve tau steps (transient), record T = 2000 steps
  binary = x > median(x)  (global median over recorded window)
  motif(t) = first 4 bits
  lag consistency for lag = 1..50; residue means mod 4; C4 = even_mean - odd_mean
"""
import numpy as np
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def step(x, r, eps):
    fx = r * x * (1.0 - x)
    return (1.0 - eps) * fx + 0.5 * eps * (np.roll(fx, 1) + np.roll(fx, -1))


def c4_at_transient(r, eps, seed, tau, T=2000, N=100, max_lag=50):
    np.random.seed(seed)
    x = np.random.rand(N)
    for _ in range(tau):
        x = step(x, r, eps)
    traj = []
    for _ in range(T):
        x = step(x, r, eps)
        traj.append(x.copy())
    traj = np.array(traj)
    b = (traj > np.median(traj)).astype(int)
    motifs = [''.join(str(bit) for bit in row) for row in b[:, :4]]
    lags = {}
    m = len(motifs)
    for lag in range(1, max_lag + 1):
        matches = sum(1 for i in range(m - lag) if motifs[i] == motifs[i + lag])
        lags[lag] = matches / (m - lag)
    res = {}
    for residue in range(4):
        vals = [lags[l] for l in lags if l % 4 == residue]
        res[residue] = float(np.mean(vals))
    even = (res[0] + res[2]) / 2
    odd = (res[1] + res[3]) / 2
    return even - odd, res, even, odd


def period4_share(r, eps, seed, tau, T=2000, N=100):
    """Fraction of recorded time-lag pairs (i, i+4) matching and (i, i+1) not:
    a settle-marker for a clean period-4 motif sequence."""
    np.random.seed(seed)
    x = np.random.rand(N)
    for _ in range(tau):
        x = step(x, r, eps)
    traj = []
    for _ in range(T):
        x = step(x, r, eps)
        traj.append(x.copy())
    b = (np.array(traj) > np.median(traj)).astype(int)
    m = 0
    M = 0
    match4 = 0
    match1 = 0
    for i in range(T - 4):
        M += 1
        if b[i, :4].tobytes() == b[i + 4, :4].tobytes():
            match4 += 1
        if b[i, :4].tobytes() == b[i + 1, :4].tobytes():
            match1 += 1
    return match4 / M, match1 / M


if __name__ == '__main__':
    taus = [1000, 5000, 20000, 100000, 400000]
    seeds = [42, 1, 2, 3]
    points = {
        'A: World-B point (3.865, 0.132)': (3.865, 0.132),
        'B: tongue core (3.88, 0.145)': (3.88, 0.145),
    }
    results = {}
    for name, (r, eps) in points.items():
        results[name] = {}
        print(f'== {name} ==')
        for seed in seeds:
            row = {}
            for tau in taus:
                c4, res, even, odd = c4_at_transient(r, eps, seed, tau)
                m4, m1 = period4_share(r, eps, seed, tau)
                row[tau] = {'C4': c4, 'res0': res[0], 'res2': res[2],
                            'res_odd': (res[1] + res[3]) / 2,
                            'match4': m4, 'match1': m1}
                print(f'  seed={seed:>2} tau={tau:>7}  C4={c4:+.4f}  '
                      f'res0={res[0]:.3f} res2={res[2]:.3f} odd={((res[1]+res[3])/2):.3f}  '
                      f'P4share4={m4:.3f} P1share1={m1:.3f}')
            results[name][seed] = row
    with open('p4_c4_settling_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    # --- Plot ---
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    colors = {42: 'red', 1: 'steelblue', 2: 'green', 3: 'orange'}
    for ax, (name, (r, eps)) in zip(axes.flat, points.items()):
        for seed in seeds:
            row = results[name][seed]
            cs = [row[t]['C4'] for t in taus]
            ax.plot(taus, cs, 'o-', color=colors[seed], label=f'seed {seed}', lw=1.5)
            ax.axhline(0.0625, color='gray', ls=':', lw=1)
        ax.set_xscale('log')
        ax.set_xlabel('transient tau (steps)')
        ax.set_ylabel('C4 = even - odd motif consistency')
        ax.set_title(f'{name}\n(5-bit motif from 4-cell window, T=2000, N=100)')
        ax.grid(alpha=0.3)
        ax.legend()
    fig.suptitle('C4 settling-time dependence: transient artifact vs settled invariant',
                 fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig('p4_c4_settling.png', dpi=140, bbox_inches='tight')
    print('saved p4_c4_settling.png')
