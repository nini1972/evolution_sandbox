import numpy as np

def step(x, r, eps):
    fx = r * x * (1.0 - x)
    return (1.0 - eps) * fx + 0.5 * eps * (np.roll(fx, 1) + np.roll(fx, -1))

def float_period(x, r, eps, kmax=8):
    x0 = x
    best = None
    for k in range(1, kmax + 1):
        y = x.copy()
        for _ in range(k):
            y = step(y, r, eps)
        d = float(np.max(np.abs(y - x0)))
        if d < 1e-6:
            return k, d
        if best is None or d < best[1]:
            best = (k, d)
    return best

def symbol_period(x, r, eps, T=600):
    traj = [x.copy()]
    xt = x.copy()
    for _ in range(T):
        xt = step(xt, r, eps)
        traj.append(xt)
    traj = np.array(traj[1:])
    gmed = np.median(traj)
    b = (traj > gmed).astype(np.int8)
    def flip(k):
        if T - k < 10:
            return 0.5
        return float(np.mean(b[:-k] != b[k:]))
    f1, f2, f4 = flip(1), flip(2), flip(4)
    if f4 < 0.01 and f2 < 0.01:
        sp = 1
    elif f4 < 0.01 and f2 > 0.5:
        sp = 2
    elif f4 < 0.01 and f1 > 0.5 and f2 > 0.1:
        sp = 4
    elif f4 < 0.05:
        sp = 4 if f2 < 0.2 else 2
    else:
        sp = 0
    return sp, f1, f2, f4

def breathing(x, r, eps):
    S0 = x.copy()
    S2 = step(step(S0, r, eps), r, eps)
    return float(np.max(np.abs(S2 - S0)))

rs = np.round(np.arange(3.84, 3.9001, 0.01), 3)
es = np.round(np.arange(0.10, 0.1801, 0.01), 3)
N, seed, transient = 100, 42, 1000

rows = []
for r in rs:
    for eps in es:
        np.random.seed(seed)
        x = np.random.rand(N)
        for _ in range(transient):
            x = step(x, r, eps)
        fp, d = float_period(x, r, eps)
        sp, f1, f2, f4 = symbol_period(x, r, eps)
        br = breathing(x, r, eps)
        rows.append((float(r), float(eps), fp, d, sp, f1, f2, f4, br))

hdr = '{:>6s} {:>5s} {:>7s} {:>7s} {:>5s} {:>6s} {:>6s} {:>6s} {:>7s}'.format(
    'r', 'eps', 'floatP', 'd', 'symP', 'f1', 'f2', 'f4', 'breath')
print(hdr)
for row in rows:
    print('{:6.3f} {:5.3f} {:>7d} {:7.4f} {:5d} {:6.3f} {:6.3f} {:6.3f} {:7.4f}'.format(*row))

f4s2 = [(row[0], row[1]) for row in rows if row[2] == 4 and row[4] == 2]
f4s4 = [(row[0], row[1]) for row in rows if row[2] == 4 and row[4] == 4]
print('')
print('float-P4 & sym-P2 (shadow folding):', len(f4s2), 'pts', f4s2[:10])
print('float-P4 & sym-P4 (true symbolic P4):', len(f4s4), 'pts', f4s4[:10])
np.save('shadow_grid.npy', np.array(rows, dtype=float))
