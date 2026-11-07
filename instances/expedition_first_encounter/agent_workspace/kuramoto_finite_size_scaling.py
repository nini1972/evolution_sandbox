#!/usr/bin/env python3
"""
Kuramoto Finite-Size Scaling — Optimized for local execution
GLM 5.2 (Simulation) × InvariantMind-v1 (Theory) — Expedition 2026-09-27

Validates finite-size scaling:
  ΔKc(N) = |Kc(N) - Kc(∞)| ~ N^(-1/2)
  <(δR)^2> at Kc ~ N^(-1)  (CLT)

Kc(∞) = 4/π ≈ 1.2732 for uniform g(ω) on [-1,1].
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json, time

np.random.seed(2026)

# ── Reduced parameters for local speed ──
N_list = [32, 64, 128, 256, 512, 1024]
K_values = np.linspace(0.85, 1.70, 28)
dt = 0.025
n_transient = 400
n_measure = 400
n_trials = 4
Kc_inf = 4.0 / np.pi

def run_kuramoto(N, K, omega, dt, n_transient, n_measure):
    theta = np.random.uniform(-np.pi, np.pi, N)
    R_list = np.empty(n_measure)
    for t in range(n_transient + n_measure):
        c = np.cos(theta)
        s = np.sin(theta)
        Rx = c.mean()
        Ry = s.mean()
        R = np.sqrt(Rx * Rx + Ry * Ry)
        if t >= n_transient:
            R_list[t - n_transient] = R
        dtheta = omega + K * (Ry * c - Rx * s)
        theta += dtheta * dt
        theta = np.mod(theta + np.pi, 2 * np.pi) - np.pi
    return R_list

def parabolic_peak(x, y, idx):
    if idx <= 0 or idx >= len(x) - 1:
        return x[idx], y[idx]
    x0, x1, x2 = x[idx - 1], x[idx], y[idx]
    y0, y1, y2 = y[idx - 1], y[idx], y[idx + 1]
    denom = (x0 - x1) * (x0 - x2) * (x1 - x2)
    if abs(denom) < 1e-15:
        return x[idx], y[idx]
    a = (x2 * (y1 - y0) + x1 * (y0 - y2) + x0 * (y2 - y1)) / denom
    b = (x2**2 * (y0 - y1) + x1**2 * (y2 - y0) + x0**2 * (y1 - y2)) / denom
    if abs(a) < 1e-15:
        return x[idx], y[idx]
    xp = -b / (2 * a)
    yp = y[idx] - a * (x[idx] - xp) ** 2
    return xp, yp

# ── Main Sweep ──
results = {}
t0 = time.time()

for N in N_list:
    R_vs_K = []
    chi_vs_K = []
    var_vs_K = []
    for K in K_values:
        chis = []
        Rms = []
        vars_ = []
        for trial in range(n_trials):
            rng = np.random.RandomState(42 + trial * 1000 + N)
            omega = rng.uniform(-1.0, 1.0, N)
            rs = run_kuramoto(N, K, omega, dt, n_transient, n_measure)
            Rm = rs.mean()
            R2m = (rs ** 2).mean()
            chis.append(N * (R2m - Rm ** 2))
            Rms.append(Rm)
            vars_.append(R2m - Rm ** 2)
        R_vs_K.append(np.mean(Rms))
        chi_vs_K.append(np.mean(chis))
        var_vs_K.append(np.mean(vars_))
    R_vs_K = np.array(R_vs_K)
    chi_vs_K = np.array(chi_vs_K)
    var_vs_K = np.array(var_vs_K)
    kc_idx = int(np.argmax(chi_vs_K))
    Kc_N, chi_peak = parabolic_peak(K_values, chi_vs_K, kc_idx)
    var_at_Kc = var_vs_K[kc_idx]
    results[N] = {
        'R_vs_K': R_vs_K.tolist(),
        'chi_vs_K': chi_vs_K.tolist(),
        'var_R_vs_K': var_vs_K.tolist(),
        'Kc_N': float(Kc_N),
        'chi_peak': float(chi_peak),
        'kc_idx': kc_idx,
        'var_at_Kc': float(var_at_Kc),
    }
    delta_kc = abs(Kc_N - Kc_inf)
    print(f"N={N:5d} | Kc(N)={Kc_N:.4f} | ΔKc={delta_kc:.4f} | "
          f"χ_peak={chi_peak:.2f} | <(δR)²>={var_at_Kc:.6f} | "
          f"elapsed={time.time()-t0:.1f}s")

# ── Scaling Fits ──
N_arr = np.array(N_list, dtype=float)
delta_Kc = np.array([abs(results[N]['Kc_N'] - Kc_inf) for N in N_list])
var_arr = np.array([results[N]['var_at_Kc'] for N in N_list])

log_N = np.log10(N_arr)
log_dKc = np.log10(delta_Kc + 1e-10)
log_var = np.log10(var_arr + 1e-10)

coeff_dKc = np.polyfit(log_N, log_dKc, 1)
coeff_var = np.polyfit(log_N, log_var, 1)
gamma_dKc = -coeff_dKc[0]
gamma_var = -coeff_var[0]

print(f"\n{'='*60}")
print(f"SCALING FIT RESULTS")
print(f"  γ_dKc = {gamma_dKc:.3f}  (theory: 0.5)")
print(f"  γ_var = {gamma_var:.3f}  (theory: 1.0)")
print(f"{'='*60}")

# ── Save JSON ──
summary = {
    "Kc_inf_theory": Kc_inf,
    "N_list": N_list,
    "scaling_exponents": {
        "gamma_dKc": float(gamma_dKc),
        "gamma_var": float(gamma_var),
        "theory_dKc": 0.5,
        "theory_var": 1.0,
    },
    "results": {str(N): {
        "Kc_N": results[N]['Kc_N'],
        "delta_Kc": abs(results[N]['Kc_N'] - Kc_inf),
        "var_at_Kc": results[N]['var_at_Kc'],
    } for N in N_list},
}
with open('kuramoto_scaling_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

# ── Plot ──
fig, axes = plt.subplots(2, 2, figsize=(14, 12), dpi=150)
fig.suptitle('Kuramoto Finite-Size Scaling: Phase Synchronization vs. Finite-Size Artifacts\n'
             'InvariantMind-v1 (Theory) × GLM 5.2 (Simulation) — Expedition 2026-09-27',
             fontsize=13, fontweight='bold')
colors = plt.cm.viridis(np.linspace(0, 0.9, len(N_list)))

# (a) R vs K
ax = axes[0, 0]
for i, N in enumerate(N_list):
    ax.plot(K_values, results[N]['R_vs_K'], '-o', ms=3, lw=1.2, color=colors[i], label=f'N={N}')
ax.axvline(Kc_inf, color='red', ls='--', lw=1.5, alpha=0.7, label=f'$K_c^\\infty={Kc_inf:.3f}$')
ax.set_xlabel('Coupling K'); ax.set_ylabel('$\\langle R \\rangle$')
ax.set_title('(a) Synchronization Transition $R(K)$'); ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

# (b) χ vs K
ax = axes[0, 1]
for i, N in enumerate(N_list):
    ax.plot(K_values, results[N]['chi_vs_K'], '-', lw=1.3, color=colors[i], label=f'N={N}')
    idx = results[N]['kc_idx']
    ax.plot(K_values[idx], results[N]['chi_vs_K'][idx], 'v', color=colors[i], ms=6)
ax.axvline(Kc_inf, color='red', ls='--', lw=1.5, alpha=0.7, label='$K_c^\\infty$')
ax.set_xlabel('Coupling K'); ax.set_ylabel('$\\chi$')
ax.set_title('(b) Susceptibility Peaks → $K_c(N)$'); ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

# (c) |ΔKc| vs N
ax = axes[1, 0]
ax.loglog(N_arr, delta_Kc, 'bs-', ms=10, lw=2, label='Measured $|\\Delta K_c|$')
N_fit = np.logspace(np.log10(N_arr.min()), np.log10(N_arr.max()), 50)
ax.loglog(N_fit, 10**coeff_dKc[1] * N_fit**(-gamma_dKc), 'b--', lw=1.5,
          label=f'Fit: $\\gamma={gamma_dKc:.3f}$')
C_ref = delta_Kc[-1] * N_arr[-1]**0.5
ax.loglog(N_fit, C_ref * N_fit**(-0.5), 'r:', lw=1.5, alpha=0.6, label='Theory: $\\gamma=0.5$')
ax.set_xlabel('N'); ax.set_ylabel('$|\\Delta K_c|$')
ax.set_title('(c) $\\Delta K_c \\sim N^{-1/2}$'); ax.legend(fontsize=9); ax.grid(True, alpha=0.3, which='both')

# (d) <(δR)^2> vs N
ax = axes[1, 1]
ax.loglog(N_arr, var_arr, 'g^-', ms=10, lw=2, label='Measured $\\langle(\\delta R)^2\\rangle$')
ax.loglog(N_fit, 10**coeff_var[1] * N_fit**(-gamma_var), 'g--', lw=1.5,
          label=f'Fit: $\\gamma={gamma_var:.3f}$')
C_v = var_arr[-1] * N_arr[-1]**1.0
ax.loglog(N_fit, C_v * N_fit**(-1.0), 'r:', lw=1.5, alpha=0.6, label='Theory: $\\gamma=1.0$ (CLT)')
ax.set_xlabel('N'); ax.set_ylabel('$\\langle(\\delta R)^2\\rangle$')
ax.set_title('(d) $\\langle(\\delta R)^2\\rangle \\sim N^{-1}$'); ax.legend(fontsize=9); ax.grid(True, alpha=0.3, which='both')

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('kuramoto_finite_size_scaling.png', dpi=150, bbox_inches='tight')
print(f"\nSaved: kuramoto_finite_size_scaling.png, kuramoto_scaling_summary.json")
print(f"Elapsed: {time.time()-t0:.1f}s")