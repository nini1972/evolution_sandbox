#!/usr/bin/env python3
"""
Test different parameters for genuine spatiotemporal chaos
"""

import numpy as np

def coupled_logistic_map(x, r, epsilon):
    """Evolve coupled logistic map lattice one time step."""
    n = len(x)
    f_x = r * x * (1 - x)
    f_left = np.roll(f_x, 1)
    f_right = np.roll(f_x, -1)
    return (1 - epsilon) * f_x + (epsilon / 2) * (f_left + f_right)

def test_parameters(r, epsilon):
    """Test if parameters produce chaos."""
    
    n_cells = 100
    
    # Initialize
    np.random.seed(42)
    x = np.random.rand(n_cells)
    
    # Transient
    for _ in range(1000):
        x = coupled_logistic_map(x, r, epsilon)
    
    # Record trajectory
    trajectory = []
    for _ in range(200):
        x = coupled_logistic_map(x, r, epsilon)
        trajectory.append(x.copy())
    
    trajectory = np.array(trajectory)
    
    # Check for periodicity
    max_period = 20
    min_error = float('inf')
    best_period = None
    
    for period in range(1, max_period + 1):
        errors = []
        for t in range(len(trajectory) - period):
            error = np.mean(np.abs(trajectory[t] - trajectory[t + period]))
            errors.append(error)
        mean_error = np.mean(errors)
        if mean_error < min_error:
            min_error = mean_error
            best_period = period
    
    print(f"r={r}, ε={epsilon}:")
    print(f"  Best period: {best_period}, Mean error: {min_error:.6f}")
    
    # Check Lyapunov-like indicator (consecutive differences)
    diffs = np.diff(trajectory, axis=0)
    mean_diff = np.mean(np.abs(diffs))
    std_diff = np.std(np.abs(diffs))
    
    print(f"  Mean consecutive diff: {mean_diff:.6f} ± {std_diff:.6f}")
    
    # Check if trajectory explores full range
    traj_min = np.min(trajectory)
    traj_max = np.max(trajectory)
    traj_range = traj_max - traj_min
    
    print(f"  Trajectory range: [{traj_min:.6f}, {traj_max:.6f}] (span: {traj_range:.6f})")
    
    return min_error, best_period, mean_diff

if __name__ == "__main__":
    # Test multiple parameter combinations
    test_cases = [
        (3.865, 0.132),  # Our original case
        (3.95, 0.2),     # Stronger chaos candidate
        (3.98, 0.1),     # Very high r, weak coupling
        (3.9, 0.3),      # Moderate r, stronger coupling
        (4.0, 0.15),     # Maximum r
    ]
    
    results = []
    for r, epsilon in test_cases:
        min_error, best_period, mean_diff = test_parameters(r, epsilon)
        results.append((r, epsilon, min_error, best_period, mean_diff))
        print()
    
    # Find the most chaotic case (highest mean_diff and no clear periodicity)
    most_chaotic = max(results, key=lambda x: (x[4], -x[2]))  # High diff, low periodicity error
    print(f"Most chaotic parameters: r={most_chaotic[0]}, ε={most_chaotic[1]}")
    print(f"  Periodicity error: {most_chaotic[2]:.6f}, Best period: {most_chaotic[3]}")
    print(f"  Mean consecutive diff: {most_chaotic[4]:.6f}")