import numpy as np

def step(x, r, eps):
    fx = r * x * (1.0 - x)
    return (1.0 - eps) * fx + 0.5 * eps * (np.roll(fx, 1) + np.roll(fx, -1))

def stats(x0, r, eps, T=500, transient=800):
    x = x0.copy()
    for _ in range(transient):
        x = step(x, r, eps)
    S0 = x.copy()
    S1 = step(S0, r, eps)
    S2 = step(S1, r, eps)
    S4 = step(step(S2, r, eps), r, eps)
    A = float(np.max(np.abs(S1 - S0)))       # antiphase jump
    B = float(np.max(np.abs(S2 - S0)))       # breathing
    traj = [S0]
    xt = S0
    for _ in range(T):
        xt = step(xt, r, eps)
        traj.append(xt)
    traj = np.array(traj)
    gmed = np.median(traj)
    b = (traj > gmed).astype(np.int8)
    def flip(k):
        return float(np.mean(b[:-k] != b[k:</think>

<tool_call>
<function=write_file>
<parameter=path>
shadow_v2.py