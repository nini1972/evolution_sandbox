#!/usr/bin/env python3
"""
Clean per-cell temporal-period diagnostic for the CML.
Distinguishes:
  - period-2  : |ACF[2] - ACF[4]| small, ACF[1] strongly negative
  - period-4  : ACF[2] and ACF[4] differ materially (ACF[2] < ACF[4])
  - aperiodic : ACF[1] ~ 0, no peaks
Histograms cell periods across the whole lattice.
"""
import numpy as np, json

def coupled(x, r, eps):
    return (1-eps)*r*x*(1-x) + (eps/2)*(np.roll(r*x*(1-x),1)+np.roll(r*x*(1-x),-1))

def cell_acf_period(sig, maxlag=32):
    c = sig - sig.mean()
    acf = np.correlate(c, c, 'full')[len(c)-1: len(c)-1+maxlag+1]
    acf = acf / (acf[0]+1e-30)
    # first positive peak after lag 1
    p = None
    for t in range(2, maxlag):
        if acf[t] > acf[t-1] and acf[t] >= acf[t+1] and acf[t] > 0.15:
            p = t; break
    return acf, p

def diagnose(r, eps, n=100, steps=4096, trans=2000, seed=1):
    np.random.seed(seed); x = np.random.rand(n)
    for _ in range(trans): x = coupled(x, r, eps)
    traj = np.empty((steps, n))
    for t in range(steps):
        x = coupled(x, r, eps); traj[t] = x
    periods = {}
    acf2, acf4, acf1 = [], [], []
    for i in range(n):
        a, p = cell_acf_period(traj[:, i])
        acf1.append(a[1]); acf2.append(a[2]); acf4.append(a[4])
        periods[p] = periods.get(p, 0) + 1
    a1, a2, a4 = float(np.median(acf1)), float(np.median(acf2)), float(np.median(acf4))
    # classifier on median ACF
    if a1 > -0.15 and max(a2, a4) < 0.3:
        cls = "aperiodic (chaos)"
    elif abs(a2 - a4) < 0.12 and a1 < -0.5:
        cls = "period-2 antiphase wave"
    elif a4 > a2 + 0.08:
        cls = "period-4 (genuine)"
    else:
        cls = "mixed/other"
    return {'r': r, 'eps': eps, 'median_acf1': a1, 'median_acf2': a2,
            'median_acf4': a4, 'cell_period_hist': periods, 'class': cls}

if __name__ == "__main__":
    cases = [
        (3.865, 0.132, "ORIGINAL 'period-4' case"),
        (4.0,   0.15,  "strong coupling"),
        (4.0,   0.001, "independent chaos (control)"),
        (3.865, 0.001, "weak coupling"),
        (3.5,   0.132, "map is natively period-4"),
        (3.57,  0.132, "map near chaos onset"),
    ]
    res = []
    for r, eps, lab in cases:
        d = diagnose(r, eps)
        res.append(d)
        print(f"\nr={r} eps={eps}  [{lab}]")
        print(f"  median ACF[1]={d['median_acf1']:+.3f}  ACF[2]={d['median_acf2']:+.3f}  ACF[4]={d['median_acf4']:+.3f}")
        print(f"  cell-period histogram: {dict(sorted(d['cell_period_hist'].items(), key=lambda x: str(x[0])))}")
        print(f"  --> CLASS: {d['class']}")
    json.dump(res, open('period_diagnosis.json', 'w'), indent=2)
