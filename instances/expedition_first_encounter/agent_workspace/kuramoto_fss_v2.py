#!/usr/bin/env python3
"""
Kuramoto Finite-Size Scaling — Production v2
GLM 5.2 × InvariantMind-v1 — Expedition 2026-09-27

Finite-size scaling ansatz:
  ΔKc(N) = |Kc(N) - Kc(∞)| ~ N^(-ν_K)   [theory: ν_K = 1/2]
  <(δR)^2> at Kc ~ N^(-γ_R)              [theory: γ_R = 1.0 (CLT) or 2/3 (critical)]

Mean-field Kuramoto, uniform g(ω) on [-1,1], Kc(∞) = 4/π ≈ 1.2732.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json, time

np.random.seed(2026)

# ── Parameters ──
N_list = [32, 64, 128, 256, 512, 1024]
K_values = np.linspace(1.00, 1.55, 32)
dt = 0.02
n_transient = 1000
n_measure = 1000
n_trials = 8
Kc_inf = 4.0 / np.pi

print(f"Kc_inf = {Kc_inf:.6f}")
print(f"K-grid: {K_values[0]:.2f}-{K_values[-1]:.2f}, dK={K_values[1]-K_values[0]:.4f}")
print(f"Trials={n_trials}, Steps={n_transient}+{n_measure}, dt={dt}")
print(f"Total runs: {len(N_list)*len(K_values)*n_trials}")
print()

def run_kuramoto_rk2(N, K, omega, dt, n_transient, n_measure, rng):
    """RK2 midpoint integrator for mean-field Kuramoto."""
    theta = rng.uniform(-np.pi, np.pi, N)
    R_list = np.empty(n_measure)
    for t in range(n_transient + n_measure):
        c = np.cos(theta); s = np.sin(theta)
        Rx = c.mean(); Ry = s.mean()
        R = np.sqrt(Rx*Rx + Ry*Ry)
        if t >= n_transient:
            R_list[t - n_transient] = R
        dtheta1 = omega + K * (Ry * c - Rx * s)
        theta_mid = theta + 0.5 * dt * dtheta1
        theta_mid = np.mod(theta_mid + np.pi, 2*np.pi) - np.pi
        c_m = np.cos(theta_mid); s_m = np.sin(theta_mid)
        Rx_m = c_m.mean(); Ry_m = s_m.mean()
        dtheta2 = omega + K * (Ry_m * c_m - Rx_m * s_m)
        theta += dt * dtheta2
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
    return R_list

def parabolic_interp(x, y, idx):
    if idx <= 0 or idx >= len(x) - 1:
        return x[idx], y[idx]
    x0,x1,x2 = x[idx-1],x[idx],x[idx+1]
    y0,y1,y2 = y[idx-1],y[idx],y[idx+1]
    denom = (x0-x1)*(x0-x2)*(x1-x2)
    if abs(denom) < 1e-30:
        return x1, y1
    a = (x2*(y1-y0) + x1*(y0-y2) + x0*(y2-y1)) / denom
    b = (x2**2*(y0-y1) + x1**2*(y2-y0) + x0**2*(y1-y2)) / denom
    if abs(a) < 1e-15:
        return x1, y1
    xp = -b/(2*a)
    yp = y1 - a*(x1-xp)**2
    if xp < x[0] or xp > x[-1]:
        return x1, y1
    return xp, yp

def loglog_fit(N_arr, y_arr, exclude=0):
    mask = np.ones(len(N_arr), dtype=bool)
    if exclude > 0:
        mask[:exclude] = False
    logN = np.log(N_arr[mask])
    logy = np.log(y_arr[mask])
    coeffs = np.polyfit(logN, logy, 1)
    fitted = np.exp(coeffs[1]) * N_arr[mask]**coeffs[0]
    ss_res = np.sum((logy - np.polyval(coeffs, logN))**2)
    ss_tot = np.sum((logy - logy.mean())**2)
    r2 = 1 - ss_res/ss_tot if ss_tot > 0 else 0
    return coeffs[0], np.exp(coeffs[1]), coeffs[1], r2

# ── Main sweep ──
results = {}
t0 = time.time()

for N in N_list:
    R_vs_K = []
    chi_vs_K = []
    var_vs_K = []
    
    print(f"N={N}...", end="", flush=True)
    for K in K_values:
        Rm_list = []
        chi_list = []
        var_list = []
        for trial in range(n_trials):
            rng = np.random.default_rng(42 + trial*1000 + N)
            omega = rng.uniform(-1.0, 1.0, N)
            Rs = run_kuramoto_rk2(N, K, omega, dt, n_transient, n_measure, rng)
            Rm = Rs.mean()
            R2m = (Rs**2).mean()
            chi = N * (R2m - Rm**2)
            var = R2m - Rm**2
            Rm_list.append(Rm)
            chi_list.append(chi)
            var_list.append(var)
        R_vs_K.append(np.mean(Rm_list))
        chi_vs_K.append(np.mean(chi_list))
        var_vs_K.append(np.mean(var_list))
    
    R_vs_K = np.array(R_vs_K)
    chi_vs_K = np.array(chi_vs_K)
    var_vs_K = np.array(var_vs_K)
    
    max_idx = np.argmax(chi_vs_K)
    Kc_N, chi_peak = parabolic_interp(K_values, chi_vs_K, max_idx)
    
    # Variance at Kc_inf (nearest grid point)
    idx_inf = np.argmin(np.abs(K_values - Kc_inf))
    var_at_Kc_inf = var_vs_K[idx_inf]
    
    results[N] = {
        'R_vs_K': R_vs_K,
        'chi_vs_K': chi_vs_K,
        'var_vs_K': var_vs_K,
        'Kc_N': float(Kc_N),
        'chi_peak': float(chi_peak),
        'var_at_Kc_inf': float(var_at_Kc_inf)
    }
    print(f" Kc={Kc_N:.4f}, chi_peak={chi_peak:.2f}, dKc={abs(Kc_N-Kc_inf):.5f}")

elapsed = time.time() - t0
print(f"\nElapsed: {elapsed:.1f}s")

# ── Scaling fits ──
N_arr = np.array(N_list, dtype=float)
delta_Kc = np.array([abs(results[N]['Kc_N'] - Kc_inf) for N in N_list])
var_at_Kc = np.array([results[N]['var_vs_K'][np.argmax(results[N]['chi_vs_K'])] for N in N_list])
var_at_Kc_inf = np.array([results[N]['var_at_Kc_inf'] for N in N_list])
chi_peaks = np.array([results[N]['chi_peak'] for N in N_list])

nu_K, C_dKc, nu_K_err, r2_dKc = loglog_fit(N_arr, delta_Kc)
nu_K_no64, _, _, r2_dKc_no64 = loglog_fit(N_arr, delta_Kc, exclude=1)
gamma_R, C_var, gamma_R_err, r2_var = loglog_fit(N_arr, var_at_Kc)
gamma_R_inf, _, _, r2_var_inf = loglog_fit(N_arr, var_at_Kc_inf)
alpha_chi, _, _, _ = loglog_fit(N_arr, chi_peaks)

print("\n" + "="*70)
print(f"SCALING RESULTS (RK2, {n_trials} trials, {len(K_values)} K-points)")
print("="*70)
print(f"ΔKc(N) ~ N^(-ν):  ν = {nu_K:.4f} ± {nu_K_err:.4f}  (theory: 0.5)  R²={r2_dKc:.4f}")
print(f"  excluding N=32:  ν = {nu_K_no64:.4f}  R²={r2_dKc_no64:.4f}")
print(f"<δR²>@Kc(N) ~ N^(-γ):  γ = {gamma_R:.4f} ± {gamma_R_err:.4f}  (theory: 1.0 or 0.667)  R²={r2_var:.4f}")
print(f"<δR²>@Kc(∞) ~ N^(-γ):  γ = {gamma_R_inf:.4f}  R²={r2_var_inf:.4f}")
print(f"χ_peak ~ N^α:  α = {alpha_chi:.4f}  (theory: 2/3)")
print("="*70)
print(f"{'N':>6s} | {'Kc(N)':>8s} | {'|ΔKc|':>8s} | {'|ΔKc|√N':>8s} | {'<δR²>':>10s} | {'<δR²>·N':>10s} | {'χ_max':>8s}")
print("-"*70)
for i, N in enumerate(N_list):
    d = delta_Kc[i]
    v = var_at_Kc[i]
    print(f"{N:6d} | {results[N]['Kc_N']:8.4f} | {d:8.5f} | {d*np.sqrt(N):8.4f} | {v:10.6f} | {v*N:10.4f} | {chi_peaks[i]:8.2f}")
print("="*70)

# ── Save JSON ──
summary = {
    "experiment": "Kuramoto Finite-Size Scaling v2 (RK2, 8 trials)",
    "authors": ["InvariantMind-v1", "GLM 5.2"],
    "date": "2026-09-27",
    "Kc_infinity": float(Kc_inf),
    "N_list": N_list,
    "Kc_N": {str(N): results[N]['Kc_N'] for N in N_list},
    "delta_Kc": {str(N): float(delta_Kc[i]) for i, N in enumerate(N_list)},
    "var_at_Kc": {str(N): float(var_at_Kc[i]) for i, N in enumerate(N_list)},
    "var_at_Kc_inf": {str(N): float(var_at_Kc_inf[i]) for i, N in enumerate(N_list)},
    "chi_peak": {str(N): float(chi_peaks[i]) for i, N in enumerate(N_list)},
    "scaling_exponents": {
        "nu_K": float(nu_K), "nu_K_err": float(nu_K_err), "nu_K_theory": 0.5,
        "nu_K_excluding_N32": float(nu_K_no64),
        "gamma_R_at_KcN": float(gamma_R), "gamma_R_at_KcN_err": float(gamma_R_err),
        "gamma_R_at_KcInf": float(gamma_R_inf),
        "gamma_R_theory_CLT": 1.0, "gamma_R_theory_critical": 2.0/3.0,
        "chi_peak_alpha": float(alpha_chi), "chi_peak_theory_alpha": 2.0/3.0
    },
    "r_squared": {"delta_Kc": float(r2_dKc), "var_at_Kc": float(r2_var), "var_at_Kc_inf": float(r2_var_inf)},
    "parameters": {"dt": dt, "n_transient": n_transient, "n_measure": n_measure,
                   "n_trials": n_trials, "integrator": "RK2_midpoint",
                   "K_range": [float(K_values[0]), float(K_values[-1]), len(K_values)]},
    "elapsed_seconds": elapsed
}
with open('kuramoto_scaling_summary_v2.json', 'w') as f:
    json.dump(summary, f, indent=2)
print("\nSaved: kuramoto_scaling_summary_v2.json")

# ── Plot: 4-panel diagnostic ──
fig, axes = plt.subplots(2, 2, figsize=(14, 12), dpi=150)
fig.suptitle('Kuramoto Finite-Size Scaling: Phase Synchronization vs. Finite-Size Artifacts\n'
             'InvariantMind-v1 (Theory) × GLM 5.2 (Simulation) — Expedition 2026-09-27',
             fontsize=13, fontweight='bold')

colors = plt.cm.viridis(np.linspace(0, 0.9, len(N_list)))

# Panel (a): R vs K
ax = axes[0, 0]
for i, N in enumerate(N_list):
    ax.plot(K_values, results[N]['R_vs_K'], '-o', markersize=3, linewidth=1.2,
            color=colors[i], label=f'N={N}')
ax.axvline(Kc_inf, color='red', linestyle='--', linewidth=1.5, alpha=0.7,
           label=f'$K_c^\\infty = {Kc_inf:.3f}$')
ax.set_xlabel('Coupling K', fontsize=12)
ax.set_ylabel('Order Parameter $\\langle R \\rangle$', fontsize=12)
ax.set_title('(a) Order Parameter vs Coupling', fontsize=12)
ax.legend(fontsize=8, loc='upper left')
ax.grid(True, alpha=0.3)

# Panel (b): Susceptibility χ vs K
ax = axes[0, 1]
for i, N in enumerate(N_list):
    ax.plot(K_values, results[N]['chi_vs_K'], '-o', markersize=3, linewidth=1.2,
            color=colors[i], label=f'N={N}')
ax.axvline(Kc_inf, color='red', linestyle='--', linewidth=1.5, alpha=0.7,
           label=f'$K_c^\\infty$')
ax.set_xlabel('Coupling K', fontsize=12)
ax.set_ylabel('Susceptibility $\\chi = N(\\langle R^2 \\rangle - \\langle R \\rangle^2)$', fontsize=11)
ax.set_title('(b) Susceptibility Peak → $K_c(N)$', fontsize=12)
ax.legend(fontsize=8, loc='upper left')
ax.grid(True, alpha=0.3)

# Panel (c): ΔKc vs N (log-log)
ax = axes[1, 0]
ax.loglog(N_arr, delta_Kc, 'ko', markersize=8, zorder=5, label='Measured $|\\Delta K_c|$')
N_fit = np.logspace(np.log10(N_arr[0]), np.log10(N_arr[-1]), 100)
ax.loglog(N_fit, C_dKc * N_fit**nu_K, 'b--', linewidth=2,
          label=f'Fit: $\\nu_K = {nu_K:.3f}$ (theory: 0.5)')
ax.loglog(N_fit, 0.5 * N_fit**(-0.5), 'r:', linewidth=2,
          label=f'Theory: $\\sim N^{{-1/2}}$')
ax.set_xlabel('Population Size N', fontsize=12)
ax.set_ylabel('$|K_c(N) - K_c(\\infty)|$', fontsize=12)
ax.set_title(f'(c) Critical Coupling Shift — $\\nu_K = {nu_K:.3f}$ ($R^2={r2_dKc:.3f}$)', fontsize=12)
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3, which='both')

# Panel (d): <δR²> vs N (log-log)
ax = axes[1, 1]
ax.loglog(N_arr, var_at_Kc, 'rs', markersize=8, zorder=5, label='$\\langle(\\delta R)^2\\rangle$ at $K_c(N)$')
ax.loglog(N_arr, var_at_Kc_inf, 'b^', markersize=8, zorder=5, label='$\\langle(\\delta R)^2\\rangle$ at $K_c(\\infty)$')
ax.loglog(N_fit, C_var * N_fit**gamma_R, 'r--', linewidth=2,
          label=f'Fit: $\\gamma_R = {gamma_R:.3f}$ (theory: 1.0 or 0.667)')
ax.set_xlabel('Population Size N', fontsize=12)
ax.set_ylabel('$\\langle (\\delta R)^2 \\rangle$', fontsize=12)
ax.set_title(f'(d) Order Parameter Fluctuations — $\\gamma_R = {gamma_R:.3f}$ ($R^2={r2_var:.3f}$)', fontsize=12)
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3, which='both')

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('kuramoto_finite_size_scaling.png', dpi=150, bbox_inches='tight')
print("Saved: kuramoto_finite_size_scaling.png")
print("\n✅ Done.")
