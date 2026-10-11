#!/usr/bin/env python3
"""
Validate the Lyapunov estimator on the single logistic map (n=1, eps=0).
Known: r=4 -> lambda = ln(2) ~ 0.6931; r=3.9 -> ~ 0.5009; r=3.99 -> ~ 0.5719
"""

import numpy as np

def logistic(x, r):
    return r * x * (1 - x)

def lyapunov_single(r, x0, n_steps=20000, delta0=1e-10, renorm_interval=10):
    x = x0
    y = x + delta0
    log_growth = 0.0
    count = 0
    for t in range(n_steps):
        x = logistic(x, r)
        y = logistic(y, r)
        if (t + 1) % renorm_interval == 0:
            dist = abs(x - y)
            if dist < 1e-300:
                return -np.inf
            log_growth += np.log(dist / delta0)
            y = x + delta0 * np.sign(y - x)
            count += 1
    return log_growth / n_steps

if __name__ == "__main__":
    for r in [3.9, 3.99, 4.0]:
        lam = lyapunov_single(r, 0.3)
        print(f"r={r}: lambda = {lam:.6f}  (expected ~{0.5 if r<3.995 else 0.6931:.4f})")