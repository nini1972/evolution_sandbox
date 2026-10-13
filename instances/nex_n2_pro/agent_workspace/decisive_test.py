#!/usr/bin/env python3
"""DECISIVE PERIOD TEST — settles period-2 vs period-4 at MACHINE PRECISION.

Why: the ACF discriminator (period_census.py) flags ACF[4]>ACF[2], but that
cannot distinguish (a) a true 4-cycle from (b) a banded chaotic attractor
with strong lag-4 correlations (e.g. just past the Feigenbaum point).
And a dominant f=0.5 FFT peak cannot distinguish a true 4-cycle from a
2-cycle, because every 4-cycle has a strong 2nd harmonic at f=0.5.

The only airtight test: iterate to machine-precision convergence on the
attractor (stable orbit => after ~500 steps the state sits on the cycle
within ~1e-15; we use 20000), then measure the exact repetition residual
    s_k = max_t |x[t+k] - x[t]|
for k in {1,2,3,4,6,8,12,16}. A strict p-cycle gives s_p ~ 1e-15 while
s_{p/2} ~ O(0.001..0.3). Chaos gives s_k ~ O(0.1) for all k.

  exact period p  <=>  s_p < 1e-9  and  no smaller k in set has s_k < 1e-9
  aperiodic       <=>  no k in set has s_k < 1e-9
"""
import numpy as np
from collections import Counter

def coupled(x, r, eps):
    f = r*x*(1.0 - x)
    return (1.0 - eps)*f + (eps/2.0)*(np.roll(f,1) + np.roll(f,-1))

KS = [1, 2, 3, 4, 6, 8, 12, 16]

def s_profile(ts):
    return {k: float(np.max(np.abs(ts[k:] - ts[:-k]))) for k in KS}

def exact_period(sp):
    for k in KS:
        if sp[k] < 1e-9:
            return k
    return None  # aperiodic (or period > 16)

def main():
    cases = [
        (3.865, 0.132, "claimed 'period-4' @ edge of chaos"),
        (3.865, 0.100, "claimed 'period-4', weaker coupling"),
        (3.50,  0.132, "native period-4 window"),
        (3.565, 0.0,   "native period-8 window (control: should be 8)"),
        (3.57,  0.0,   "just past Feigenbaum pt (banded chaos control)"),
        (3.40,  0.0,   "native period-2 (control)"),
        (3.865, 0.0,   "uncoupled chaos (control)"),
        (4.00,  0.132, "r=4 fully chaotic, with coupling"),
    ]
    n, trans, rec = 120, 20000, 2000
    np.random.seed(0)
    for r, eps, tag in cases:
        x = np.random.rand(n)
        for _ in range(trans):
            x = coupled(x, r, eps)
        S = np.empty((rec, n))
        for t in range(rec):
            x = coupled(x, r, eps); S[t] = x
        cnt = Counter(); rep = {}
        for i in range(n):
            sp = s_profile(S[:, i])
            p = exact_period(sp)
            cnt[p] += 1
            if p not in rep:
                rep[p] = (i, sp)
        print(f"r={r:<6} eps={eps:<6} [{tag}]")
        for p in [1, 2, 3, 4, 6, 8, 12, 16, None]:
            if cnt[p]:
                print(f"    exact period {str(p):>4} : {cnt[p]:3d}/{n} cells")
        for p, (i, sp) in rep.items():
            v = S[:8, i]
            print(f"    rep cell{i} [p={p}]: " + " ".join(f"{a:.10f}" for a in v))
            print(f"        s_profile: " + "  ".join(f"s{k}={sp[k]:.2e}" for k in KS))
            if p == 4:
                print(f"        A-C = {v[0]-v[2]:+.3e}   B-D = {v[1]-v[3]:+.3e}   "
                      f"(period-4 split amplitude, machine-precision)")
        print()

if __name__ == "__main__":
    main()
