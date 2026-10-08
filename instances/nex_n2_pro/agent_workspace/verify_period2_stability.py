#!/usr/bin/env python3
"""
Verify the period-2 orbit stability over longer time
"""

import numpy as np

def coupled_logistic_map(x, r, epsilon):
    """Evolve coupled logistic map lattice one time step."""
    n = len(x)
    f_x = r * x * (1 - x)
    f_left = np.roll(f_x, 1)
    f_right = np.roll(f_x, -1)
    return (1 - epsilon) * f_x + (epsilon / 2) * (f_left + f_right)

def verify_period2():
    """Verify period-2 stability."""
    
    r = 3.865
    epsilon = 0.132
    n_cells = 100
    
    # Initialize
    np.random.seed(42)
    x = np.random.rand(n_cells)
    
    # Transient
    for _ in range(1000):
        x = coupled_logistic_map(x, r, epsilon)
    
    # Record long trajectory
    trajectory = []
    for _ in range(100):
        x = coupled_logistic_map(x, r, epsilon)
        trajectory.append(x.copy())
    
    trajectory = np.array(trajectory)
    
    # Check period-2 consistency
    errors = []
    for t in range(0, len(trajectory)-2, 2):
        if t+2 < len(trajectory):
            error = np.mean(np.abs(trajectory[t] - trajectory[t+2]))
            errors.append(error)
    
    print(f"Period-2 reconstruction errors (mean ± std): {np.mean(errors):.2e} ± {np.std(errors):.2e}")
    print(f"Maximum error: {np.max(errors):.2e}")
    print(f"Number of comparisons: {len(errors)}")
    
    # Check if it's truly period-2 vs higher periods
    period4_errors = []
    for t in range(len(trajectory)-4):
        error = np.mean(np.abs(trajectory[t] - trajectory[t+4]))
        period4_errors.append(error)
    
    print(f"Period-4 reconstruction errors: {np.mean(period4_errors):.2e} ± {np.std(period4_errors):.2e}")
    
    # Check period-1 (fixed point)
    period1_errors = []
    for t in range(len(trajectory)-1):
        error = np.mean(np.abs(trajectory[t] - trajectory[t+1]))
        period1_errors.append(error)
    
    print(f"Period-1 reconstruction errors: {np.mean(period1_errors):.2e} ± {np.std(period1_errors):.2e}")

if __name__ == "__main__":
    verify_period2()