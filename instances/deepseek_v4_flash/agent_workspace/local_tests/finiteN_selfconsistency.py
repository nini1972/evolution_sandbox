"""Finite-N self-consistency: F_N(K) = (1/N) sum_{|w|<K} sqrt(1-(w/K)^2).
Exact stationary response of a FINITE sample (partial locking branch).
If F_N(3) ~ 0.71 (measured for a=0 at N=2000), the anomaly is a finite-N
threshold shift, and the a=1 plateau solves R = F_N(3R).
"""
import numpy as np

def cauchy_sample(n, gamma=1.0, seed=7):
    r = np.random.default_rng(seed)
    return gamma * np.tan(np.pi * (r.random(n) - 0.5))

def F_N(om, K):
    w = np.abs(om)
    locked = w < K
    if locked.sum() == 0:
        return 0.0
    return float(np.sqrt(1 - (w[locked]/K)**2).mean())  # normalized by N via mean of subset? NO - must be /N

def F_N_proper(om, K):
    """(1/N) sum over locked of sqrt(1-(w/K)^2)"""
    w = np.abs(om)
    locked = w < K
    if locked.sum() == 0:
        return 0.0
    return float(np.sqrt(1 - (w[locked]/K)**2).sum() / om.size)

for N in [2000, 100000]:
    om = cauchy_sample(N, 1.0, seed=40)  # seed*13+1 style
    print(f'--- N={N} ---')
    for K in [1.5, 2.0, 2.5, 3.0, 3.6, 6.0, 10.0]:
        print(f'  K={K:5.1f}: F_N={F_N_proper(om,K):.4f}  (OA: {np.sqrt(max(0,1-2/K)):.4f})',
              flush=True)

# a=1 self-consistency fixed points: R = F_N(3R) for K0=3
print()
print('=== a=1, K0=3: R vs F_N(3R) fixed point search (N=2000,100k) ===')
for N in [2000, 100000]:
    om = cauchy_sample(N, 1.0, seed=40)
    rs = np.linspace(0.01, 0.9, 90)
    diffs = []
    for r in rs:
        d = r - F_N_proper(om, 3.0*r)
        diffs.append((r, d))
    # find sign changes
    print(f'N={N}:')
    for i in range(len(rs)-1):
        if diffs[i][1] * diffs[i+1][1] < 0:
            print(f'  fixed point near R={rs[i]:.4f} (diff {diffs[i][1]:+.4f} -> {diffs[i+1][1]:+.4f})')
    # also evaluate at R=0.57
    print(f'  R=0.570: F_N(1.71)={F_N_proper(om,3.0*0.570):.4f}, diff={0.570-F_N_proper(om,1.71):+.4f}', flush=True)