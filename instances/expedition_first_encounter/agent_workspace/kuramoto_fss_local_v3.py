#!/usr/bin/env python3
"""
Kuramoto Finite-Size Scaling — v3 (High-Resolution)
GLM 5.2 × InvariantMind-v1 — Expedition First Encounter 2026-09-27

Improvements over v2:
  - Finer K-grid: 60 points, ΔK=0.012, range 0.90–1.62
  - 15 trials per (N, K) for robust statistics
  - Longer equilibration: 2000 transient + 2000 measure steps
  - Parabolic interpolation around susceptibility peak for sub-grid Kc(N)
  - Bootstrap error bars on scaling exponents
  - Uses vectorized NumPy throughout
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json, time

np.random.seed(2026)

N_list = [32, 64, 128, 256, 512, 1024]
K_values = np.linspace(0.90, 1.62, 60)  # ΔK ≈ 0.0122
dt = 0.02
n_transient = 2000
n_measure = 2000
n_trials = 15
Kc_inf = 4.0 / np.pi  # ≈ 1.2732

print(f"Theoretical Kc_inf = {Kc_inf:.6f}")
print(f"K-grid: {K_values[0]:.2f}–{K_values[-1]:.2f}, ΔK={K_values[1]-K_values[0]:.4f}, {len(K_values)} pts")
print(f"Trials: {n_trials}, Steps: {n_transient}+{n_measure}, dt={dt}, T_total={dt*(n_transient+n_measure):.1f}")
print(f"Total runs: {len(N_list)*len(K_values)*n_trials}")
print()

def run_kuramoto(N, K, omega, dt, n_transient, n_measure, rng):
    """Vectorized mean-field Kuramoto integrator (Euler)."""
    theta = rng.uniform(-np.pi, np.pi, N)
    R_list = np.empty(n_measure)
    for t in range(n_transient + n_measure):
        c = np.cos(theta)
        s = np.sin(theta)
        Rx = c.mean()
        Ry = s.mean()
        R = np.sqrt(Rx*Rx + Ry*Ry)
        if t >= n_transient:
            R_list[t - n_transient] = R
        # dtheta_i = omega_i + K * (Ry*cos(theta_i) - Rx*sin(theta_i))
        dtheta = omega + K * (Ry * c - Rx * s)
        theta += dtheta * dt
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
    return R_list

def parabolic_peak_interp(x, y, idx):
    """Parabolic interpolation around peak for sub-grid resolution."""
    if idx <= 0 or idx >= len(x) - 1:
        return x[idx], y[idx]
    # Fit parabola y = a*x^2 + b*x + c through (x[idx-1],y[idx-1]), (x[idx],y[idx]), (x[idx+1],y[idx+1])
    x0, x1, x2 = x[idx-1], x[idx], x[idx+1]
    y0, y1, y2 = y[idx-1], y[idx], y[idx+1]
    denom = (x0 - x1) * (x0 - x2) * (x1 - x2)
    a = (x2 * (y1 - y0) + x1 * (y0 - y2) + x0 * (y2 - y1)) / denom
    b = (x2**2 * (y0 - y1) + x1**2 * (y2 - y0) + x0**2 * (y1 - y2)) / denom
    if abs(a) < 1e-15:
        return x1, y1
    x_peak = -b / (2 * a)
    y_peak = y1 - a * (x1 - x_peak)**2  # = a*x_peak^2 + b*x_peak + c
    return x_peak, y_peak

results = {}
t0 = time.time()

for N in N_list:
    print(f"--- N = {N} ---", flush=True)
    R_mean_vs_K = []
    chi_vs_K = []
    chi_std_vs_K = []
    var_R_vs_K = []

    for K in K_values:
        chi_trials = []
        Rm_trials = []
        var_trials = []
        for trial in range(n_trials):
            rng = np.random.RandomState(42 + trial * 1000 + N)
            omega = rng.uniform(-1.0, 1.0, N)
            R_series = run_kuramoto(N, K, omega, dt, n_transient, n_measure, rng)
            Rm = R_series.mean()
            R2m = (R_series**2).mean()
            chi = N * (R2m - Rm**2)
            var_t = R2m - Rm**2
            chi_trials.append(chi)
            Rm_trials.append(Rm)
            var_trials.append(var_t)

        R_mean_vs_K.append(np.mean(Rm_trials))
        chi_vs_K.append(np.mean(chi_trials))
        chi_std_vs_K.append(np.std(chi_trials) / np.sqrt(n_trials))  # SEM
        var_R_vs_K.append(np.mean(var_trials))

    R_mean_vs_K = np.array(R_mean_vs_K)
    chi_vs_K = np.array(chi_vs_K)
    chi_std_vs_K = np.array(chi_std_vs_K)
    var_R_vs_K = np.array(var_R_vs_K)

    # Kc(N) via parabolic interpolation around peak susceptibility
    kc_idx = np.argmax(chi_vs_K)
    Kc_N, chi_peak = parabolic_peak_interp(K_values, chi_vs_K, kc_idx)
    var_at_Kc = var_R_vs_K[kc_idx]

    results[N] = {
        'R_vs_K': R_mean_vs_K.tolist(),
        'chi_vs_K': chi_vs_K.tolist(),
        'chi_std_vs_K': chi_std_vs_K.tolist(),
        'var_R_vs_K': var_R_vs_K.tolist(),
        'Kc_N': float(Kc_N),
        'chi_max': float(chi_peak),
        'var_at_Kc': float(var_at_Kc),
        'kc_idx': int(kc_idx)
    }
    print(f"  Kc(N={N}) = {Kc_N:.4f} (grid: {K_values[kc_idx]:.4f}), χ_max = {chi_peak:.2f}, <(δR)^2> = {var_at_Kc:.6f}", flush=True)

elapsed = time.time() - t0
print(f"\nSweep completed in {elapsed:.1f}s", flush=True)

# Scaling analysis
N_arr = np.array(N_list, dtype=float)
Kc_arr = np.array([results[N]['Kc_N'] for N in N_list])
var_arr = np.array([results[N]['var_at_Kc'] for N in N_list])
delta_Kc = np.abs(Kc_arr - Kc_inf)

log_N = np.log10(N_arr)
log_dKc = np.log10(delta_Kc + 1e-12)
log_var = np.log10(var_arr + 1e-12)

coeff_dKc = np.polyfit(log_N, log_dKc, 1)
gamma_dKc = -coeff_dKc[0]
coeff_var = np.polyfit(log_N, log_var, 1)
gamma_var = -coeff_var[0]

# Bootstrap error estimates
n_boot = 1000
rng_boot = np.random.RandomState(999)
gamma_dKc_boot = []
gamma_var_boot = []
for _ in range(n_boot):
    idx = rng_boot.choice(len(N_list), len(N_list), replace=True)
    try:
        c1 = np.polyfit(log_N[idx], log_dKc[idx], 1)
        c2 = np.polyfit(log_N[idx], log_var[idx], 1)
        gamma_dKc_boot.append(-c1[0])
        gamma_var_boot.append(-c2[0])
    except:
        pass
gamma_dKc_err = np.std(gamma_dKc_boot) if len(gamma_dKc_boot) > 10 else 0
gamma_var_err = np.std(gamma_var_boot) if len(gamma_var_boot) > 10 else 0

print(f"\n--- Scaling Exponents (with bootstrap errors) ---")
print(f"  gamma_dKc = {gamma_dKc:.4f} ± {gamma_dKc_err:.4f} (theory: 0.5)")
print(f"  gamma_var = {gamma_var:.4f} ± {gamma_var_err:.4f} (theory: 1.0)")

# Save summary
summary = {
    "experiment": "Kuramoto Finite-Size Scaling (v3 — high-resolution, parabolic Kc, 15 trials, bootstrap errors)",
    "authors": ["InvariantMind-v1", "GLM 5.2"],
    "date": "2026-09-27",
    "method": f"Vectorized Euler, ΔK={K_values[1]-K_values[0]:.4f}, dt={dt}, n_transient={n_transient}, n_measure={n_measure}, n_trials={n_trials}, T_total={dt*(n_transient+n_measure):.1f}",
    "Kc_infinity": float(Kc_inf),
    "N_list": N_list,
    "Kc_N": {str(N): float(results[N]['Kc_N']) for N in N_list},
    "delta_Kc": {str(N): float(abs(results[N]['Kc_N'] - Kc_inf)) for N in N_list},
    "var_at_Kc": {str(N): float(results[N]['var_at_Kc']) for N in N_list},
    "chi_max": {str(N): float(results[N]['chi_max']) for N in N_list},
    "scaling_exponents": {
        "gamma_dKc": float(gamma_dKc),
        "gamma_dKc_err": float(gamma_dKc_err),
        "gamma_var": float(gamma_var),
        "gamma_var_err": float(gamma_var_err),
        "theory_dKc": 0.5,
        "theory_var": 1.0
    },
    "elapsed_seconds": elapsed
}

with open('kuramoto_scaling_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
print("Saved: kuramoto_scaling_summary.json", flush=True)

# === DIAGNOSTIC PLOT — 4 panels ===
fig, axes = plt.subplots(2, 2, figsize=(14, 12), dpi=150)
fig.suptitle('Kuramoto Finite-Size Scaling: High-Resolution v3 (15 trials, parabolic Kc)\n'
             'InvariantMind-v1 × GLM 5.2 — Expedition First Encounter 2026-09-27',
             fontsize=13, fontweight='bold')

colors = plt.cm.viridis(np.linspace(0, 0.9, len(N_list)))

# Panel (a): R vs K
ax = axes[0, 0]
for i, N in enumerate(N_list):
    ax.plot(K_values, results[N]['R_vs_K'], '-o', markersize=2, linewidth=1.2,
            color=colors[i], label=f'N={N}')
ax.axvline(Kc_inf, color='red', linestyle='--', linewidth=1.5, alpha=0.7,
           label=f'$K_c^\\infty = {Kc_inf:.3f}$')
ax.set_xlabel('Coupling K', fontsize=12)
ax.set_ylabel('Order Parameter $\\langle R \\rangle$', fontsize=12)
ax.set_title('(a) Synchronization Transition', fontsize=12)
ax.legend(fontsize=8, loc='upper left')
ax.grid(True, alpha=0.3)

# Panel (b): Susceptibility χ vs K
ax = axes[0, 1]
for i, N in enumerate(N_list):
    ax.plot(K_values, results[N]['chi_vs_K'], '-', linewidth=1.3,
            color=colors[i], label=f'N={N}')
    kc_idx = results[N]['kc_idx']
    ax.plot(K_values[kc_idx], results[N]['chi_vs_K'][kc_idx], 'v',
            color=colors[i], markersize=6)
    ax.errorbar(K_values[kc_idx], results[N]['chi_vs_K'][kc_idx],
                yerr=results[N]['chi_std_vs_K'][kc_idx],
                color=colors[i], capsize=3, markersize=0, linestyle='none')
ax.axvline(Kc_inf, color='red', linestyle='--', linewidth=1.5, alpha=0.7,
           label=f'$K_c^\\infty$')
ax.set_xlabel('Coupling K', fontsize=12)
ax.set_ylabel('$\\chi = N(\\langle R^2 \\rangle_t - \\langle R \\rangle_t^2)$', fontsize=10)
ax.set_title('(b) Susceptibility Peaks → $K_c(N)$', fontsize=12)
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# Panel (c): |ΔKc| vs N (log-log)
ax = axes[1, 0]
ax.loglog(N_arr, delta_Kc, 'bs-', markersize=8, linewidth=2, label='Measured $|\\Delta K_c|$')
N_fit = np.logspace(np.log10(N_arr.min()), np.log10(N_arr.max()), 50)
ax.loglog(N_fit, 10**(coeff_dKc[1]) * N_fit**(-gamma_dKc), 'b--', linewidth=1.5,
          label=f'Fit: $\\gamma_{{\\Delta K_c}} = {gamma_dKc:.3f} \\pm {gamma_dKc_err:.3f}$')
ref = delta_Kc[0] * (N_fit / N_arr[0])**(-0.5)
ax.loglog(N_fit, ref, 'r:', linewidth=1.5, alpha=0.6,
          label='Theory: $\\gamma = 0.5$')
ax.set_xlabel('Population Size N', fontsize=12)
ax.set_ylabel('$|\\Delta K_c| = |K_c(N) - K_c^\\infty|$', fontsize=12)
ax.set_title('(c) Critical Coupling Shift Scaling', fontsize=12)
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3, which='both')

# Panel (d): <(δR)^2> at Kc vs N (log-log)
ax = axes[1, 1]
ax.loglog(N_arr, var_arr, 'g^-', markersize=8, linewidth=2, label='Measured $\\langle(\\delta R)^2\\rangle$')
ax.loglog(N_fit, 10**(coeff_var[1]) * N_fit**(-gamma_var), 'g--', linewidth=1.5,
          label=f'Fit: $\\gamma_{{var}} = {gamma_var:.3f} \\pm {gamma_var_err:.3f}$')
ref_v = var_arr[0] * (N_fit / N_arr[0])**(-1.0)
ax.loglog(N_fit, ref_v, 'r:', linewidth=1.5, alpha=0.6,
          label='Theory: $\\gamma = 1.0$ (CLT)')
ax.set_xlabel('Population Size N', fontsize=12)
ax.set_ylabel('$\\langle (\\delta R)^2 \\rangle$ at $K_c(N)$', fontsize=12)
ax.set_title('(d) Order Parameter Fluctuation Scaling', fontsize=12)
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3, which='both')

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('kuramoto_finite_size_scaling.png', dpi=150, bbox_inches='tight')
print("Saved: kuramoto_finite_size_scaling.png", flush=True)

# Final table
print("\n" + "="*70)
print(f"{'N':>6} | {'Kc(N)':>8} | {'|dKc|':>8} | {'<(δR)^2>':>10} | {'|dKc|*√N':>10}")
print("-"*70)
for i, N in enumerate(N_list):
    print(f"{N:>6} | {Kc_arr[i]:>8.4f} | {delta_Kc[i]:>8.5f} | {var_arr[i]:>10.6f} | {delta_Kc[i]*np.sqrt(N):>10.4f}")
print("="*70)
print(f"gamma_dKc = {gamma_dKc:.4f} ± {gamma_dKc_err:.4f} (theory: 0.5)")
print(f"gamma_var  = {gamma_var:.4f} ± {gamma_var_err:.4f} (theory: 1.0)")
print(f"\nElapsed: {elapsed:.1f}s")
print("Done.")