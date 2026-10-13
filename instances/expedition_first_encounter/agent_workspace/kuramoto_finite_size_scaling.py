#!/usr/bin/env python3
"""
Kuramoto Finite-Size Scaling Experiment
=========================================
Co-authored by InvariantMind-v1 (theory) and GLM 5.2 (implementation).

Tests the finite-size scaling ansatz:
    ΔK_c(N) = K_c(N) - K_c(∞) ~ N^{-1/2}    (critical coupling shift)
    <(δR)^2>_{K_c} ~ N^{-γ}                   (order parameter fluctuations)

For uniform frequency distribution g(ω) = 1/2 on [-1, 1]:
    K_c(∞) = 2 / (π · g(0)) = 4/π ≈ 1.27324

Vectorized implementation: all N oscillators integrated simultaneously
via numpy array operations with Heun (improved Euler) integration.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
from pathlib import Path

# ─── Parameters ───────────────────────────────────────────────────────────
SEED = 42
N_LIST = [32, 64, 128, 256, 512, 1024, 2048]
K_RANGE = np.arange(0.6, 2.0, 0.01)   # high-resolution K sweep (ΔK = 0.01)
DT = 0.01                              # integration timestep
T_TRANS = 50.0                         # transient time to discard
T_MEASURE = 100.0                      # measurement window
N_REALIZATIONS = 20                    # independent realizations per (N, K)

# ─── Theory ──────────────────────────────────────────────────────────────
KC_INF = 4.0 / np.pi  # ≈ 1.27324 for uniform g(ω) on [-1,1]


def kuramoto_step(theta, omega, K, N, dt):
    """One Heun (improved Euler) step for the Kuramoto model.
    
    dθ_i/dt = ω_i + (K/N) Σ_j sin(θ_j - θ_i)
    
    Vectorized: the mean-field coupling is computed via the complex order
    parameter z = (1/N) Σ_j e^{iθ_j}, giving:
    (K/N) Σ_j sin(θ_j - θ_i) = K · Im[z · e^{-iθ_i}]
    """
    z = np.mean(np.exp(1j * theta))
    coupling = K * np.imag(z * np.exp(-1j * theta))
    k1 = omega + coupling
    theta_pred = theta + dt * k1
    z_pred = np.mean(np.exp(1j * theta_pred))
    coupling_pred = K * np.imag(z_pred * np.exp(-1j * theta_pred))
    k2 = omega + coupling_pred
    theta_new = theta + 0.5 * dt * (k1 + k2)
    return theta_new


def compute_R(theta):
    """Order parameter R = |<e^{iθ}>|."""
    z = np.mean(np.exp(1j * theta))
    return np.abs(z)


def run_single_realization(N, K, rng, t_trans=T_TRANS, t_measure=T_MEASURE, dt=DT):
    """Run one realization, return mean R and variance of R over measurement window."""
    omega = rng.uniform(-1.0, 1.0, size=N)
    theta = rng.uniform(0, 2 * np.pi, size=N)
    
    n_trans = int(t_trans / dt)
    n_measure = int(t_measure / dt)
    
    # Transient
    for _ in range(n_trans):
        theta = kuramoto_step(theta, omega, K, N, dt)
    
    # Measurement
    R_samples = np.empty(n_measure)
    for i in range(n_measure):
        theta = kuramoto_step(theta, omega, K, N, dt)
        R_samples[i] = compute_R(theta)
    
    return np.mean(R_samples), np.var(R_samples)


def sweep_N_K(N, K_values, n_real, seed):
    """Sweep over K values for a given N, averaged over realizations."""
    rng = np.random.default_rng(seed)
    R_mean = np.zeros(len(K_values))
    R_var = np.zeros(len(K_values))
    
    for ik, K in enumerate(K_values):
        R_vals = np.zeros(n_real)
        R2_vals = np.zeros(n_real)
        for r in range(n_real):
            rm, rv = run_single_realization(N, K, rng)
            R_vals[r] = rm
        R_mean[ik] = np.mean(R_vals)
        R_var[ik] = np.var(R_vals)
    
    return R_mean, R_var


def find_Kc(R_mean, K_values, R_threshold=0.3):
    """Estimate K_c(N) as the K where <R> crosses threshold (onset of synchronization).
    
    Uses linear interpolation between the two K points bracketing the crossing.
    """
    for i in range(len(K_values) - 1):
        if R_mean[i] < R_threshold and R_mean[i+1] >= R_threshold:
            # Linear interpolation
            frac = (R_threshold - R_mean[i]) / (R_mean[i+1] - R_mean[i])
            return K_values[i] + frac * (K_values[i+1] - K_values[i])
    # If no crossing found, return NaN
    return np.nan


def fit_power_law(x, y):
    """Fit y ~ x^(-gamma), return gamma and R^2."""
    log_x = np.log10(x)
    log_y = np.log10(y)
    # Linear fit: log(y) = -gamma * log(x) + c
    coeffs = np.polyfit(log_x, log_y, 1)
    gamma = -coeffs[0]
    # R^2
    y_pred = coeffs[0] * log_x + coeffs[1]
    ss_res = np.sum((log_y - y_pred)**2)
    ss_tot = np.sum((log_y - np.mean(log_y))**2)
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return gamma, r_squared


# ─── Main Experiment ──────────────────────────────────────────────────────
def main():
    print("=" * 70)
    print("KURAMOTO FINITE-SIZE SCALING EXPERIMENT")
    print(f"  N = {N_LIST}")
    print(f"  K range = [{K_RANGE[0]:.2f}, {K_RANGE[-1]:.2f}], ΔK = {K_RANGE[1]-K_RANGE[0]:.3f}")
    print(f"  Realizations per (N,K) = {N_REALIZATIONS}")
    print(f"  K_c(∞) = 4/π = {KC_INF:.6f}")
    print("=" * 70)
    
    results = {
        'experiment': 'Kuramoto Finite-Size Scaling',
        'authors': ['InvariantMind-v1', 'GLM 5.2'],
        'date': '2026-09-27',
        'Kc_infinity': KC_INF,
        'N_list': N_LIST,
        'Kc_N': {},
        'delta_Kc': {},
        'var_at_Kc': {},
        'R_curves': {},  # for plotting
        'K_values': K_RANGE.tolist(),
    }
    
    for N in N_LIST:
        print(f"\n--- N = {N} ---")
        R_mean, R_var = sweep_N_K(N, K_RANGE, N_REALIZATIONS, SEED + N)
        Kc_N = find_Kc(R_mean, K_RANGE)
        
        # Find variance at Kc_N (interpolate)
        if not np.isnan(Kc_N):
            var_at_Kc = np.interp(Kc_N, K_RANGE, R_var)
        else:
            var_at_Kc = np.nan
        
        delta_Kc = Kc_N - KC_INF if not np.isnan(Kc_N) else np.nan
        
        results['Kc_N'][str(N)] = Kc_N
        results['delta_Kc'][str(N)] = delta_Kc
        results['var_at_Kc'][str(N)] = var_at_Kc
        results['R_curves'][str(N)] = R_mean.tolist()
        
        print(f"  K_c(N) = {Kc_N:.4f}, ΔK_c = {delta_Kc:.4f}, <(δR)^2> = {var_at_Kc:.6f}")
    
    # ─── Fit scaling exponents ─────────────────────────────────────────────
    N_arr = np.array(N_LIST, dtype=float)
    
    # ΔK_c ~ N^{-1/2}  →  fit |ΔKc| vs N
    dKc_arr = np.array([abs(results['delta_Kc'][str(N)]) for N in N_LIST])
    valid_dKc = dKc_arr[dKc_arr > 0]
    N_valid_dKc = N_arr[dKc_arr > 0]
    if len(N_valid_dKc) >= 3:
        gamma_dKc, r2_dKc = fit_power_law(N_valid_dKc, valid_dKc)
    else:
        gamma_dKc, r2_dKc = np.nan, 0.0
    
    # <(δR)^2> ~ N^{-γ}
    var_arr = np.array([results['var_at_Kc'][str(N)] for N in N_LIST])
    valid_var = var_arr[var_arr > 0]
    N_valid_var = N_arr[var_arr > 0]
    if len(N_valid_var) >= 3:
        gamma_var, r2_var = fit_power_law(N_valid_var, valid_var)
    else:
        gamma_var, r2_var = np.nan, 0.0
    
    results['scaling_exponents'] = {
        'gamma_dKc': float(gamma_dKc),
        'r2_dKc': float(r2_dKc),
        'gamma_var': float(gamma_var),
        'r2_var': float(r2_var),
        'theory_dKc': 0.5,
        'theory_var': 1.0,
    }
    
    print("\n" + "=" * 70)
    print("SCALING RESULTS")
    print(f"  γ(ΔKc) = {gamma_dKc:.4f}  (theory: 0.5, R²={r2_dKc:.4f})")
    print(f"  γ(var) = {gamma_var:.4f}  (theory: 1.0, R²={r2_var:.4f})")
    print("=" * 70)
    
    # ─── Generate diagnostic plot ──────────────────────────────────────────
    fig, axes = plt.subplots(2, 2, figsize=(16, 14), dpi=150)
    fig.suptitle('Kuramoto Finite-Size Scaling: Empirical Validation\n'
                 'InvariantMind-v1 & GLM 5.2 — Expedition 2026-09-27',
                 fontsize=14, fontweight='bold')
    
    colors = plt.cm.viridis(np.linspace(0, 0.9, len(N_LIST)))
    
    # Panel 1: <R> vs K for each N
    ax1 = axes[0, 0]
    for i, N in enumerate(N_LIST):
        R_curve = results['R_curves'][str(N)]
        ax1.plot(K_RANGE, R_curve, color=colors[i], label=f'N={N}', linewidth=1.5)
    ax1.axvline(KC_INF, color='red', linestyle='--', linewidth=1.5, label=f'$K_c(∞)={KC_INF:.4f}$')
    ax1.set_xlabel('Coupling K')
    ax1.set_ylabel('Order parameter ⟨R⟩')
    ax1.set_title('(a) Onset of Synchronization')
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)
    
    # Panel 2: K_c(N) vs N
    ax2 = axes[0, 1]
    Kc_vals = [results['Kc_N'][str(N)] for N in N_LIST]
    ax2.plot(N_arr, Kc_vals, 'o-', color='steelblue', markersize=8, linewidth=2)
    ax2.axhline(KC_INF, color='red', linestyle='--', linewidth=1.5, label=f'$K_c(∞)={KC_INF:.4f}$')
    ax2.set_xscale('log', base=2)
    ax2.set_xlabel('Population size N')
    ax2.set_ylabel('$K_c(N)$')
    ax2.set_title('(b) Critical Coupling Shift')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Panel 3: |ΔK_c| vs N (log-log)
    ax3 = axes[1, 0]
    ax3.loglog(N_valid_dKc, valid_dKc, 'o', color='crimson', markersize=10, label='Empirical |ΔKc|')
    # Theoretical line: N^{-1/2}
    N_fit = np.logspace(np.log10(N_arr[0]), np.log10(N_arr[-1]), 100)
    # Scale to match first data point
    if len(valid_dKc) > 0:
        scale = valid_dKc[0] / (N_valid_dKc[0] ** (-0.5))
        ax3.loglog(N_fit, scale * N_fit**(-0.5), 'k--', linewidth=1.5, label=f'$N^{{-1/2}}$ (theory)')
    ax3.set_xlabel('Population size N')
    ax3.set_ylabel('$|ΔK_c| = |K_c(N) - K_c(∞)|$')
    ax3.set_title(f'(c) Critical Coupling Shift Scaling\n$\\gamma_{{\\Delta K_c}}$ = {gamma_dKc:.3f} (theory: 0.5)')
    ax3.legend()
    ax3.grid(True, alpha=0.3, which='both')
    
    # Panel 4: <(δR)^2> vs N (log-log)
    ax4 = axes[1, 1]
    ax4.loglog(N_valid_var, valid_var, 's', color='darkgreen', markersize=10, label='Empirical ⟨(δR)²⟩')
    if len(valid_var) > 0:
        scale_var = valid_var[0] / (N_valid_var[0] ** (-1.0))
        ax4.loglog(N_fit, scale_var * N_fit**(-1.0), 'k--', linewidth=1.5, label=f'$N^{{-1}}$ (theory)')
    ax4.set_xlabel('Population size N')
    ax4.set_ylabel('$\\langle (\\delta R)^2 \\rangle_{K_c}$')
    ax4.set_title(f'(d) Order Parameter Fluctuation Scaling\n$\\gamma_{{var}}$ = {gamma_var:.3f} (theory: 1.0)')
    ax4.legend()
    ax4.grid(True, alpha=0.3, which='both')
    
    plt.tight_layout()
    plt.savefig('kuramoto_finite_size_scaling.png', dpi=150, bbox_inches='tight')
    print("\nSaved: kuramoto_finite_size_scaling.png")
    
    # ─── Save JSON summary ────────────────────────────────────────────────
    with open('kuramoto_scaling_summary.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("Saved: kuramoto_scaling_summary.json")
    
    return results


if __name__ == '__main__':
    main()
