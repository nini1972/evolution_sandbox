#!/usr/bin/env python3
"""
Sweep coupling strength epsilon at r=4.0 to find the spatiotemporal chaos window
using the largest Lyapunov exponent (renormalized separation method).
"""

import numpy as np

def coupled_logistic_map(x, r, epsilon):
    n = len(x)
    f_x = r * x * (1 - x)
    f_left = np.roll(f_x, 1)
    f_right = np.roll(f_x, -1)
    return (1 - epsilon) * f_x + (epsilon / 2) * (f_left + f_right)

def lyapunov_1d_cml(r, epsilon, n_cells=100, n_steps=3000, delta0=1e-8, renorm_interval=10):
    """
    Estimate the largest Lyapunov exponent of the CML via the
    two-nearby-trajectories + renormalization method, measuring the
    mean per-cell absolute deviation as the distance metric.
    """
    np.random.seed(7)
    x = np.random.rand(n_cells)
    y = x + delta0 * np.random.randn(n_cells)
    y = np.clip(y, 1e-12, 1 - 1e-12)

    log_growth = 0.0
    count = 0
    for t in range(n_steps):
        x = coupled_logistic_map(x, r, epsilon)
        y = coupled_logistic_map(y, r, epsilon)
        if (t + 1) % renorm_interval == 0:
            dist = np.mean(np.abs(x - y))
            if dist < 1e-15:
                return -np.inf
            log_growth += np.log(dist / delta0)
            # renormalize y back to distance delta0 along the direction of separation
            direction = (y - x) / dist
            y = x + delta0 * direction
            count += 1
    return log_growth / n_steps * renorm_interval  # per time step

if __name__ == "__main__":
    r = 4.0
    epsilons = [0.001, 0.003, 0.005, 0.01, 0.02, 0.03, 0.05, 0.08, 0.1, 0.132, 0.15, 0.2, 0.3, 0.5]
    print(f"{'epsilon':>10} {'lambda1':>12}  verdict")
    print("-" * 40)
    results = []
    for eps in epsilons:
        lam = lyapunov_1d_cml(r, eps)
        verdict = "CHAOTIC" if lam > 0.01 else ("marginal" if lam > -0.005 else "ordered")
        print(f"{eps:>10} {lam:>12.4f}  {verdict}")
        results.append((eps, lam))