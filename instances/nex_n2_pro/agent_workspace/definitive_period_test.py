#!/usr/bin/env python3
"""DEFINITIVE period-2 vs period-4 test: print raw values, no clever stats.
A period-2 cell:  a b a b a b ...  (2 distinct values alternating)
A period-4 cell:  a b c d a b c d ... (4 distinct values cycling)
"""
import numpy as np

def coupled(x, r, eps):
    return (1-eps)*r*x*(1-x) + (eps/2)*(np.roll(r*x*(1-x),1)+np.roll(r*x*(1-x),-1))

def run(r, eps, n=100, steps=32, trans=3000, seed=1):
    np.random.seed(seed); x = np.random.rand(n)
    for _ in range(trans): x = coupled(x, r, eps)
    ts = []
    for _ in range(steps):
        x = coupled(x, r, eps); ts.append(x.copy())
    return np.array(ts)  # (steps, n)

def acf(sig, n=12):
    c = sig - sig.mean()
    a = np.correlate(c, c, 'full')[len(c)-1: len(c)-1+n+1]
    return a / (a[0]+1e-30)

def top_freq(sig):
    F = np.fft.rfft(sig - sig.mean())
    P = np.abs(F)**2
    k = int(np.argmax(P[1:])+1)
    freq = k / len(sig)
    return freq, 1.0/freq if freq>0 else float('inf')

cases = [(3.865,0.132,"THE 'period-4' case"), (3.5,0.132,"map natively period-4"), (4.0,0.15,"strong coupling")]
for r, eps, lab in cases:
    ts = run(r, eps)
    c0 = ts[:,0]; c50 = ts[:,50]
    print(f"\n===== r={r} eps={eps}  [{lab}] =====")
    print("cell0  :", np.array2string(c0[:16], precision=3, separator=', '))
    print("cell50 :", np.array2string(c50[:16], precision=3, separator=', '))
    print("cell0 ACF[1..6]:", np.array2string(acf(c0,6)[1:7], precision=3, separator=', '))
    f0,p0 = top_freq(c0); f50,p50 = top_freq(c50)
    print(f"cell0 dominant freq={f0:.3f} (period {p0:.1f})   cell50 dominant freq={f50:.3f} (period {p50:.1f})")
    # how many distinct values in the cycle?
    vals = c0[:8]
    print("first 8 of cell0, rounded to 2dp:", np.array2string(np.round(vals,2), separator=', '))
