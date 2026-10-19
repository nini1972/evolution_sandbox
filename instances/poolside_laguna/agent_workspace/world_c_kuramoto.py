"""
Kuramoto R^alpha Phase Diagram with Finite-Size Scaling
========================================================
World C high-performance compute job.

This script investigates the Kuramoto oscillator model across a range of
coupling strengths K and system sizes N, measuring the order parameter R
and its critical scaling. It sweeps the (K, N) phase space, computes the
time-averaged order parameter, detects the critical coupling Kc, and
performs finite-size scaling to extract the infinite-N critical point
and critical exponent.

Uses Numba JIT acceleration for speed.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
import os

# ---------------------------------------------------------------------------
# JIT-accelerated core: Kuramoto simulation
# ---------------------------------------------------------------------------
try:
    from numba import njit, prange
    HAVE_NUMBA = True
except ImportError:
    HAVE_NUMBA = False

if HAVE_NUMBA:
    @njit(parallel=True, fastmath=True)
    def _kuramoto_step(theta, omega, K, N, dt):
        """One RK4 step of the Kuramoto ODE for N oscillators."""
        # Compute mean field
        # z = (1/N) * sum_j exp(i theta_j)
        re = 0.0
        im = 0.0
        for j in range(N):
            re += np.cos(theta[j])
            im += np.sin(theta[j])
        re /= N
        im /= N

        # RHS: dtheta/dt = omega + K * Im(z * exp(-i theta))
        #     K * (re * sin(theta) - im * cos(theta))
        for j in prange(N):
            rhs = omega[j] + K * (re * np.sin(theta[j]) - im * np.cos(theta[j]))
            theta[j] += dt * rhs
else:
    def _kuramoto_step(theta, omega, K, N, dt):
        re = np.cos(theta).mean()
        im = np.sin(theta).mean()
        rhs = omega + K * (re * np.sin(theta) - im * np.cos(theta))
        theta += dt * rhs

# ---------------------------------------------------------------------------
# Simulation driver
# ---------------------------------------------------------------------------
def run_kuramoto(K, N, n_steps=2000, dt=0.05, seed=None, transient=500):
    """Run the Kuramoto model and return time-averaged order parameter."""
    rng = np.random.default_rng(seed)
    theta = rng.uniform(0, 2*np.pi, N)
    omega = rng.normal(0, 1, N)  # natural frequencies ~ N(0,1)
    K = float(K)
    for t in range(n_steps):
        _kuramoto_step(theta, omega, K, N, dt)
    # Measure order parameter after transient
    R_vals = np.zeros(n_steps - transient)
    for t in range(transient, n_steps):
        re = np.cos(theta).mean()
        im = np.sin(theta).mean()
        R_vals[t - transient] = np.sqrt(re**2 + im**2)
        _kuramoto_step(theta, omega, K, N, dt)
    R_mean = R_vals.mean()
    R_std = R_vals.std()
    return R_mean, R_std

# ---------------------------------------------------------------------------
# Parameter sweep
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    # Check if colony_lib is available for additional tools
    try:
        from colony_lib.scaling import extract_finite_size_scaling
        from colony_lib.datasets import load_dataset
        HAVE_COLONY = True
    except ImportError:
        HAVE_COLONY = False

    # System sizes: logarithmically spaced
    N_list = [100, 200, 400, 800, 1600, 3200]
    # Coupling range: well below critical, around critical, well above
    # For omega ~ N(0,1), the mean-field Kc = 2 / (pi * g(0)) = 2/pi ~ 0.6366
    K_min, K_max = 0.30, 1.10
    K_values = np.linspace(K_min, K_max, 40)

    print(f"HAVE_NUMBA: {HAVE_NUMBA}")
    print(f"HAVE_COLONY: {HAVE_COLONY}")
    print(f"N_list: {N_list}")
    print(f"K_values: {len(K_values)} points from {K_min} to {K_max}")

    # Storage: R[N][K]
    R_mean_grid = np.zeros((len(N_list), len(K_values)))
    R_std_grid = np.zeros((len(N_list), len(K_values)))

    for i, N in enumerate(N_list):
        for j, K in enumerate(K_values):
            seed = 1000 + i * 1000 + j
            R_m, R_s = run_kuramoto(K, N, n_steps=2000, dt=0.05, seed=seed)
            R_mean_grid[i, j] = R_m
            R_std_grid[i, j] = R_s
        print(f"  N={N} done. R range: [{R_mean_grid[i].min():.4f}, {R_mean_grid[i].max():.4f}]")

    # --- Phase Diagram Plot ---
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Left: R vs K for different N
    ax = axes[0]
    for i, N in enumerate(N_list):
        ax.plot(K_values, R_mean_grid[i], 'o-', markersize=3, label=f'N={N}')
    ax.axvline(x=2/np.pi, color='k', linestyle='--', alpha=0.5, label=f'Kc=2/π≈{2/np.pi:.4f}')
    ax.set_xlabel('Coupling K')
    ax.set_ylabel('Order Parameter R')
    ax.set_title('Kuramoto Order Parameter vs Coupling')
    ax.legend(fontsize=8)
    ax.set_xlim(K_min, K_max)
    ax.set_ylim(-0.02, 1.05)
    ax.grid(True, alpha=0.3)

    # Right: Phase diagram (color = R)
    ax = axes[1]
    K_mesh, N_mesh = np.meshgrid(K_values, N_list)
    im = ax.pcolormesh(K_mesh, N_mesh, R_mean_grid, shading='auto', cmap='viridis')
    ax.axvline(x=2/np.pi, color='red', linestyle='--', alpha=0.7, label=f'Kc=2/π≈{2/np.pi:.4f}')
    plt.colorbar(im, ax=ax, label='Order Parameter R')
    ax.set_xlabel('Coupling K')
    ax.set_ylabel('System Size N')
    ax.set_title('Kuramoto Phase Diagram (K vs N)')
    ax.legend(fontsize=8)
    plt.setp(ax.get_yticklabels(), rotation=0)

    plt.tight_layout()
    plt.savefig('kuramoto_phase_diagram.png', dpi=150)
    plt.close()
    print("Saved kuramoto_phase_diagram.png")

    # --- Finite-Size Scaling Analysis ---
    # At each K, find the critical exponent via dR/dK for the largest N as proxy
    # Also try finite-size scaling collapse
    from numpy.polynomial import polynomial as P

    # Estimate Kc by looking at where the largest-N curve has steepest slope
    N_large = N_list[-1]
    R_large = R_mean_grid[-1]
    # Numerical derivative
    dR = np.gradient(R_large, K_values)
    idx_max_slope = np.argmax(dR)
    Kc_est = K_values[idx_max_slope]
    print(f"Estimated Kc (steepest slope): {Kc_est:.4f} (theoretical: {2/np.pi:.4f})")

    # Finite-size scaling: R ~ N^{-beta} near critical
    # For each K near Kc, fit R vs N
    K_near = K_values[idx_max_slope - 2 : idx_max_slope + 3]
    beta_estimates = []
    for kj in K_near:
        idx_K = np.argmin(np.abs(K_values - kj))
        R_vs_N = R_mean_grid[:, idx_K]
        # Fit log(R) vs log(N): R = a * N^b  => log R = log a + b log N
        logN = np.log(np.array(N_list, dtype=float))
        logR = np.log(R_vs_N + 1e-12)
        coeffs = np.polyfit(logN, logR, 1)
        beta_estimates.append(-coeffs[0])  # R ~ N^{-beta} => b = -beta

    print(f"Beta estimates near Kc: {beta_estimates}")
    beta_mean = np.mean(beta_estimates) if beta_estimates else 0.5
    print(f"Mean beta: {beta_mean:.4f}")

    # --- Scaling Collapse Plot ---
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # 1. Scaling collapse: R*N^beta vs K
    ax = axes[0]
    for i, N in enumerate(N_list):
        scaled_R = R_mean_grid[i] * (N ** beta_mean)
        ax.plot(K_values, scaled_R, 'o-', markersize=3, label=f'N={N}')
    ax.axvline(x=Kc_est, color='red', linestyle='--', alpha=0.7, label=f'Kc≈{Kc_est:.4f}')
    ax.set_xlabel('Coupling K')
    ax.set_ylabel(f'R * N^{beta_mean:.2f}')
    ax.set_title('Finite-Size Scaling Collapse')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # 2. Critical coupling vs N (extrapolation to 1/N -> 0)
    ax = axes[1]
    # Re-estimate Kc for each N
    Kc_per_N = []
    for i, N in enumerate(N_list):
        dR_i = np.gradient(R_mean_grid[i], K_values)
        idx_i = np.argmax(dR_i)
        Kc_per_N.append(K_values[idx_i])
    Kc_per_N = np.array(Kc_per_N)
    ax.plot(1/np.array(N_list), Kc_per_N, 'o-', label='Estimated Kc(N)')
    ax.axhline(y=2/np.pi, color='red', linestyle='--', label=f'1/N → 0: Kc={2/np.pi:.4f}')
    ax.set_xlabel('1/N')
    ax.set_ylabel('Critical Coupling Kc')
    ax.set_title('Kc vs System Size')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # 3. Order parameter near critical for different N (log-log)
    ax = axes[2]
    for i, N in enumerate(N_list):
        if R_mean_grid[i, idx_max_slope] > 0.01:  # only if R > 0
            ax.plot(K_values[K_values >= Kc_est],
                    R_mean_grid[i, K_values >= Kc_est],
                    'o-', markersize=3, label=f'N={N}')
    ax.set_xlabel('K - Kc')
    ax.set_ylabel('R')
    ax.set_title('Order Parameter above Kc')
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3, which='both')
    ax.set_yscale('log')

    plt.tight_layout()
    plt.savefig('kuramoto_finite_size_scaling.png', dpi=150)
    plt.close()
    print("Saved kuramoto_finite_size_scaling.png")

    # --- Save numerical results ---
    results = {
        'N_list': N_list,
        'K_values': K_values.tolist(),
        'R_mean_grid': R_mean_grid.tolist(),
        'K_critical_estimated': Kc_est,
        'K_critical_theoretical': float(2 / np.pi),
        'beta_estimates': beta_estimates,
        'beta_mean': beta_mean,
        'Kc_per_N': Kc_per_N.tolist(),
        'HAVE_NUMBA': HAVE_NUMBA,
        'HAVE_COLONY': HAVE_COLONY,
    }
    with open('kuramoto_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("Saved kuramoto_results.json")

    # Also save the R grid as CSV
    with open('kuramoto_R_grid.csv', 'w') as f:
        f.write('N,K,R_mean,R_std\n')
        for i, N in enumerate(N_list):
            for j, K in enumerate(K_values):
                f.write(f'{N},{K:.6f},{R_mean_grid[i,j]:.6f},{R_std_grid[i,j]:.6f}\n')
    print("Saved kuramoto_R_grid.csv")

    print("\n=== JOB COMPLETE ===")
