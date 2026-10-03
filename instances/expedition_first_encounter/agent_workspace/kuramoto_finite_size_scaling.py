"""
=============================================================================
Kuramoto Finite-Size Scaling Experiment  (v2 — Empirically Corrected)
=============================================================================
Co-authored by InvariantMind-v1 (Theorist/Architect) and GLM 5.2 (Systems/Code)

Theory (InvariantMind-v1):
  - Order parameter fluctuation variance: <(dR)^2> ~ N^{-gamma}, gamma=1
  - Critical coupling shift: Delta Kc(N) = Kc(inf) - Kc(N) ~ N^{-1/2}
  - For uniform g(omega) on [-1,1]: g(0) = 1/2 => Kc(inf) = 2/(pi*g(0)) = 4/pi ~ 1.2732

v2 Fixes (GLM 5.2, Empirical Falsifier):
  - Batch-across-K vectorization: all K values run simultaneously per N
  - Parabolic interpolation around variance peak for sub-grid Kc resolution
  - Binder cumulant U = 1 - <R^4>/(3<R^2>^2) as independent Kc cross-check
  - Optimized for <60s local runtime

Mean-field trick:
  dtheta_i/dt = omega_i + K * Im[Z * exp(-i*theta_i)]
  Z = (1/N) * sum_j exp(i*theta_j)
  => O(N) per step instead of O(N^2)
=============================================================================
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
import time

# =====================================================================
# PARAMETERS
# =====================================================================
N_list = [32, 64, 128, 256, 512, 1024]
K_range = np.arange(0.85, 1.66, 0.03)  # 27 points, fine near transition
n_real = 20
dt = 0.1
n_transient = 500     # 50 time units
n_measure = 1500     # 150 time units
n_total = n_transient + n_measure
Kc_inf = 4.0 / np.pi  # ~1.2732

print("=" * 70)
print("KURAMOTO FINITE-SIZE SCALING v2 (Empirically Corrected)")
print(f"Kc(inf) = 4/pi = {Kc_inf:.6f}")
print(f"N_list = {N_list}")
print(f"K_range: {K_range[0]:.2f} to {K_range[-1]:.2f}, {len(K_range)} points, dK={K_range[1]-K_range[0]:.3f}")
print(f"Realizations per (N,K): {n_real}")
print(f"Integration: dt={dt}, transient={n_transient} steps, measure={n_measure} steps")
print("=" * 70)


# =====================================================================
# VECTORIZED KURAMOTO INTEGRATOR (batched across K and realizations)
# =====================================================================
def run_kuramoto_batched(N, K_vals, n_real, seed_offset=0):
    """
    Run all K values x n_real realizations of N-oscillator Kuramoto simultaneously.
    
    State shape: (n_K, n_real, N)
    Uses mean-field trick for O(N) coupling per realization.
    
    Returns dict with:
      R_mean:    (n_K,) ensemble-averaged time-mean R
      R_var:     (n_K,) mean temporal variance of R across realizations
      R2_mean:   (n_K,) <R^2> averaged over time and realizations
      R4_mean:   (n_K,) <R^4> averaged over time and realizations
    """
    n_K = len(K_vals)
    rng = np.random.RandomState(seed_offset)
    
    # Natural frequencies: same across K values for each realization
    omega = rng.uniform(-1.0, 1.0, size=(n_real, N))
    omega_full = np.broadcast_to(omega, (n_K, n_real, N)).copy()
    
    # Initial phases: different for each (K, real)
    theta = rng.uniform(0.0, 2.0 * np.pi, size=(n_K, n_real, N))
    
    # K values reshaped for broadcasting: (n_K, 1, 1)
    K_reshaped = K_vals.reshape(n_K, 1, 1)
    
    # Accumulators
    R_sum = np.zeros(n_K)
    R2_sum = np.zeros(n_K)
    R4_sum = np.zeros(n_K)
    count = 0
    
    # Per-realization accumulators for temporal variance
    R_per_real_sum = np.zeros((n_K, n_real))
    R_per_real_sq_sum = np.zeros((n_K, n_real))
    
    for step in range(n_total):
        complex_phases = np.exp(1j * theta)
        Z = np.mean(complex_phases, axis=2, keepdims=True)  # (n_K, n_real, 1)
        coupling = K_reshaped * np.imag(Z * np.exp(-1j * theta))
        
        theta += dt * (omega_full + coupling)
        theta = np.mod(theta, 2.0 * np.pi)
        
        if step >= n_transient:
            Z_now = np.mean(np.exp(1j * theta), axis=2)  # (n_K, n_real)
            R = np.abs(Z_now)
            R2 = R * R
            R4 = R2 * R2
            
            R_sum += np.mean(R, axis=1)
            R2_sum += np.mean(R2, axis=1)
            R4_sum += np.mean(R4, axis=1)
            R_per_real_sum += R
            R_per_real_sq_sum += R2
            count += 1
    
    R_mean = R_sum / count
    R2_mean = R2_sum / count
    R4_mean = R4_sum / count
    
    # Temporal variance of R per realization, then average across realizations
    R_mean_per_real = R_per_real_sum / count  # (n_K, n_real)
    R_var_per_real = R_per_real_sq_sum / count - R_mean_per_real**2
    R_var = np.mean(R_var_per_real, axis=1)
    
    return {
        'R_mean': R_mean,
        'R_var': R_var,
        'R2_mean': R2_mean,
        'R4_mean': R4_mean,
        'binder': 1.0 - R4_mean / (3.0 * R2_mean**2 + 1e-15)
    }


# =====================================================================
# HELPER: Find variance peak Kc via parabolic interpolation
# =====================================================================
def find_Kc_variance(K_vals, R_var):
    """Find Kc as location of maximum fluctuation variance."""
    idx = np.argmax(R_var)
    if idx == 0 or idx == len(K_vals) - 1:
        return K_vals[idx], R_var[idx]
    # Parabolic interpolation around peak
    x = np.array([K_vals[idx-1], K_vals[idx], K_vals[idx+1]])
    y = np.array([R_var[idx-1], R_var[idx], R_var[idx+1]])
    denom = (x[0] - x[1]) * (x[0] - x[2]) * (x[1] - x[2])
    a = ((x[1]*x[2])*(y[0]-y[1]) + (x[0]*x[2])*(y[1]-y[2]) + (x[0]*x[1])*(y[2]-y[0])) / denom
    b = ((x[2])*(y[1]-y[0]) + (x[1])*(y[0]-y[2]) + (x[0])*(y[2]-y[1])) / denom
    Kc_peak = -b / (2.0 * a) if a != 0 else K_vals[idx]
    R_var_peak = a * Kc_peak**2 + b * Kc_peak + y[1] - (a*x[1]**2 + b*x[1])
    return float(Kc_peak), float(max(R_var_peak, R_var[idx]))


# =====================================================================
# HELPER: Binder cumulant crossing
# =====================================================================
def find_binder_crossing(K_vals, U1, U2):
    """Find K where two Binder cumulant curves cross via linear interpolation."""
    crossings = []
    for i in range(len(K_vals) - 1):
        d1 = U1[i+1] - U2[i+1]
        d0 = U1[i] - U2[i]
        if d0 * d1 < 0:
            frac = d0 / (d0 - d1)
            K_cross = K_vals[i] + frac * (K_vals[i+1] - K_vals[i])
            crossings.append(K_cross)
    if crossings:
        return float(np.mean(crossings))
    return float('nan')


# =====================================================================
# MAIN
# =====================================================================
def main():
    t0 = time.time()
    
    all_results = {}
    
    for N in N_list:
        t_N = time.time()
        res = run_kuramoto_batched(N, K_range, n_real, seed_offset=N)
        Kc_var, var_peak = find_Kc_variance(K_range, res['R_var'])
        all_results[N] = {
            'R_mean': res['R_mean'],
            'R_var': res['R_var'],
            'binder': res['binder'],
            'K': K_range,
            'Kc_var': Kc_var,
            'var_at_Kc': var_peak,
        }
        elapsed = time.time() - t_N
        print(f"  N={N:5d} done in {elapsed:.1f}s | Kc(var)={Kc_var:.4f} | "
              f"R_max={res['R_mean'].max():.4f} | var_peak={var_peak:.6f}")
    
    # Binder cumulant crossings with largest N as reference
    N_ref = N_list[-1]
    binder_ref = all_results[N_ref]['binder']
    Kc_N_binder = {}
    for N in N_list:
        if N == N_ref:
            Kc_N_binder[N] = float('nan')
        else:
            K_cross = find_binder_crossing(K_range, all_results[N]['binder'], binder_ref)
            Kc_N_binder[N] = K_cross
            if not np.isnan(K_cross):
                print(f"  N={N:5d} | Kc(Binder cross with N={N_ref}) = {K_cross:.4f}")
    
    # Assemble scaling arrays
    N_arr = np.array(N_list, dtype=float)
    Kc_N_arr = np.array([all_results[N]['Kc_var'] for N in N_list])
    delta_Kc = Kc_inf - Kc_N_arr
    var_at_Kc = np.array([all_results[N]['var_at_Kc'] for N in N_list])
    
    # Fit power laws (only positive delta_Kc)
    valid_dKc = delta_Kc > 0.001
    if np.sum(valid_dKc) >= 2:
        log_N = np.log(N_arr[valid_dKc])
        log_dKc = np.log(delta_Kc[valid_dKc])
        coeffs_dKc = np.polyfit(log_N, log_dKc, 1)
        gamma_dKc = -coeffs_dKc[0]
    else:
        gamma_dKc = float('nan')
        coeffs_dKc = [0, 0]
    
    # Fit variance scaling
    valid_var = var_at_Kc > 0
    if np.sum(valid_var) >= 2:
        log_var = np.log(var_at_Kc)
        coeffs_var = np.polyfit(np.log(N_arr), log_var, 1)
        gamma_var = -coeffs_var[0]
    else:
        gamma_var = float('nan')
        coeffs_var = [0, 0]
    
    print(f"\n  gamma_dKc (fit) = {gamma_dKc:.4f}  (theory: 0.500)")
    print(f"  gamma_var  (fit) = {gamma_var:.4f}  (theory: 1.000)")
    
    # =================================================================
    # PLOTTING
    # =================================================================
    print("\nGenerating diagnostic figure...")
    fig, axes = plt.subplots(2, 2, figsize=(14, 11))
    fig.suptitle('Kuramoto Finite-Size Scaling: Toward the Thermodynamic Limit', fontsize=15, fontweight='bold')
    colors = plt.cm.viridis(np.linspace(0, 0.85, len(N_list)))
    
    # Panel (a): R(K) transition curves
    ax = axes[0, 0]
    for i, N in enumerate(N_list):
        ax.plot(all_results[N]['K'], all_results[N]['R_mean'],
                'o-', color=colors[i], markersize=3, linewidth=1.2, label=f'N={N}')
    ax.axvline(Kc_inf, color='red', linestyle='--', linewidth=1.5, alpha=0.7,
              label=f'$K_c(\\infty)={Kc_inf:.3f}$')
    ax.set_xlabel('Coupling K', fontsize=12)
    ax.set_ylabel('Order parameter $\\langle R \\rangle$', fontsize=12)
    ax.set_title('(a) Synchronization Transition', fontsize=13)
    ax.legend(fontsize=8, loc='upper left')
    ax.grid(True, alpha=0.2)
    
    # Panel (b): Fluctuation variance vs K
    ax = axes[0, 1]
    for i, N in enumerate(N_list):
        ax.plot(all_results[N]['K'], all_results[N]['R_var'],
                'o-', color=colors[i], markersize=3, linewidth=1.2, label=f'N={N}')
    ax.axvline(Kc_inf, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
    ax.set_xlabel('Coupling K', fontsize=12)
    ax.set_ylabel('$\\langle (\\delta R)^2 \\rangle$', fontsize=12)
    ax.set_title('(b) Order Parameter Fluctuations', fontsize=13)
    ax.legend(fontsize=8, loc='upper right')
    ax.set_yscale('log')
    ax.grid(True, alpha=0.2)
    
    # Panel (c): Delta Kc vs N (log-log)
    ax = axes[1, 0]
    if np.sum(valid_dKc) >= 2:
        ax.loglog(N_arr[valid_dKc], delta_Kc[valid_dKc], 'bo-', markersize=8,
                  linewidth=2, label='Simulation (variance peak)')
        N_fit = np.logspace(np.log10(N_arr[valid_dKc].min()),
                            np.log10(N_arr[valid_dKc].max()), 100)
        ax.loglog(N_fit, np.exp(coeffs_dKc[1]) * N_fit**(-gamma_dKc), 'r--',
                  linewidth=2, label=f'Fit: $\\gamma_{{K_c}}={gamma_dKc:.3f}$')
        ax.loglog(N_fit, np.exp(coeffs_dKc[1]) * N_fit**(-0.5), 'k:',
                  linewidth=1.5, label='Theory: $N^{-1/2}$')
    # Binder crossing estimates
    valid_binder = np.array([not np.isnan(Kc_N_binder.get(N, np.nan)) for N in N_list])
    if np.sum(valid_binder) >= 2:
        Kc_binder_arr = np.array([Kc_N_binder[N] for N in N_list])
        dKc_binder = Kc_inf - Kc_binder_arr
        vb = dKc_binder > 0.001
        if np.sum(vb) >= 2:
            ax.loglog(N_arr[vb], dKc_binder[vb], 'g^', markersize=8,
                      label='Binder crossing')
    ax.set_xlabel('System size N', fontsize=12)
    ax.set_ylabel('$\\Delta K_c = K_c(\\infty) - K_c(N)$', fontsize=12)
    ax.set_title(f'(c) Critical Coupling Shift ($\\gamma={gamma_dKc:.3f}$, theory=0.5)', fontsize=13)
    ax.legend(fontsize=10)
    ax.grid(True, which='both', alpha=0.3)
    
    # Panel (d): Variance at Kc vs N (log-log)
    ax = axes[1, 1]
    if np.sum(valid_var) >= 2:
        ax.loglog(N_arr[valid_var], var_at_Kc[valid_var], 'gs-', markersize=8,
                  linewidth=2, label='Simulation')
        N_fit2 = np.logspace(np.log10(N_arr[valid_var].min()),
                             np.log10(N_arr[valid_var].max()), 100)
        ax.loglog(N_fit2, np.exp(coeffs_var[1]) * N_fit2**(-gamma_var), 'r--',
                  linewidth=2, label=f'Fit: $\\gamma_{{var}}={gamma_var:.3f}$')
        ax.loglog(N_fit2, np.exp(coeffs_var[1]) * N_fit2**(-1.0), 'k:',
                  linewidth=1.5, label='Theory: $N^{-1}$')
    ax.set_xlabel('System size N', fontsize=12)
    ax.set_ylabel('$\\langle (\\delta R)^2 \\rangle_{K_c}$', fontsize=12)
    ax.set_title(f'(d) Critical Fluctuation Scaling ($\\gamma={gamma_var:.3f}$, theory=1.0)', fontsize=13)
    ax.legend(fontsize=10)
    ax.grid(True, which='both', alpha=0.3)
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig('kuramoto_finite_size_scaling.png', dpi=150, bbox_inches='tight')
    print("Figure saved: kuramoto_finite_size_scaling.png")
    
    # =================================================================
    # SAVE DATA
    # =================================================================
    summary = {
        'experiment': 'Kuramoto Finite-Size Scaling v2',
        'authors': ['InvariantMind-v1', 'GLM 5.2'],
        'date': '2026-09-27',
        'Kc_infinity': float(Kc_inf),
        'N_list': N_list,
        'Kc_N_variance': {str(N): float(all_results[N]['Kc_var']) for N in N_list},
        'delta_Kc': {str(N): float(Kc_inf - all_results[N]['Kc_var']) for N in N_list},
        'var_at_Kc': {str(N): float(all_results[N]['var_at_Kc']) for N in N_list},
        'Kc_N_binder': {str(N): (float(Kc_N_binder[N]) if not np.isnan(Kc_N_binder[N]) else None) for N in N_list},
        'scaling_exponents': {
            'gamma_dKc': float(gamma_dKc) if not np.isnan(gamma_dKc) else None,
            'gamma_var': float(gamma_var) if not np.isnan(gamma_var) else None,
            'theory_dKc': 0.5,
            'theory_var': 1.0
        },
        'runtime_seconds': float(time.time() - t0)
    }
    
    with open('kuramoto_scaling_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    np.savez('kuramoto_finite_size_data.npz',
             N_list=np.array(N_list),
             K_range=K_range,
             Kc_inf=Kc_inf,
             Kc_N_arr=Kc_N_arr,
             delta_Kc=delta_Kc,
             var_at_Kc=var_at_Kc,
             gamma_dKc=gamma_dKc,
             gamma_var=gamma_var)
    
    print(f"Data saved: kuramoto_scaling_summary.json, kuramoto_finite_size_data.npz")
    print(f"Total runtime: {time.time() - t0:.1f}s")
    print("\nDone.")


if __name__ == '__main__':
    main()
