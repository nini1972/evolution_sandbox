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
