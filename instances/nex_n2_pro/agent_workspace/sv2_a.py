import numpy as np

def step(x, r, eps):
    fx = r * x * (1.0 - x)
    return (1.0 - eps) * fx + 0.5 * eps * (np.roll(fx, 1) + np.roll(fx, -1))

def evolve(x, r, eps, n):
    for _ in range(n):
        x = step(x, r, eps)
    return x

def stats(x0, r, eps, T=400, transient=800):
    x = evolve(x0.copy(), r, eps, transient)
    S0 = x.copy()
    S1 = step(S0, r, eps)
    S2 = step(S1, r, eps)
    A = float(np.max(np.abs(S1 - S0)))
    B = float(np.max(np.abs(S2 - S0)))
    traj = [S0]
    xt = S0
    for _ in range(T):
        xt = step(xt, r, eps)
        traj.append(xt)
    traj = np.array(traj)
    gmed = np.median(traj)
    b = (traj > gmed).astype(np.int8)
    f1 = float(np.mean(b[:-1] != b[1:]))
    f2 = float(np.mean(b[:-2] != b[2:]))
    f4 = float(np.mean(b[:-4] != b[4:]))
    if f4 < 0.01 and f2 < 0.01:
        sp = 1
    elif f4 < 0.01 and f2 > 0.5:
        sp = 2
    elif f4 < 0.05 and f2 < 0.2:
        sp = 4
    else:
        sp = 0
    return sp, f1, f2, f4, A, B
