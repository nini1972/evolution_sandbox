#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reconcile my replication with tencent's published P(lock) table.
Record FULL lock-time distributions for all 24 cells (or inf).
Then search: which observation horizon T* maps my lock times onto tencent's table?
Also scan natural-frequency spread kappa (uniform[-kappa,kappa]).
If a single (T*, kappa) reproduces the table, the discrepancy is protocol choice,
not physics — and my 'horizon, not barrier' claim holds.
"""
import os, json
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(20260910)
N = 150; DT = 0.02; NSEEDS = 12; TMAX = 100.0
NSTEPS = int(TMAX/DT)
inits = rng.uniform(0, 2*np.pi, (NSEEDS, N))

alphas = [1.0, 1.2, 1.4, 1.6, 1.8, 2.0]
K0s    = [5, 10, 20, 40]
TENCENT = np.array([
    [0.92, 1.00, 1.00, 1.00],
    [0.33, 1.00, 1.00, 1.00],
    [0.08, 0.92, 1.00, 1.00],
    [0.00, 0.42, 1.00, 1.00],
    [0.00, 0.25, 0.92, 1.00],
    [0.00, 0.08, 0.50, 0.92],
])

def lock_times(alpha, K0, kappa, seed_offset=0):
    lt = []
    for s in range(NSEEDS):
        om = rng.uniform(-kappa, kappa, N)
        th = inits[s].copy()
        done = False
        for it in range(NSTEPS):
            z = np.mean(np.exp(1j*th)); R = abs(z)
            if R > 0.8:
                lt.append(it*DT); done = True; break
            K = K0 * R**alpha
            th = th + DT*(om + K*np.sin(np.angle(z) - th))
        if not done: lt.append(np.inf)
    return np.array(lt)

def Pm(lt, T):
    return float(np.mean(lt < T))

results = {}
for kappa in [0.5, 1.0, 2.0]:
    LTs = {}   # (i,j) -> locktime array
    for i,a in enumerate(alphas):
        for j,k in enumerate(K0s):
            LTs[(i,j)] = lock_times(a, k, kappa)
            if j == 0:
                fin = LTs[(i,j)][np.isfinite(LTs[(i,j)])]
                print("k=%.1f a=%.1f K0=%2d: P(6.45)=%.2f med=%.1f maxfin=%.1f nlock12=%.0f" %
                      (kappa, a, k, Pm(LTs[(i,j)],6.45),
                       np.median(fin) if len(fin) else np.inf,
                       np.max(fin) if len(fin) else np.inf,
                       np.sum(np.isfinite(LTs[(i,j)]))))
    # best horizon T* for this kappa
    best = None
    for T in np.linspace(0.1, 50.0, 500):
        Ppred = np.array([[Pm(LTs[(i,j)], T) for j in range(4)] for i in range(6)])
        err = np.mean((Ppred - TENCENT)**2)
        if best is None or err < best[0]:
            best = (err, T, Ppred)
    err, Tstar, Ppred = best
    results[kappa] = {'Tstar': Tstar, 'MSE': err, 'Ppred': Ppred.tolist()}
    print("kappa=%.1f: BEST T* = %.2f  MSE(vs tencent) = %.4f" % (kappa, Tstar, err))
    print(np.round(Ppred,2)); print()

# also: my decisive cell over 100s with kappa=1
lt = lock_times(2.0, 5.0, 1.0)
fin = lt[np.isfinite(lt)]
print("DECISIVE (a=2,K0=5,kappa=1): P(lock by 6.45)=%.2f  P(by 100)=%.2f  med=%.1f  max=%.1f  all=%s" %
      (Pm(lt,6.45), Pm(lt,100.0), np.median(fin), np.max(fin), np.sum(np.isfinite(lt))))

json.dump({'best_by_kappa': {str(k): results[k] for k in results},
           'decisive': {'P6': Pm(lt,6.45), 'P100': Pm(lt,100.0)}},
          open(os.path.join(OUT,'reconcile.json'),'w'), indent=1)
print("saved reconcile.json")