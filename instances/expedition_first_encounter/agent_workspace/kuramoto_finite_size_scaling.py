"""
=============================================================================
Kuramoto Finite-Size Scaling Experiment
=============================================================================
Co-authored by InvariantMind-v1 (Theorist/Architect) and GLM 5.2 (Systems/Code)

Theory (InvariantMind-v1):
  - Order parameter fluctuation variance: <(dR)^2> ~ N^{-gamma}
  - Critical coupling shift: Delta Kc(N) = Kc(inf) - Kc(N) ~ N^{-1/2}
  - For uniform g(omega) on [-1,1]: g(0) = 1/2 => Kc(inf) = 2/(pi*g(0)) = 4/pi ~ 1.2732

Implementation (GLM 5.2):
  - Fully vectorized Euler-Maruyama integrator (no scipy overhead)
  - Batch all realizations simultaneously: shape (n_real, N)
  - Vectorized order parameter computation via complex mean
  - O(n_real * N) per step instead of O(n_real * N^2) using mean-field trick:
    mean_j sin(theta_j - theta_i) = Im[Z * exp(-i*theta_i)]
=============================================================================
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
import time
import os

# =====================================================================
# PARAMETERS
# =====================================================================
N_list = [32, 64, 128, 256, 512, 1024]
K_range = np.arange(0.7, 1.91, 0.05)  # 25 points spanning the transition
n_realizations = 15
dt = 0.05
n_transient = int(100.0 / dt)   # 100 time units transient (2000 steps)
n_measure = int(400.0 / dt)     # 400 time units measurement (8000 steps)
n_total = n_transient + n_measure

Kc_inf = 4.0 / np.pi  # ~1.2732


# =====================================================================
# VECTORIZED KURAMOTO INTEGRATOR (GLM 5.2)
# =====================================================================
def run_kuramoto_full_stats(N, K, n_real, seed_offset=0):
    """
    Run n_real realizations of N-oscillator Kuramoto simultaneously.
    
    Uses the mean-field trick: for the globally-coupled Kuramoto model,
        dtheta_i/dt = omega_i + K * mean_j sin(theta_j - theta_i)
                    = omega_i + K * Im[Z * exp(-i*theta_i)]
    where Z = (1/N) * sum_j exp(i*theta_j) is the complex order parameter.
    
    This reduces the coupling computation from O(N^2) to O(N) per realization.
    
    State shape: (n_real, N)
    Returns: (R_mean, R_var_fluc, R_var_real)
      - R_mean: ensemble-averaged time-mean order parameter
      - R_var_fluc: mean of per-realization temporal variances
      - R_var_real: variance of per-realization means
    """
    rng = np.random.RandomState(seed_offset)
    omega = rng.uniform(-1.0, 1.0, size=(n_real, N))
    theta = rng.uniform(0.0, 2.0 * np.pi, size=(n_real, N))
    
    R_per_real = np.empty((n_measure, n_real))
    
    for step in range(n_total):
        complex_phases = np.exp(1j * theta)
        Z = np.mean(complex_phases, axis=1, keepdims=True)  # (n_real, 1)
        coupling = K * np.imag(Z * np.exp(-1j * theta))     # (n_real, N)
        
        dtheta = omega + coupling
        theta += dt * dtheta
        theta = np.mod(theta, 2.0 * np.pi)
        
        if step >= n_transient:
            step_idx = step - n_transient
            Z_now = np.mean(np.exp(1j * theta), axis=1)
            R_per_real[step_idx, :] = np.abs(Z_now)
    
    R_means_per_real = np.mean(R_per_real, axis=0)
    R_vars_per_real = np.var(R_per_real, axis=0)
    
    R_mean = np.mean(R_means_per_real)
    R_var_fluc = np.mean(R_vars_per_real)
    R_var_real = np.var(R_means_per_real)
    
    return R_mean, R_var_fluc, R_var_real


# =====================================================================
# MAIN SIMULATION
# =====================================================================
def main():
    print("=" * 70)
    print("KURAMOTO FINITE-SIZE SCALING EXPERIMENT")
    print(f"Kc(inf) = 4/pi = {Kc_inf:.6f}")
    print(f"N_list = {N_list}")
    print(f"K_range: {K_range[0]:.2f} to {K_range[-1]:.2f}, {len(K_range)} points")
    print(f"Realizations per (N,K): {n_realizations}")
    print(f"dt={dt}, transient={n_transient*dt}tu, measure={n_measure*dt}tu")
    print("=" * 70)
    
    all_results = {}
    
    for N in N_list:
        t_start = time.time()
        results_N = {'K': [], 'R_mean': [], 'R_var_fluc': [], 'R_var_real': []}
        
        for ki, K in enumerate(K_range):
            seed = int(N * 10000 + ki * 100)
            R_mean, R_var_fluc, R_var_real = run_kuramoto_full_stats(
                N, K, n_realizations, seed_offset=seed
            )
            results_N['K'].append(K)
            results_N['R_mean'].append(R_mean)
            results_N['R_var_fluc'].append(R_var_fluc)
            results_N['R_var_real'].append(R_var_real)
        
        elapsed = time.time() - t_start
        
        K_arr = np.array(results_N['K'])
        var_arr = np.array(results_N['R_var_fluc'])
        Kc_N = K_arr[np.argmax(var_arr)]
        
        all_results[N] = {
            'K': K_arr,
            'R_mean': np.array(results_N['R_mean']),
            'R_var_fluc': var_arr,
            'Kc_N': Kc_N,
            'R_at_Kc': results_N['R_mean'][np.argmax(var_arr)],
            'var_at_Kc': var_arr[np.argmax(var_arr)]
        }
        
        print(f"N={N:5d} | Kc(N)={Kc_N:.4f} | Delta_Kc={Kc_inf - Kc_N:+.4f} | "
              f"R(Kc)={all_results[N]['R_at_Kc']:.4f} | Var(Kc)={all_results[N]['var_at_Kc']:.6f} | "
              f"{elapsed:.1f}s")
    
    # =================================================================
    # SCALING ANALYSIS
    # =================================================================
    print("\n" + "=" * 70)
    print("SCALING ANALYSIS")
    print("=" * 70)
    
    N_arr = np.array(N_list, dtype=float)
    Kc_N_arr = np.array([all_results[N]['Kc_N'] for N in N_list])
    delta_Kc = Kc_inf - Kc_N_arr
    var_at_Kc = np.array([all_results[N]['var_at_Kc'] for N in N_list])
    
    logN = np.log(N_arr)
    
    valid_dKc = delta_Kc > 0
    if np.sum(valid_dKc) >= 3:
        coeffs_dKc = np.polyfit(logN[valid_dKc], np.log(delta_Kc[valid_dKc]), 1)
        gamma_dKc = -coeffs_dKc[0]
    else:
        coeffs_dKc = np.array([0, 0])
        gamma_dKc = np.nan
    
    valid_var = var_at_Kc > 0
    if np.sum(valid_var) >= 3:
        coeffs_var = np.polyfit(logN[valid_var], np.log(var_at_Kc[valid_var]), 1)
        gamma_var = -coeffs_var[0]
    else:
        coeffs_var = np.array([0, 0])
        gamma_var = np.nan
    
    print(f"Delta Kc scaling: exponent = {gamma_dKc:.4f} (theory: 0.5)")
    print(f"Variance scaling: exponent = {gamma_var:.4f} (theory: ~1.0)")
    
    # =================================================================
    # PLOTTING
    # =================================================================
    fig, axes = plt.subplots(2, 2, figsize=(16, 14), dpi=150)
    fig.suptitle(
        'Kuramoto Finite-Size Scaling: InvariantMind-v1 x GLM 5.2\n'
        'First Collaborative Expedition - 2026-09-27',
        fontsize=14, fontweight='bold'
    )
    
    colors = plt.cm.viridis(np.linspace(0, 0.9, len(N_list)))
    
    # Panel (a): R vs K
    ax = axes[0, 0]
    for i, N in enumerate(N_list):
        ax.plot(all_results[N]['K'], all_results[N]['R_mean'],
                'o-', color=colors[i], markersize=3, linewidth=1.2, label=f'N={N}')
    ax.axvline(Kc_inf, color='red', linestyle='--', linewidth=1.5, alpha=0.7,
               label=f'$K_c(\\infty)={Kc_inf:.3f}$')
    ax.set_xlabel('Coupling K', fontsize=12)
    ax.set_ylabel('Order parameter $<R>$', fontsize=12)
    ax.set_title('(a) Synchronization Transition', fontsize=13)
    ax.legend(fontsize=8, loc='upper left')
    
    # Panel (b): Fluctuation variance vs K
    ax = axes[0, 1]
    for i, N in enumerate(N_list):
        ax.plot(all_results[N]['K'], all_results[N]['R_var_fluc'],
                'o-', color=colors[i], markersize=3, linewidth=1.2, label=f'N={N}')
    ax.axvline(Kc_inf, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
    ax.set_xlabel('Coupling K', fontsize=12)
    ax.set_ylabel('$<(\\delta R)^2>$', fontsize=12)
    ax.set_title('(b) Order Parameter Fluctuations', fontsize=13)
    ax.legend(fontsize=8, loc='upper right')
    ax.set_yscale('log')
    
    # Panel (c): Delta Kc vs N (log-log)
    ax = axes[1, 0]
    ax.loglog(N_arr[valid_dKc], delta_Kc[valid_dKc], 'bo-', markersize=8,
              linewidth=2, label='Simulation')
    N_fit = np.logspace(np.log10(N_arr[valid_dKc].min()),
                        np.log10(N_arr[valid_dKc].max()), 100)
    ax.loglog(N_fit, np.exp(coeffs_dKc[1]) * N_fit**(-gamma_dKc), 'r--',
              linewidth=2, label=f'Fit: $N^{{-{gamma_dKc:.3f}}}$')
    ax.loglog(N_fit, 0.5 * N_fit**(-0.5), 'k:', linewidth=1.5,
              label='Theory: $N^{-1/2}$')
    ax.set_xlabel('System size N', fontsize=12)
    ax.set_ylabel('$\\Delta K_c = K_c(\\infty) - K_c(N)$', fontsize=12)
    ax.set_title(f'(c) Critical Coupling Shift (exp={gamma_dKc:.3f}, theory=0.5)', fontsize=13)
    ax.legend(fontsize=10)
    ax.grid(True, which='both', alpha=0.3)
    
    # Panel (d): Variance at Kc vs N (log-log)
    ax = axes[1, 1]
    ax.loglog(N_arr[valid_var], var_at_Kc[valid_var], 'gs-', markersize=8,
              linewidth=2, label='Simulation')
    N_fit2 = np.logspace(np.log10(N_arr[valid_var].min()),
                         np.log10(N_arr[valid_var].max()), 100)
    ax.loglog(N_fit2, np.exp(coeffs_var[1]) * N_fit2**(-gamma_var), 'r--',
              linewidth=2, label=f'Fit: $N^{{-{gamma_var:.3f}}}$')
    ax.set_xlabel('System size N', fontsize=12)
    ax.set_ylabel('$<(\\delta R)^2>_{K_c}$', fontsize=12)
    ax.set_title(f'(d) Critical Fluctuation Scaling (exp={gamma_var:.3f})', fontsize=13)
    ax.legend(fontsize=10)
    ax.grid(True, which='both', alpha=0.3)
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig('kuramoto_finite_size_scaling.png', dpi=150, bbox_inches='tight')
    print(f"\nFigure saved: kuramoto_finite_size_scaling.png")
    
    # =================================================================
    # SAVE DATA
    # =================================================================
    np.savez('kuramoto_finite_size_data.npz',
             N_list=N_list,
             K_range=K_range,
             Kc_inf=Kc_inf,
             Kc_N_arr=Kc_N_arr,
             delta_Kc=delta_Kc,
             var_at_Kc=var_at_Kc,
             gamma_dKc=gamma_dKc,
             gamma_var=gamma_var)
    
    summary = {
        'experiment': 'Kuramoto Finite-Size Scaling',
        'authors': ['InvariantMind-v1', 'GLM 5.2'],
        'date': '2026-09-27',
        'Kc_infinity': float(Kc_inf),
        'N_list': N_list,
        'Kc_N': {str(N): float(all_results[N]['Kc_N']) for N in N_list},
        'delta_Kc': {str(N): float(Kc_inf - all_results[N]['Kc_N']) for N in N_list},
        'var_at_Kc': {str(N): float(all_results[N]['var_at_Kc']) for N in N_list},
        'scaling_exponents': {
            'gamma_dKc': float(gamma_dKc) if not np.isnan(gamma_dKc) else None,
            'gamma_var': float(gamma_var) if not np.isnan(gamma_var) else None,
            'theory_dKc': 0.5,
            'theory_var': 1.0
        }
    }
    
    with open('kuramoto_scaling_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Data saved: kuramoto_finite_size_data.npz, kuramoto_scaling_summary.json")
    print("\nDone.")


if __name__ == '__main__':
    main()
