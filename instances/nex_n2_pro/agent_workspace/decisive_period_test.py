#!/usr/bin/env python3
"""
Decisive diagnostic: is the settled 'P4 tongue' state actually period-4,
or is it an antiphase period-2 spatial flip that my even-consistency
contrast C4 also reports as 1.0?

I will (a) count distinct 4-site motifs and their frequencies,
(b) directly test m(t)==m(t+2) vs m(t)==m(t+4),
(c) test the per-SITE temporal period (does site 0 cycle through 2 or 4 values?),
(d) check whether the C4 metric can distinguish P2 from P4 at all.
"""
import numpy as np

def step(x, r, eps):
    fx = r * x * (1.0 - x)
    return (1.0 - eps) * fx + 0.5 * eps * (np.roll(fx, 1) + np.roll(fx, -1))

def analyze(r, eps, seed, tau=10000, T=2000, N=100):
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
    motifs = [b[t, :4].tobytes() for t in range(T)]

    from collections import Counter
    cnt = Counter(motifs)
    print(f"\n=== (r={r}, eps={eps}, seed={seed}) ===")
    print(f"distinct 4-site motifs: {len(cnt)}")
    for m, c in cnt.most_common(8):
        print(f"   {m.decode():>8s}  freq={c}/{T} = {c/T:.3f}")

    # (b) direct period tests on the 4-site motif
    m2 = sum(1 for t in range(T - 2) if motifs[t] == motifs[t + 2]) / (T - 2)
    m4 = sum(1 for t in range(T - 4) if motifs[t] == motifs[t + 4]) / (T - 4)
    m1 = sum(1 for t in range(T - 1) if motifs[t] == motifs[t + 1]) / (T - 1)
    print(f"  motif(t)==motif(t+1): {m1:.3f}   (t+2): {m2:.3f}   (t+4): {m4:.3f}")
    print(f"  -> motif temporal period = 2" if m2 > 0.99 else "  -> motif temporal period > 2")

    # (c) per-SITE temporal period: look at the first 8 sites
    for s in range(8):
        col = b[:, s]
        seq = col[:16]
        period2 = np.mean(col[1:-1] == col[:-2])   # x_t vs x_{t-2}
        period4 = np.mean(col[3:-1] == col[:-4])
        print(f"  site {s}: P2match={period2:.3f} P4match={period4:.3f}  head16={''.join(map(str, seq))}")

    # (d) does C4 distinguish? construct a pure-P4 synthetic and a pure-P2
    #     and compute the same even/odd contrast on each.
    def c4contrast(motifs, T, max_lag=50):
        lags = {}
        for lag in range(1, max_lag + 1):
            matches = sum(1 for i in range(T - lag) if motifs[i] == motifs[i + lag])
            lags[lag] = matches / (T - lag)
        res = {k: float(np.mean([lags[l] for l in lags if l % 4 == k])) for k in range(4)}
        even = (res[0] + res[2]) / 2
        odd = (res[1] + res[3]) / 2
        return even - odd, res

    # pure period-2 motif sequence (ABAB...)
    p2 = ['A', 'B'] * (T // 2)
    c4_2, res2 = c4contrast(p2, 2 * len(p2))
    # pure period-4 motif sequence (ABCDABCD...)
    p4 = ['A', 'B', 'C', 'D'] * (T // 4)
    c4_4, res4 = c4contrast(p4, 4 * len(p4))
    print(f"\n  C4-contrast on pure P2 synthetic: {c4_2:+.3f}  res={ {k:round(v,3) for k,v in res2.items()} }")
    print(f"  C4-contrast on pure P4 synthetic: {c4_4:+.3f}  res={ {k:round(v,3) for k,v in res4.items()} }")
    return c4_2, c4_4

analyze(3.88, 0.145, 42)     # tongue core
analyze(3.865, 0.132, 42)    # world-B point
