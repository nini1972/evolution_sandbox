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

def shadow_period(x, r, eps, T=400, tol=0.02):
    xt = x
    traj = [xt.copy()]
    for _ in range(T):
       </think>

<tool_call>
<function=write_file>
<parameter=path>
sv3_b.py