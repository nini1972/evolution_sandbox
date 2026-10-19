"""
Kuramoto Phase Diagram with Finite-Size Scaling (CORRECTED)
============================================================
Bug fix: coupling term sign was flipped. Also using RK4 integration.

Standard Kuramoto: dθ_i/dt = ω_i + K * Im(z * e^{-iθ_i})
                  = ω_i + K * (im*cos(θ_i) - re*sin(θ_i))
where z = re + i*im = (1/N) Σ e^{iθ_j}
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
import os

from numba import njit, prange

@njit(parallel=True, fastmath=True)
def kuramoto_rhs(theta, omega, re, im, K, N):
    """Compute dθ/dt = ω + K*(im*cos(θ) - re*sin(θ))"""
    dtheta = np.zeros(N)
    for j in prange(N):
        dtheta[j] = omega[j] + K * (im * np.cos(theta[j]) - re * np.sin(theta[j]))
    return dtheta

@njit(parallel=True, fastmath=True)
def kuramoto_step_rk4(theta, omega, K, N, dt):
    """One RK4 step."""
    # k1
    re1 = 0.0; im1 = 0.0
    for j in range(N):
        re1 += np.cos(theta[j])
        im1 += np.sin(theta[j])
    re1 /= N; im1 /= N
    k1 = kuramoto_rhs(theta, omega, re1, im1, K, N)

    # k2
    theta2 = theta + 0.5 * dt * k1
    re2 = 0.0; im2 = 0.0
    for j in range(N):
        re2 += np.cos(theta2[j])
        im2 += np.sin(theta2[j])
    re2 /= N; im2 /= N
    k2 = kuramoto_rhs(theta2, omega, re2, im2, K, N)

    # k3
    theta3 = theta + 0.5 * dt * k2
    re3 = 0.0; im3 = 0.0
    for j in range(N):
        re3 += np.cos(theta3[j])
        im3 += np.sin(theta3[j])
    re3 /= N; im3 /= N
    k3 = kuramoto_rhs(theta3, omega, re3, im3, K, N)

    # k4
    theta4 = theta + dt * k3
    re4 = 0.0; im4 = 0.0
    for j in range(N):
        re4 += np.cos(theta4[j])
        im4 += np.sin(theta4[j])
    re4 /= N; im4 /= N
    k4 = kuramoto_rhs(theta4, omega, re4, im4, K, N)

    theta += (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
    return theta

@njit(parallel=True, fastmath=True)
def compute_mean_field(theta, N):
    re = 0.0; im = 0.0
    for j in prange(N):
        re += np.cos(theta[j])
        im += np.sin(theta[j])
    re /= N; im /= N
    return re, im

def run_kuramoto(K, N, n_steps=3000, dt=0.02, seed=None, transient=1000):
    """Run the Kuramoto model and return time-averaged order parameter."""
    rng = np.random.default_rng(seed)
    theta = rng.uniform(0, 2 * np.pi, N).astype(np.float64)
    omega = rng.normal(0, 1, N).astype(np.float64)  # natural frequencies ~ N(0,1)
    K = float(K)

    # Equilibrate
    for t in range(transient):
        kuramoto_step_rk4(theta, omega, K, N, dt)

    # Measure order parameter
    R_vals = np.zeros(n_steps - transient)
    for t in range(transient, n_steps):
        kuramoto_step_rk4(theta, omega, K, N, dt)
        re, im = compute_mean_field(theta, N)
        R_vals[t - transient] = np.sqrt(re**2 + im**2)

    R_mean = R_vals.mean()
    R_std = R_vals.std()
    return R_mean, R_std


def main():
    # System sizes: logarithmically spaced for good scaling
    N_list = [64, 128, 256, 512, 1024, 2048, 4096]
    # Coupling range
    # For omega ~ N(0,1), the mean-field Kc = 2 / (pi * g(0)) = 2/pi ~ 0.6366
    K_min, K_max = 0.20, 1.20
    K_values = np.linspace(K_min, K_max, 50)

    print(f"N_list: {N_list}")
    print(f"Sweeping {len(K_values)} K values x {len(N_list)} N values")
    print(f"Numba parallel: {True}")

    R_mean_grid = np.zeros((len(N_list), len(K_values)))
    R_std_grid = np.zeros((len(N_list), len(K_values)))

    for i, N in enumerate(N_list):
        for j, K in enumerate(K_values):
            seed = 1000 + i * 1000 + j
            R_m, R_s = run_kuramoto(K, N, n_steps=3000, dt=0.02, seed=seed)
            R_mean_grid[i, j] = R_m
            R_std_grid[i, j] = R_s
        print(f"  N={N} done. R range: [{R_mean_grid[i].min():.4f}, {R_mean_grid[i].max():.4f}]")

    # --- Phase Diagram Plot ---
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    ax = axes[0]
    for i, N in enumerate(N_list):
        ax.plot(K_values, R_mean_grid[i], 'o-', markersize=3, label=f'N={N}')
    ax.axvline(x=2/np.pi, color='k', linestyle='--', alpha=0.5, label=f'Kc=2/π≈{2/np.pi:.4f}')
    ax.set_xlabel('Coupling K')
    ax.set_ylabel('Order Parameter R')
    ax.set_title('Kuramoto Order Parameter vs Coupling (RK4)')
    ax.legend(fontsize=7, ncol=2)
    ax.set_xlim(K_min, K_max)
    ax.set_ylim(-0.02, 1.05)
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    K_mesh, N_mesh = np.meshgrid(K_values, N_list)
    im = ax.pcolormesh(K_mesh, N_mesh, R_mean_grid, shading='auto', cmap='plasma')
    ax.axvline(x=2/np.pi, color='cyan', linestyle='--', alpha=0.7, label=f'Kc=2/π≈{2/np.pi:.4f}')
    plt.colorbar(im, ax=ax, label='Order Parameter R')
    ax.set_xlabel('Coupling K')
    ax.set_ylabel('System Size N')
    ax.set_title('Kuramoto Phase Diagram (K vs N)')
    ax.legend(fontsize=8, loc='upper left')
    plt.tight_layout()
    plt.savefig('kuramoto_phase_diagram.png', dpi=150)
    plt.close()
    print("Saved kuramoto_phase_diagram.png")

    # --- Finite-Size Scaling Analysis ---
    # Estimate Kc from steepest slope of largest-N curve
    R_large = R_mean_grid[-1]
    dR = np.gradient(R_large, K_values)
    idx_max_slope = int(np.argmax(dR))
    Kc_est = float(K_values[idx_max_slope])
    print(f"Estimated Kc: {Kc_est:.4f} (theoretical: {2/np.pi:.4f})")

    # Near-critical scaling: R ~ N^{-beta} at fixed K
    K_near = K_values[max(0, idx_max_slope - 3):idx_max_slope + 4]
    beta_estimates = []
    for kj in K_near:
        idx_K = int(np.argmin(np.abs(K_values - kj)))
        R_vs_N = R_mean_grid[:, idx_K]
        logN = np.log(np.array(N_list, dtype=float))
        logR = np.log(R_vs_N + 1e-12)
        coeffs = np.polyfit(logN, logR, 1)
        beta_estimates.append(float(-coeffs[0]))
    beta_mean = float(np.mean(beta_estimates)) if beta_estimates else 0.5
    print(f"Beta estimates near Kc: {[f'{b:.3f}' for b in beta_estimates]}")
    print(f"Mean beta: {beta_mean:.4f}")

    # Kc vs N extrapolation
    Kc_per_N = []
    for i, N in enumerate(N_list):
        dR_i = np.gradient(R_mean_grid[i], K_values)
        idx_i = int(np.argmax(dR_i))
        Kc_per_N.append(float(K_values[idx_i]))
    Kc_per_N = np.array(Kc_per_N)

    # --- Scaling collapse + extra plots ---
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # 1. Scaling collapse
    ax = axes[0]
    for i, N in enumerate(N_list):
        scaled_R = R_mean_grid[i] * (N ** beta_mean)
        ax.plot(K_values, scaled_R, 'o-', markersize=3, label=f'N={N}')
    ax.axvline(x=Kc_est, color='red', linestyle='--', alpha=0.7, label=f'Kc≈{Kc_est:.4f}')
    ax.set_xlabel('Coupling K')
    ax.set_ylabel(f'R · N^({beta_mean:.2f})')
    ax.set_title('Finite-Size Scaling Collapse')
    ax.legend(fontsize=6, ncol=2)
    ax.grid(True, alpha=0.3)

    # 2. Kc vs N
    ax = axes[1]
    ax.plot(1/np.array(N_list), Kc_per_N, 'o-', label='Estimated Kc(N)')
    ax.axhline(y=2/np.pi, color='red', linestyle='--', label=f'N→∞: Kc={2/np.pi:.4f}')
    ax.set_xlabel('1/N')
    ax.set_ylabel('Critical Coupling Kc')
    ax.set_title('Kc vs System Size')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # 3. R vs K-N collapsed
    ax = axes[2]
    for i, N in enumerate(N_list):
        scaled_R = R_mean_grid[i] * (N ** beta_mean)
        ax.plot(K_values - Kc_est, scaled_R, 'o-', markersize=3, label=f'N={N}')
    ax.axvline(x=0, color='red', linestyle='--', alpha=0.7)
    ax.set_xlabel('K - Kc')
    ax.set_ylabel(f'R · N^({beta_mean:.2f})')
    ax.set_title('Collapsed Order Parameter')
    ax.legend(fontsize=6)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('kuramoto_finite_size_scaling.png', dpi=150)
    plt.close()
    print("Saved kuramoto_finite_size_scaling.png")

    # --- Save JSON results ---
    results = {
        'N_list': N_list,
        'K_values': K_values.tolist(),
        'R_mean_grid': R_mean_grid.tolist(),
        'R_std_grid': R_std_grid.tolist(),
        'K_critical_estimated': Kc_est,
        'K_critical_theoretical': float(2 / np.pi),
        'beta_estimates': beta_estimates,
        'beta_mean': beta_mean,
        'Kc_per_N': Kc_per_N.tolist(),
        'method': 'RK4',
        'dt': 0.02,
        'n_steps': 3000,
        'transient': 1000,
    }
    with open('kuramoto_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("Saved kuramoto_results.json")

    # CSV
    with open('kuramoto_R_grid.csv', 'w') as f:
        f.write('N,K,R_mean,R_std\n')
        for i, N in enumerate(N_list):
            for j, K in enumerate(K_values):
                f.write(f'{N},{K:.6f},{R_mean_grid[i,j]:.6f},{R_std_grid[i,j]:.6f}\n')
    print("Saved kuramoto_R_grid.csv")

    print("\n=== JOB COMPLETE ===")


if __name__ == '__main__':
    main()
