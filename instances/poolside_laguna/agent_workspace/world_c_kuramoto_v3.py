"""
Kuramoto Phase Diagram v3 - CORRECTED K-range
=============================================
For omega ~ N(0,1): g(0) = 1/sqrt(2*pi), K_c = 2/(pi*g(0)) = 2*sqrt(2/pi) ~ 1.596
Need K range [0.3, 3.0] to capture the transition.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
from numba import njit, prange

Kc_theoretical = 2 * np.sqrt(2.0 / np.pi)  # ~1.5958
print(f"Theoretical Kc = 2*sqrt(2/pi) = {Kc_theoretical:.4f}")

@njit(parallel=True, fastmath=True)
def kuramoto_rhs(theta, omega, re, im, K, N):
    dtheta = np.zeros(N)
    for j in prange(N):
        dtheta[j] = omega[j] + K * (im * np.cos(theta[j]) - re * np.sin(theta[j]))
    return dtheta

@njit(parallel=True, fastmath=True)
def kuramoto_step_rk4(theta, omega, K, N, dt):
    re1 = 0.0; im1 = 0.0
    for j in range(N):
        re1 += np.cos(theta[j]); im1 += np.sin(theta[j])
    re1 /= N; im1 /= N
    k1 = kuramoto_rhs(theta, omega, re1, im1, K, N)

    theta2 = theta + 0.5 * dt * k1
    re2 = 0.0; im2 = 0.0
    for j in range(N):
        re2 += np.cos(theta2[j]); im2 += np.sin(theta2[j])
    re2 /= N; im2 /= N
    k2 = kuramoto_rhs(theta2, omega, re2, im2, K, N)

    theta3 = theta + 0.5 * dt * k2
    re3 = 0.0; im3 = 0.0
    for j in range(N):
        re3 += np.cos(theta3[j]); im3 += np.sin(theta3[j])
    re3 /= N; im3 /= N
    k3 = kuramoto_rhs(theta3, omega, re3, im3, K, N)

    theta4 = theta + dt * k3
    re4 = 0.0; im4 = 0.0
    for j in range(N):
        re4 += np.cos(theta4[j]); im4 += np.sin(theta4[j])
    re4 /= N; im4 /= N
    k4 = kuramoto_rhs(theta4, omega, re4, im4, K, N)

    theta += (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
    return theta

@njit(parallel=True, fastmath=True)
def compute_mean_field(theta, N):
    re = 0.0; im = 0.0
    for j in prange(N):
        re += np.cos(theta[j]); im += np.sin(theta[j])
    re /= N; im /= N
    return re, im

def run_kuramoto(K, N, n_steps=4000, dt=0.01, seed=None, transient=2000):
    rng = np.random.default_rng(seed)
    theta = rng.uniform(0, 2*np.pi, N).astype(np.float64)
    omega = rng.normal(0, 1, N).astype(np.float64)
    K = float(K)
    for t in range(transient):
        kuramoto_step_rk4(theta, omega, K, N, dt)
    R_vals = np.zeros(n_steps - transient)
    for t in range(transient, n_steps):
        kuramoto_step_rk4(theta, omega, K, N, dt)
        re, im = compute_mean_field(theta, N)
        R_vals[t - transient] = np.sqrt(re**2 + im**2)
    return R_vals.mean(), R_vals.std()

def main():
    N_list = [128, 256, 512, 1024, 2048, 4096]
    # Dense K range around expected Kc ~ 1.596
    K_values = np.concatenate([
        np.linspace(0.3, 1.3, 20),
        np.linspace(1.35, 2.1, 40),
        np.linspace(2.2, 3.0, 15)
    ])
    print(f"N_list: {N_list}")
    print(f"Sweeping {len(K_values)} K values x {len(N_list)} N values")

    R_mean_grid = np.zeros((len(N_list), len(K_values)))
    R_std_grid = np.zeros((len(N_list), len(K_values)))

    for i, N in enumerate(N_list):
        for j, K in enumerate(K_values):
            seed = 1000 + i * 10000 + j
            R_m, R_s = run_kuramoto(K, N, n_steps=4000, dt=0.01, seed=seed)
            R_mean_grid[i, j] = R_m
            R_std_grid[i, j] = R_s
        print(f"  N={N} done. R range: [{R_mean_grid[i].min():.4f}, {R_mean_grid[i].max():.4f}]")

    # --- Phase Diagram ---
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    ax = axes[0]
    for i, N in enumerate(N_list):
        ax.plot(K_values, R_mean_grid[i], 'o-', markersize=2, label=f'N={N}')
    ax.axvline(x=Kc_theoretical, color='k', linestyle='--', alpha=0.7, label=f'Kc=2√(2/π)≈{Kc_theoretical:.4f}')
    ax.set_xlabel('Coupling K'); ax.set_ylabel('Order Parameter R')
    ax.set_title('Kuramoto Order Parameter vs Coupling (RK4)'); ax.legend(fontsize=7, ncol=2)
    ax.set_ylim(-0.02, 1.05); ax.grid(True, alpha=0.3)
    ax = axes[1]
    K_mesh, N_mesh = np.meshgrid(K_values, N_list)
    im = ax.pcolormesh(K_mesh, N_mesh, R_mean_grid, shading='auto', cmap='viridis')
    ax.axvline(x=Kc_theoretical, color='red', linestyle='--', alpha=0.7, label=f'Kc≈{Kc_theoretical:.4f}')
    plt.colorbar(im, ax=ax, label='Order Parameter R')
    ax.set_xlabel('Coupling K'); ax.set_ylabel('System Size N')
    ax.set_title('Kuramoto Phase Diagram'); ax.legend(fontsize=8, loc='upper left')
    plt.tight_layout(); plt.savefig('kuramoto_phase_diagram_v3.png', dpi=150); plt.close()
    print("Saved kuramoto_phase_diagram_v3.png")

    # --- Find Kc: steepest slope of largest N ---
    R_large = R_mean_grid[-1]
    dR = np.gradient(R_large, K_values)
    idx_max_slope = int(np.argmax(dR))
    Kc_est = float(K_values[idx_max_slope])
    print(f"\nEstimated Kc (largest N): {Kc_est:.4f}")
    print(f"Theoretical Kc: {Kc_theoretical:.4f}")
    print(f"Relative error: {abs(Kc_est - Kc_theoretical)/Kc_theoretical * 100:.2f}%")

    # --- Finite-size scaling analysis ---
    # Below Kc: R ~ N^(-1/2) (fluctuations), beta = 1/2
    # Above Kc: R_inf - R(N) ~ N^(-1/2) (finite-size correction)

    # Estimate beta below Kc: use a K well below Kc
    K_below = Kc_est * 0.9
    idx_below = int(np.argmin(np.abs(K_values - K_below)))
    R_vs_N_below = R_mean_grid[:, idx_below]

    logN = np.log(np.array(N_list, dtype=float))
    logR = np.log(R_vs_N_below + 1e-15)
    beta_below = float(-np.polyfit(logN, logR, 1)[0])
    print(f"\nBelow Kc (K={K_below:.3f}): R ~ N^(-beta), beta = {beta_below:.4f} (theoretical: 0.5)")

    # Above Kc: R_inf - R(N) ~ N^(-1/2)
    K_above = Kc_est * 1.1
    idx_above = int(np.argmin(np.abs(K_values - K_above)))
    R_vs_N_above = R_mean_grid[:, idx_above]
    R_inf_est = R_vs_N_above[-1]  # approximate
    diffs = R_inf_est - R_vs_N_above
    diffs = diffs[diffs > 1e-12]
    log_diffs = np.log(diffs)
    # This is the finite-size correction exponent
    if len(diffs) > 2:
        alpha_corr = float(-np.polyfit(logN[:len(diffs)], log_diffs, 1)[0])
        print(f"Above Kc (K={K_above:.3f}): R_inf - R ~ N^(-alpha), alpha = {alpha_corr:.4f} (theoretical: 0.5)")

    # --- Kc vs N extrapolation ---
    Kc_per_N = []
    for i, N in enumerate(N_list):
        dR_i = np.gradient(R_mean_grid[i], K_values)
        idx_i = int(np.argmax(dR_i))
        Kc_per_N.append(float(K_values[idx_i]))
    Kc_per_N = np.array(Kc_per_N)
    print(f"\nKc(N) estimates: {Kc_per_N}")

    # --- Scaling collapse ---
    beta_collapse = 0.5  # theoretical mean-field value
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    ax = axes[0]
    for i, N in enumerate(N_list):
        scaled_R = R_mean_grid[i] * (float(N) ** beta_collapse)
        ax.plot(K_values, scaled_R, 'o-', markersize=2, label=f'N={N}')
    ax.axvline(x=Kc_est, color='red', linestyle='--', alpha=0.7, label=f'Kc≈{Kc_est:.4f}')
    ax.set_xlabel('K'); ax.set_ylabel(f'R · N^({beta_collapse})')
    ax.set_title('Scaling Collapse (beta=0.5)'); ax.legend(fontsize=6); ax.grid(True, alpha=0.3)

    ax = axes[1]
    ax.plot(1/np.array(N_list, dtype=float), Kc_per_N, 'o-', label='Estimated Kc(N)')
    ax.axhline(y=Kc_theoretical, color='red', linestyle='--', label=f'N→∞: Kc={Kc_theoretical:.4f}')
    ax.set_xlabel('1/N'); ax.set_ylabel('Kc')
    ax.set_title('Kc vs System Size'); ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

    ax = axes[2]
    for i, N in enumerate(N_list):
        shifted_K = (np.array(K_values) - Kc_est) * float(N)
        ax.plot(shifted_K, R_mean_grid[i], 'o-', markersize=2, label=f'N={N}')
    ax.axvline(x=0, color='red', linestyle='--', alpha=0.7)
    ax.set_xlabel('N·(K - Kc)')
    ax.set_ylabel(f'R · N^({beta_collapse})')
    ax.set_title('Rescaled Phase Transition')
    ax.legend(fontsize=6); ax.grid(True, alpha=0.3)

    plt.tight_layout(); plt.savefig('kuramoto_finite_size_scaling_v3.png', dpi=150); plt.close()
    print("Saved kuramoto_finite_size_scaling_v3.png")

    # --- Save results ---
    results = {
        'N_list': N_list,
        'K_values': K_values.tolist(),
        'R_mean_grid': R_mean_grid.tolist(),
        'R_std_grid': R_std_grid.tolist(),
        'K_critical_estimated': Kc_est,
        'K_critical_theoretical': float(Kc_theoretical),
        'beta_below_Kc': beta_below,
        'beta_theoretical': 0.5,
        'Kc_per_N': Kc_per_N.tolist(),
        'method': 'RK4_numba',
        'dt': 0.01,
        'n_steps': 4000,
        'transient': 2000,
    }
    with open('kuramoto_results_v3.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("Saved kuramoto_results_v3.json")
    print("\n=== JOB COMPLETE ===")

if __name__ == '__main__':
    main()
