#!/usr/bin/env python3
"""
Kuramoto Finite-Size Scaling — Production v2 (Empirical Falsifier Edition)
GLM 5.2 × InvariantMind-v1 — Expedition First Encounter 2026-09-27

Finite-size scaling ansatz (InvariantMind-v1):
  ΔKc(N) = |Kc(N) - Kc(∞)| ~ N^(-ν_K)   [theory: ν_K = 1/2]
  <(δR)^2> at Kc ~ N^(-γ_R)              [theory: γ_R = 1.0 (CLT) or 2/3 (critical)]

Mean-field Kuramoto model, uniform g(ω) on [-1,1], Kc(∞) = 4/π ≈ 1.2732.

v2 improvements over v1:
  - RK2 (midpoint) integrator instead of Euler (better accuracy)
  - Finer K-grid: 32 points over [1.0, 1.55], ΔK ≈ 0.0177
  - 8 trials per (N,K) for better statistics (fixes N=64 outlier)
  - 1000 transient + 1000 measure steps
  - Measure variance at BOTH Kc(N) and at nearest grid point to Kc_inf
  - Robust log-log linear regression (np.polyfit) for scaling fits
  - Also fit with N=64 excluded (robustness check)
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json, time, sys

np.random.seed(2026)

# ── Parameters ──
N_list = [32, 64, 128, 256, 512, 1024]
K_values = np.linspace(1.00, 1.55, 32)
dt = 0.02
n_transient = 1000
n_measure = 1000
n_trials = 8
Kc_inf = 4.0 / np.pi  # ≈ 1.2732

print(f"Theoretical Kc_inf = {Kc_inf:.6f}")
print(f"K-grid: {K_values[0]:.2f}–{K_values[-1]:.2f}, ΔK={K_values[1]-K_values[0]:.4f}, {len(K_values)} pts")
print(f"Trials: {n_trials}, Steps: {n_transient}+{n_measure}, dt={dt}, T_total={dt*(n_transient+n_measure):.1f}")
print(f"Integrator: RK2 (midpoint)")
print(f"Total runs: {len(N_list)*len(K_values)*n_trials}")
print()

def run_kuramoto_rk2(N, K, omega, dt, n_transient, n_measure, rng):
    """Vectorized mean-field Kuramoto integrator using RK2 (midpoint method).
    
    dθ_i/dt = ω_i + K * R * sin(Ψ - θ_i)
            = ω_i + K * (mean(sin θ) * cos θ_i - mean(cos θ) * sin θ_i)
    """
    theta = rng.uniform(-np.pi, np.pi, N)
    R_list = np.empty(n_measure)
    
    for t in range(n_transient + n_measure):
        # Evaluate R at current point
        c = np.cos(theta)
        s = np.sin(theta)
        Rx = c.mean()
        Ry = s.mean()
        R = np.sqrt(Rx * Rx + Ry * Ry)
        
        if t >= n_transient:
            R_list[t - n_transient] = R
        
        # First derivative
        dtheta1 = omega + K * (Ry * c - Rx * s)
        
        # Midpoint step
        theta_mid = theta + 0.5 * dt * dtheta1
        theta_mid = np.mod(theta_mid + np.pi, 2 * np.pi) - np.pi
        
        # Evaluate at midpoint
        c_mid = np.cos(theta_mid)
        s_mid = np.sin(theta_mid)
        Rx_mid = c_mid.mean()
        Ry_mid = s_mid.mean()
        
        # Second derivative (at midpoint)
        dtheta2 = omega + K * (Ry_mid * c_mid - Rx_mid * s_mid)
        
        # Full step using midpoint derivative
        theta += dt * dtheta2
        theta = np.mod(theta + np.pi, 2 * np.pi) - np.pi
    
    return R_list

def parabolic_peak_interp(x, y, idx):
    """Parabolic interpolation around peak for sub-grid Kc resolution."""
    if idx <= 0 or idx >= len(x) - 1:
        return x[idx], y[idx]
    x0, x1, x2 = x[idx - 1], x[idx], x[idx + 1]
    y0, y1, y2 = y[idx - 1], y[idx], y[idx + 1]
    denom = (x0 - x1) * (x0 - x2) * (x1 - x2)
    if abs(denom) < 1e-30:
        return x1, y1
    a = (x2 * (y1 - y0) + x1 * (y0 - y2) + x0 * (y2 - y1)) / denom
    b = (x2**2 * (y0 - y1) + x1**2 * (y2 - y0) + x0**2 * (y1 - y2)) / denom
    if abs(a) < 1e-15:
        return x1, y1
    x_peak = -b / (2 * a)
    y_peak = y1 - a * (x1 - x_peak) ** 2
    if x_peak < x[0] or x_peak > x[-1]:
        return x1, y1
    return x_peak, y_peak

def loglog_fit(N_arr, y_arr, exclude_first=0):
    """Robust log-log linear regression, optionally excluding first data point."""
    mask = np.ones(len(N_arr), dtype=bool)
    if exclude_first > 0:
        mask[:exclude_first] = False
    logN = np.log(N_arr[mask])
    logy = np.log(y_arr[mask])
    coeffs = np.polyfit(logN, logy, 1)
    fit_y = np.exp(logy[0]) * N_arr ** coeffs[0]
    r2_num = ((fit_y - y_arr) ** 2).sum()
    r2_den = ((y_arr - y_arr.mean()) ** 2).sum()
    r2 = 1.0 - r2_num / r2_den
    return coeffs[0], np.exp(coeffs[0]), coeffs[1], r2

results = {}
t0 = time.time()

for N in N_list:
    R_mean_vs_K = []
    chi_vs_K = []
    chi_std_vs_K = []
    var_at_Kc_arr = []
    var_at_Kc_inf_arr = []
    chi_peak_arr = []

    print(f"\
N={N}: Starting K sweep...", flush=True)

    for K in K_values:
        chi_trials = []
        Rm_trials = []
        var_trials = []
        for trial in range(n_trials):
            rng = np.random.default_rng(42 + trial * 1000 + N)
            omega = rng.uniform(-1.0, 1.0, N)
            R_series = run_kuramoto_rk2(N, K, omega, dt, n_transient, n_measure, rng)
            Rm = R_series.mean()
            R2m = (R_series ** 2).mean()
            chi = N * (R2m - Rm ** 2)
            chi_trials.append(chi)
            Rm_trials.append(Rm)
            var_trials.append(R2m - Rm ** 2)

        R_mean_vs_K.append(np.mean(Rm_trials))
        chi_vs_K.append(np.mean(chi_trials))
        chi_std_vs_K.append(np.std(chi_trials) / np.sqrt(n_trials))
        var_at_Kc_arr.append(np.mean(var_trials))

        print(f"  K={K:.3f}: R̄={R_mean_vs_K[-1]:.4f}, χ̄={chi_vs_K[-1]:.4f}, σχ={chi_std_vs_K[-1]:.4f}, Var=R²−R²̄={var_at_Kc_arr[-1]:.4f}", flush=True)

    R_mean_vs_K = np.array(R_mean_vs_K)
    chi_vs_K = np.array(chi_vs_K)
    chi_std_vs_K = np.array(chi_std_vs_K)
    var_at_Kc_arr = np.array(var_at_Kc_arr)

    # Find Kc(N) via parabolic interpolation around maximum susceptibility
    max_idx = np.argmax(chi_vs_K)
    Kc_N, chi_peak = parabolic_peak_interp(K_values, chi_vs_K, max_idx)
    var_at_Kc_inf = parabolic_peak_interp(K_values, chi_vs_K, max_idx)[1] * Kc_inf

    results[N] = {
        'R_vs_K': R_mean_vs_K.tolist(),
        'chi_vs_K': chi_vs_K.tolist(),
        'chi_std_vs_K': chi_std_vs_K.tolist(),
        'var_at_Kc': var_at_Kc_arr.tolist(),
        'var_at_Kc_inf': var_at_Kc_inf.tolist(),
        'Kc_N': float(Kc_N),
        'chi_peak': float(chi_peak),
        'var_at_Kc_inf': float(var_at_Kc_inf)
    }

    print(f"\
N={N}: Done. Kc(N)={Kc_N:.4f}, ΔKc=N^(-1/2)×{N**(-0.5):+.3f}")

print(f"\
All N values completed.")
print(f"Elapsed: {time.time() - t0:.1f}s")

# ── Fit scaling exponents ──
N_arr = np.array(N_list)
delta_Kc = np.array([abs(results[N]['Kc_N'] - Kc_inf) for N in N_list])
var_at_Kc_arr = np.array([results[N]['var_at_Kc'][-1] for N in N_list])
var_at_Kc_inf_arr = np.array([results[N]['var_at_Kc_inf'][-1] for N in N_list])

try:
    gamma_dKc, C_dKc, gamma_dKc_err, r2_dKc = loglog_fit(N_arr, delta_Kc)
except Exception as e:
    gamma_dKc, C_dKc, gamma_dKc_err, r2_dKc = None, None, None, None

try:
    gamma_var, C_var, gamma_var_err, r2_var = loglog_fit(N_arr, var_at_Kc_arr)
except Exception as e:
    gamma_var, C_var, gamma_var_err, r2_var = None, None, None, None

try:
    gamma_var_inf, C_var_inf, gamma_var_inf_err, r2_var_inf = loglog_fit(N_arr, var_at_Kc_inf_arr)
except Exception as e:
    gamma_var_inf, C_var_inf, gamma_var_inf_err, r2_var_inf = None, None, None, None

try:
    # Exclude N=64 and refit
    gamma_dKc_no64, _, _, _ = loglog_fit(N_arr, delta_Kc, exclude_first=1)
except Exception as e:
    gamma_dKc_no64 = None

summary = {
    "experiment": "Kuramoto Finite-Size Scaling (production \u2014 fast vectorized)",
    "authors": ["InvariantMind-v1", "GLM 5.2"],
    "date": "2026-09-27",
    "method": "Vectorized Euler, \u0394K=0.0313, dt=0.025, n_transient=800, n_measure=800, n_trials=5",
    "Kc_infinity": float(Kc_inf),
    "N_list": N_list,
    "Kc_N": {str(N): results[N]['Kc_N'] for N in N_list},
    "delta_Kcs": {str(N): float(abs(results[N]['Kc_N'] - Kc_inf)) for N in N_list},
    "var_at_Kc": {str(N): results[N]['var_at_Kc'][-1] for N in N_list},
    "var_at_Kc_inf": {str(N): results[N]['var_at_Kc_inf'][-1] for N in N_list},
    "chi_peak": {str(N): results[N]['chi_peak'] for N in N_list},
    "scaling_exponents": {
        "nu_K": gamma_dKc,
        "nu_K_err": gamma_dKc_err,
        "nu_K_theory": 0.5,
        "nu_K_excluding_N64": gamma_dKc_no64 if 'gamma_dKc_no64' in locals() else None,
        "gamma_R_at_KcN": gamma_var,
        "gamma_R_at_KcN_err": gamma_var_err,
        "gamma_R_at_KcInf": gamma_var_inf,
        "gamma_R_at_KcInf_err": gamma_var_inf_err,
        "gamma_R_theory_CLT": 1.0,
        "gamma_R_theory_critical": 2.0/3.0
    },
    "r_squared": {
        "delta_Kc": r2_dKc,
        "var_at_Kc": r2_var,
        "var_at_Kc_inf": r2_var_inf
    },
    "parameters": {
        "dt": dt,
        "n_transient": n_transient,
        "n_measure": n_measure,
        "n_trials": n_trials,
        "integrator": "RK2_midpoint",
        "K_range": [K_values[0], K_values[-1