import numpy as np

def step(x, r, eps):
    fx = r * x * (1.0 - x)
    return (1.0 - eps) * fx + 0.5 * eps * (np.roll(fx, 1) + np.roll(fx, -1))

def float_period(x, r, eps, tol=1e-8, kmax=8):
    x0 = x
    for k in range(1, kmax + 1):
        y = x0.copy()
        for _ in range(k):
            y = step(y, r, eps)
        if float(np.max(np.abs(y - x0))) < tol:
            return k
    return None

def shadow_period(x, r, eps, T=400):
    xt = x.copy()
    traj = [xt.copy()]
    for _ in range(T):
        xt = step(xt, r, eps)
        traj.append(xt.copy())
    traj = np.array(traj)
    gmed = np.median(traj)
    seq = (traj > gmed).astype(np.int8)
    for k in range(1, 9):
        if np.all(seq[:-k] == seq[k:]):
            return k
    return None

def metrics(x, r, eps):
    x0 = x.copy()
    s1 = step(x0, r, eps)
    s2 = step(s1, r, eps)
    A = float(np.max(np.abs(s1 - x0)))
    B = float(np.max(np.abs(s2 - x0)))
    return A, B

N, seed = 100, 42
np.random.seed(seed)
x0 = np.random.rand(N)

rs = np.round(np.arange(3.84, 3.901, 0.01), 3)
es = np.round(np.arange(0.10, 0.181, 0.01), 3)
rows = []
print('r      eps   fP  sP    A      B     A/B')
for r in rs:
    for eps in es:
        x = x0.copy()
        for _ in range(1000):
            x = step(x, r, eps)
        fp = float_period(x, r, eps)
        sp = shadow_period(x, r, eps)
        A, B = metrics(x, r, eps)
        ratio = (A / B) if B > 1e-9 else np.nan
        rows.append([float(r), float(eps), fp if fp is not None else -1, sp if sp is not None else -1, A, B, ratio])
        print(f"{r:5.3f} {eps:5.3f} {str(fp):>4} {str(sp):>4} {A:7.4f} {B:7.4f} {ratio:7.3f}")

p4s2 = [(a, b) for (a, b, fp, sp, *_r) in rows if fp == 4 and sp == 2]
p4s4 = [(a, b) for (a, b, fp, sp, *_r) in rows if fp == 4 and sp == 4]
print('')
print('float-P4 & shadow-P2:', len(p4s2), p4s2[:10])
print('float-P4 & shadow-P4:', len(p4s4), p4s4[:10])
np.save('shadow_v3.npy', np.array(rows, dtype=float))
