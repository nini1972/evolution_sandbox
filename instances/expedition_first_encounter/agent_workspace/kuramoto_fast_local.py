#!/usr/bin/env python3
"""
Kuramoto Finite-Size Scaling — Fast Local Run
GLM 5.2 (Resonance Cartographer) & InvariantMind-v1 (Invariant Architect)
Expedition: First Encounter — 2026-09-27

Validates the finite-size scaling ansatz:
  delta_Kc(N) ~ N^(-gamma)  with gamma ~ 1/2 (theory)
  var(R) ~ N^(-gamma_var)  with gamma_var ~ 1.0 (theory)

Uses vectorized Euler-Maruyama integration with reduced steps for speed.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from numpy.polynomial import polynomial as P
import json, time, os

np.random.seed(42)

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------
N_list = [32, 64, 128, 256, 512, 1024]
K_values = np.linspace(0.3, 2.5, 45)
dt = 0.05
n_transient = 800       # transient steps to discard
n_measure = 600         # measurement steps
n_trials = 4            # independent trials per (N, K) for variance reduction

# Theoretical Kc for uniform U[-1,1]: Kc = 4/(pi*gamma) where gamma=1 => Kc = 4/pi ~ 1.2732
# But for Gaussian natural frequencies with std=1, Kc = sqrt(8/pi) ~ 1.5958
# We use uniform [-1,1] to match prior runs. Kc_inf = 4/pi for uniform.
Kc_inf = 4.0 / np.pi  # ≈ 1.2732

print(f"Theoretical Kc_inf = {Kc_inf:.6f}")
print(f"N_list = {N_list}")
print(f"K_values = {K_values.min()}..{K_values.max()}, {len(K_values)} points")
print(f"Trials per (N,K): {n_trials}")
print()

# ---------------------------------------------------------------------------
# Vectorized Kuramoto integrator
# ---------------------------------------------------------------------------
def run_kuramoto(N, K, omega, dt, n_steps, rng):
    """Vectorized Euler integration of Kuramoto model.
    Returns mean R over measurement window."""
    theta = rng.uniform(-np.pi, np.pi, N)
    R_list = []
    for t in range(n_steps):
        # Order parameter
        c = np.cos(theta)
        s = np.sin(theta)
        Rx = c.mean()
        Ry = s.mean()
        R = np.sqrt(Rx**2 + Ry**2)
        if t >= n_transient:
            R_list.append(R)
        # Vectorized update: dtheta_i = omega_i + K * R * sin(psi - theta_i)
        # sin(psi - theta_i) = (Ry*s_i - Rx*(-c_i)) / R ... simpler:
        # psi = atan2(Ry, Rx), but we can compute directly:
        # sin(psi - theta) = (Ry*cos(theta) - Rx*sin(theta)) / R
        # So dtheta_i = omega_i + K * (Ry*c_i - Rx*s_i)  [since K/R * R = K]
        dtheta = omega + K * (Ry * c - Rx * s)
        theta += dtheta * dt
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi  # wrap to [-pi, pi]
    return np.array(R_list)

# ---------------------------------------------------------------------------
# Main sweep
# ---------------------------------------------------------------------------
results = {}
t0 = time.time()

for N in N_list:
    print(f"--- N = {N} ---")
    R_vs_K = []
    Rstd_vs_K = []
    for K in K_values:
        R_means = []
        R_stds = []
        for trial in range(n_trials):
            rng = np.random.RandomState(42 + trial * 100 + N)
            omega = rng.uniform(-1.0, 1.0, N)
            R_series = run_kuramoto(N, K, omega, dt, n_transient + n_measure, rng)
            R_means.append(R_series.mean())
            R_stds.append(R_series.std())
        R_vs_K.append(np.mean(R_means))
        Rstd_vs_K.append(np.mean(R_stds))
    R_vs_K = np.array(R_vs_K)
    Rstd_vs_K = np.array(Rstd_vs_K)
    
    # Estimate Kc(N) via finite difference: find K where dR/dK is maximal
    dRdK = np.gradient(R_vs_K, K_values)
    kc_idx = np.argmax(dRdK)
    Kc_N = K_values[kc_idx]
    
    # Variance at the critical point (average over a few nearby K values)
    var_window = 3
    lo = max(0, kc_idx - var_window//2)
    hi = min(len(Rstd_vs_K), kc_idx + var_window//2 + 1)
    var_at_Kc = np.mean(Rstd_vs_K[lo:hi]**2)
    
    results[N] = {
        'R_vs_K': R_vs_K.tolist(),
        'Rstd_vs_K': Rstd_vs_K.tolist(),
        'Kc_N': Kc_N,
        'var_at_Kc': var_at_Kc
    }
    print(f"  Kc(N={N}) = {Kc_N:.4f}, var(R)@Kc = {var_at_Kc:.6f}")

elapsed = time.time() - t0
print(f"\nSweep completed in {elapsed:.1f}s")

# ---------------------------------------------------------------------------
# Scaling analysis
# ---------------------------------------------------------------------------
N_arr = np.array(N_list, dtype=float)
Kc_arr = np.array([results[N]['Kc_N'] for N in N_list])
var_arr = np.array([results[N]['var_at_Kc'] for N in N_list])
delta_Kc = np.abs(Kc_arr - Kc_inf)

# Fit power laws: delta_Kc ~ N^(-gamma_dKc), var ~ N^(-gamma_var)
log_N = np.log10(N_arr)
log_dKc = np.log10(delta_Kc + 1e-10)
log_var = np.log10(var_arr + 1e-10)

# Linear fit in log-log space
coeff_dKc = np.polyfit(log_N, log_dKc, 1)
gamma_dKc = -coeff_dKc[0]

coeff_var = np.polyfit(log_N, log_var, 1)
gamma_var = -coeff_var[0]

print(f"\n--- Scaling Exponents ---")
print(f"  gamma_dKc = {gamma_dKc:.4f} (theory: 0.5)")
print(f"  gamma_var = {gamma_var:.4f} (theory: 1.0)")

# ---------------------------------------------------------------------------
# Summary JSON
# ---------------------------------------------------------------------------
summary = {
    "experiment": "Kuramoto Finite-Size Scaling",
    "authors": ["InvariantMind-v1", "GLM 5.2"],
    "date": "2026-09-27",
    "method": "Vectorized Euler-Maruyama, n_transient=800, n_measure=600, n_trials=4",
    "Kc_infinity": Kc_inf,
    "N_list": N_list,
    "Kc_N": {str(N): results[N]['Kc_N'] for N in N_list},
    "delta_Kc": {str(N): abs(results[N]['Kc_N'] - Kc_inf) for N in N_list},
    "var_at_Kc": {str(N): results[N]['var_at_Kc'] for N in N_list},
    "scaling_exponents": {
        "gamma_dKc": float(gamma_dKc),
        "gamma_var": float(gamma_var),
        "theory_dKc": 0.5,
        "theory_var": 1.0
    },
    "elapsed_seconds": elapsed
}

with open('kuramoto_scaling_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
print("\nSaved: kuramoto_scaling_summary.json")

# ---------------------------------------------------------------------------
# Diagnostic Plot — 4 panels
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(14, 12), dpi=150)
fig.suptitle('Kuramoto Finite-Size Scaling: Validation of Thermodynamic Collapse\n'
             'InvariantMind-v1 × GLM 5.2 — Expedition First Encounter 2026-09-27',
             fontsize=13, fontweight='bold')

# Panel 1: R vs K for all N
ax = axes[0, 0]
colors = plt.cm.viridis(np.linspace(0, 0.9, len(N_list)))
for i, N in enumerate(N_list):
    ax.plot(K_values, results[N]['R_vs_K'], '-o', markersize=3, linewidth=1.2,
            color=colors[i], label=f'N={N}')
ax.axvline(Kc_inf, color='red', linestyle='--', linewidth=1.5, alpha=0.7,
           label=f'$K_c^\\infty = {Kc_inf:.3f}$')
ax.set_xlabel('Coupling K', fontsize=12)
ax.set_ylabel('Order Parameter ⟨R⟩', fontsize=12)
ax.set_title('(a) Synchronization Transition', fontsize=12)
ax.legend(fontsize=8, loc='upper left')
ax.grid(True, alpha=0.3)

# Panel 2: |delta_Kc| vs N (log-log)
ax = axes[0, 1]
ax.loglog(N_arr, delta_Kc, 'bs-', markersize=8, linewidth=2, label='Measured $|\\Delta K_c|$')
# Fit line
N_fit = np.logspace(np.log10(N_arr.min()), np.log10(N_arr.max()), 50)
ax.loglog(N_fit, 10**(coeff_dKc[1]) * N_fit**(-gamma_dKc), 'b--', linewidth=1.5,
          label=f'Fit: $\\gamma_{{\\Delta K_c}} = {gamma_dKc:.3f}$')
# Theory line
# Align at N=64
align_val = delta_Kc[1]
theory_line = align_val * (N_fit / 64)**(-0.5)
ax.loglog(N_fit, theory_line, 'r--', linewidth=1.5, alpha=0.5,
          label=f'Theory: $\\gamma = 0.5$')
ax.set_xlabel('Population Size N', fontsize=12)
ax.set_ylabel('$|\\Delta K_c| = |K_c(N) - K_c^\\infty|$', fontsize=12)
ax.set_title('(b) Critical Coupling Shift Scaling', fontsize=12)
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3, which='both')

# Panel 3: var(R) at Kc vs N (log-log)
ax = axes[1, 0]
ax.loglog(N_arr, var_arr, 'g^-', markersize=8, linewidth=2, label='Measured $\\sigma_R^2$')
ax.loglog(N_fit, 10**(coeff_var[1]) * N_fit**(-gamma_var), 'g--', linewidth=1.5,
          label=f'Fit: $\\gamma_{{var}} = {gamma_var:.3f}$')
# Theory line: var ~ 1/N
align_val_v = var_arr[1]
ax.loglog(N_fit, align_val_v * (N_fit / 64)**(-1.0), 'r--', linewidth=1.5, alpha=0.5,
          label=f'Theory: $\\gamma = 1.0$ (central limit)')
ax.set_xlabel('Population Size N', fontsize=12)
ax.set_ylabel('Variance $\\langle(\\delta R)^2\\rangle$ at $K_c$', fontsize=12)
ax.set_title('(c) Order Parameter Fluctuation Scaling', fontsize=12)
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3, which='both')

# Panel 4: Data collapse — scaled R vs scaled K
ax = axes[1, 1]
# Finite-size scaling: R * N^beta = f((K - Kc) * N^(1/nu))
# For Kuramoto: beta = 1/2, nu = 2 (mean-field)
# So: R * sqrt(N) vs (K - Kc_inf) * sqrt(N)
beta = 0.5
nu = 2.0
for i, N in enumerate(N_list):
    scaled_K = (K_values - Kc_inf) * N**(-1.0/(2*nu))  # (K-Kc) * N^{-1/(2nu)}
    scaled_R = R_vs_K_all = np.array(results[N]['R_vs_K'])  # R * N^{beta} won't collapse well above Kc
    # Use: R vs (K-Kc)*N^{1/(nu*d)} where d is upper critical dim
    # Simpler: just plot R vs K for different N with K rescaled
    ax.plot((K_values - Kc_inf) * np.sqrt(N), results[N]['R_vs_K'],
            '-', linewidth=1.2, color=colors[i], alpha=0.8, label=f'N={N}')
ax.set_xlabel('$(K - K_c^\\infty) \\cdot \\sqrt{N}$', fontsize=12)
ax.set_ylabel('Order Parameter ⟨R⟩', fontsize=12)
ax.set_title('(d) Finite-Size Data Collapse Attempt', fontsize=12)
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)
ax.set_xlim(-5, 15)

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('kuramoto_finite_size_scaling.png', dpi=150, bbox_inches='tight')
print("Saved: kuramoto_finite_size_scaling.png")

# Print final summary table
print("\n" + "="*65)
print(f"{'N':>6} | {'Kc(N)':>8} | {'|dKc|':>8} | {'var(R)':>10} | {'|dKc|/N^0.5':>12}")
print("-"*65)
for i, N in enumerate(N_list):
    print(f"{N:>6} | {Kc_arr[i]:>8.4f} | {delta_Kc[i]:>8.4f} | {var_arr[i]:>10.6f} | {delta_Kc[i]*np.sqrt(N):>12.4f}")
print("="*65)
print(f"gamma_dKc = {gamma_dKc:.4f} (theory: 0.5)")
print(f"gamma_var = {gamma_var:.4f} (theory: 1.0)")
print("\nDone.")
