import numpy as np

N = 32
def step(x, r, eps):
    fx = r * x * (1.0 - x)
    return (1.0 - eps) * fx + 0.5 * eps * (np.roll(fx, 1) + np.roll(fx, -1))

def distances(x, r, eps, kmax=8):
    d = np.zeros(kmax); y = x.copy()
    for k in range(1, kmax + 1):
        y = step(y, r, eps); d[k-1] = float(np.max(np.abs(y - x)))
    return d

def float_period(d, tol=1e-5):
    for k in range(1, len(d) + 1):
        if d[k-1] < tol: return k
    return None

def shadow_period(x, r, eps, T=200, agree=0.985):
    xt = x.copy(); traj = [xt.copy()]
    for _ in range(T):
        xt = step(xt, r, eps); traj.append(xt.copy())
    traj = np.array(traj)
    seq = (traj > np.median(traj)).astype(np.int8)
    for k in range(1, 9):
        if float(np.mean(seq[:-k] == seq[k:])) > agree:
            return k
    return None

def antiphase_gap(x):
    return float(np.abs(np.mean(x[0::2]) - np.mean(x[1::2])))

rs = np.round(np.arange(3.50, 4.001, 0.01), 2)
es = np.round(np.arange(0.05, 0.301, 0.01), 2)
np.random.seed(42)
rows = []
for r in rs:
    for eps in es:
        x = np.random.rand(N)
        for _ in range(300): x = step(x, r, eps)
        d = distances(x, r, eps)
        fp = float_period(d)
        sp = shadow_period(x, r, eps)
        gap = antiphase_gap(x)
        br = float(d[1]) if fp == 4 else 0.0
        rows.append([float(r), float(eps), fp or -1, sp or -1, gap, br, d[1], d[3]])
import json
np.save('phasediag.npy', np.array(rows))
print('grid', len(rs), 'x', len(es), '=', len(rs)*len(es), 'points')
np.unique(np.array(rows)[:,2], return_counts=True)
print('float period counts:', dict(zip(*np.unique(np.array(rows)[:,2], return_counts=True))))
print('shadow period counts:', dict(zip(*np.unique(np.array(rows)[:,3], return_counts=True))))
