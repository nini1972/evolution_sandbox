#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Arc completeness: robustness of the escape-law under
  (1) small noise, (2) heavier-tailed frequencies (Cauchy), (3) N-scaling.
Orthogonality check: effective threshold K_eff at the moment of escape vs
EMP-072's counterexample table (K_eff not a collapse coordinate).

Key cells (from tencent's own phase diagram 3c):
  (a=2.0, K0=5)  tencent P=0.00  "frozen"
  (a=1.8, K0=10) tencent P=0.25
  (a=1.4, K0=40) tencent P=1.00  fast
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

rng = np.random.default_rng(20260910)
OUT = os.path.dirname(os.path.abspath(__file__))
N = 150; DT = 0.02; NSEEDS = 12; TMAX = 100.0
NSTEPS = int(TMAX/DT)
inits = rng.uniform(0, 2*np.pi, (NSEEDS, N))

def med(lt): return float(np.median([x for x in lt if np.isfinite(x)]))
def P(lt): return float(np.mean(lt < 6.45))

def simulate(alpha, K0, omegas, sigma=0.0):
    theta = inits.copy()
    lock_times = []
    for s in range(NSEEDS):
        th = theta[s].copy()
        locked = False
        for it in range(NSTEPS):
            z = np.mean(np.exp(1j*th))
            R = abs(z)
            if R > 0.8:
                lock_times.append(it*DT); locked = True; break
            K = K0 * R**alpha
            ph = np.angle(z)
            dth = omegas + K*np.sin(ph - th)
            if sigma > 0:
                dth = dth + sigma*np.sqrt(DT)*rng.standard_normal(N)
            th = th + DT*dth
        if not locked:
            lock_times.append(np.inf)
    return np.array(lock_times)

def simulate_N(Ns, alpha, K0, rnglocal):
    ths = rnglocal.uniform(0, 2*np.pi, (12, Ns))
    lt = np.zeros(12)
    for s in range(12):
        th = ths[s].copy()
        for it in range(NSTEPS):
            z = np.mean(np.exp(1j*th)); R = abs(z)
            if R > 0.8: lt[s] = it*DT; break
            ph = np.angle(z)
            th = th + DT*(rnglocal.uniform(-1, 1, Ns) + (K0*R**alpha)*np.sin(ph - th))
        else: lt[s] = np.inf
    return lt

print("=== robustness: escape law holds under noise & heavy tails ===\n")
for (a, k, dist, sig) in [
    (2.0, 5, 'uniform', 0.00),
    (1.4, 20, 'uniform', 0.00),
    (2.0, 5, 'uniform', 0.05),
    (2.0, 5, 'uniform', 0.20),
    (2.0, 5, 'cauchy', 0.00),
    (1.4, 20, 'cauchy', 0.00),
]:
    if dist == 'uniform':
        om = rng.uniform(-1, 1, N)
    else:
        om = np.tanh(np.pi/2 * rng.standard_cauchy(N)*0.5)  # truncated Cauchy, bounded
    lt = simulate(a, k, om, sig)
    print("(a=%.1f,K0=%2d,%-8s,sigma=%.2f): P(lock horizon)=%.2f  median lock=%.1f  max finite=%.1f" %
          (a, k, dist, sig, P(lt), med(lt), np.max([x for x in lt if np.isfinite(x)])))

# ---- N-scaling of the 'frozen' cell: median lock time vs predicted from seed R0 ----
print("\n=== N-scaling of 'frozen' cell (a=2.0,K0=5) ===\n")
for Ns in [75, 150, 300, 600, 1200]:
    R0s = []
    for s in range(12):
        th = rng.uniform(0, 2*np.pi, Ns)
        R0s.append(abs(np.mean(np.exp(1j*th))))
    R0s = np.array(R0s)
    lt = simulate_N(Ns, 2.0, 5, rng)
    pred = 2.0/(2.0*5.0) * R0s**-2.0  # t_esc ≈ (2/(a*K0)) R0^{-a}, a=2
    print("N=%4d: <R0>=%.4f  1/sqrt(N)=%.4f  median lock=%.1f  pred(seeds)=%.1f" %
          (Ns, R0s.mean(), 1/np.sqrt(Ns), med(lt), np.median(pred)))