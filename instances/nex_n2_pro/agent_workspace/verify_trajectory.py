#!/usr/bin/env python3
"""
Verify that the trajectory is actually chaotic and not artificially periodic
"""

import numpy as np
import matplotlib.pyplot as plt

# Set non-interactive backend
import matplotlib
matplotlib.use('Agg')

def coupled_logistic_map(x, r, epsilon):
    """Evolve coupled logistic map lattice one time step."""
    n = len(x)
    f_x = r * x * (1 - x)
    f_left = np.roll(f_x, 1)
    f_right = np.roll(f_x, -1)
    return (1 - epsilon) * f_x + (epsilon / 2) * (f_left + f_right)

def verify_chaos():
    """Verify the system is actually chaotic."""
    
    r = 3.865
    epsilon = 0.132
    n_cells = 100
    
    # Initialize
    np.random.seed(42)
    x = np.random.rand(n_cells)
    
    # Transient
    for _ in range(1000):
        x = coupled_logistic_map(x, r, epsilon)
    
    # Record trajectory
    trajectory = []
    for _ in range(100):
        x = coupled_logistic_map(x, r, epsilon)
        trajectory.append(x.copy())
    
    trajectory = np.array(trajectory)
    
    # Check if it's actually varying
    print("Trajectory statistics:")
    print(f"Mean: {np.mean(trajectory):.6f}")
    print(f"Std: {np.std(trajectory):.6f}")
    print(f"Min: {np.min(trajectory):.6f}")
    print(f"Max: {np.max(trajectory):.6f}")
    
    # Check consecutive differences
    diffs = np.diff(trajectory, axis=0)
    print(f"Mean consecutive difference: {np.mean(np.abs(diffs)):.6f}")
    print(f"Std of consecutive differences: {np.std(np.abs(diffs)):.6f}")
    
    # Check if any two time steps are identical
    identical_pairs = 0
    total_pairs = 0
    for i in range(len(trajectory)):
        for j in range(i+1, len(trajectory)):
            if np.allclose(trajectory[i], trajectory[j], atol=1e-10):
                identical_pairs += 1
            total_pairs += 1
    
    print(f"Identical time step pairs: {identical_pairs}/{total_pairs}")
    
    # Plot first few time steps
    plt.figure(figsize=(12, 8))
    for i in range(min(10, len(trajectory))):
        plt.plot(trajectory[i], label=f't={i}', alpha=0.7)
    plt.xlabel('Cell Index')
    plt.ylabel('Value')
    plt.title('First 10 Time Steps of Trajectory')
    plt.legend()
    plt.savefig('trajectory_verification.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    # Plot time series for first cell
    plt.figure(figsize=(12, 4))
    plt.plot(trajectory[:, 0], 'b-', linewidth=1)
    plt.xlabel('Time')
    plt.ylabel('Value (Cell 0)')
    plt.title('Time Series for First Cell')
    plt.savefig('cell0_timeseries.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    return trajectory

if __name__ == "__main__":
    traj = verify_chaos()