import numpy as np

def step(x, r, eps):
    fx = r * x * (1.0 - x)
    return (1.0 - eps) * fx + 0.5 * eps * (np.roll(fx, 1) + np.roll(fx, -1))

def distances(x, r, eps, kmax=8):
    d = np.zeros(kmax)
    y = x.copy()
    for k in range(1, kmax + 1):
        y = step(y, r, eps)
        d[k - 1] = float(np.max(np.abs(y - x)))
    return d

def float_period(d, tol=1e-5):
    for k in range(1, len(d) + 1):
        if d[k - 1] < tol:
            return k
    return None

def shadow_period(x, r, eps, T=400, agree=0.985):
    xt = x.copy()
    traj = [xt.copy()]
    for _ in range(T):
        xt = step(xt, r, eps)
        traj.append(xt.copy())
    traj = np.array(traj)
    gmed = np.median(traj)
    seq = (traj > gmed).astype(np.int8)
    for k in range(1, 9):
        frac = float(np.mean(seq[:-k] == seq[k:]))
        if frac > agree:
            return k
    return None

N, seed = 100, 42
np.random.seed(seed)
x0 = np.random.rand(N)

rs = np.round(np.arange(3.84, 3.901, 0.01), 3)
es = np.round(np.arange(0.10, 0.181, 0.01), 3)
rows = []
print('r      eps   fP sP   d2      d4     breathing')
for r in rs:
    for eps in es:
        x = x0.copy()
        for _ in range(1000):
            x = step(x, r, eps)
        d = distances(x, r, eps)
        fp = float_period(d)
        sp = shadow_period(x, r, eps)
        breathing = float(d[1]) if fp == 4 else 0.0
        rows.append([float(r), float(eps), fp if fp else -1, sp if sp else -1,
                     d[1], d[3], breathing])
        print(f"{r:5.3f} {eps:5.3f} {str(fp):>3} {str(sp):>3} {d[1]:7.4f} {d[3]:7.4f} {breathing:7.4f}")

fp4_sp2 = [(a, b) for (a, b, fp, sp, *_r) in rows if fp == 4 and sp == 2]
fp4_sp4 = [(a, b) for (a, b, fp, sp, *_r) in rows if fp == 4 and sp == 4]
fp4_spn = [(a, b) for (a, b, fp, sp, *_r) in rows if fp == 4 and sp not in (2, 4)]
fp2 = [(a, b) for (a, b, fp, sp, *_r) in rows if fp == 2]
print('')
print('float-P4 & shadow-P2 (breathers):', len(fp4_sp2))
print('float-P4 & shadow-P4:', len(fp4_sp4))
print('float-P4 & other shadow:', len(fp4_spn), fp4_spn[:8])
print('float-P2 points:', len(fp2))
np.save('shadow_v4.npy', np.array(rows, dtype=float))
