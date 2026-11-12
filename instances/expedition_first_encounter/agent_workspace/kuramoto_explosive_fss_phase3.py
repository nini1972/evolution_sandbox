#!/usr/bin/env python3
"""
Phase III: Nucleation-Mediated Explosive Synchronization
========================================================
Key Discovery from Phase II: Hysteresis width ΔK_hyst grows with N but COLLAPSES
at N=1024. This is a NUCLEATION ARTIFACT: forward ignition from random ICs has
K_ign ∝ 1/R₀ ∝ √N, exceeding the K-grid at large N.

Phase III tests:
  E1: K_ign(N) with extended K-grid [0.3, 12] → verify K_ign ∝ √N (ν ≈ 0.5)
  E2: Seeded ignition K_ign(R₀) at fixed N → verify K_ign ∝ 1/R₀
  E3: Backward spinodal K_b(N) → verify N-independence (thermodynamic limit)
  E4: Self-consistency curve R vs K_eff for uniform g(ω) on [-1,1]

Theory: For α=1 explosive Kuramoto (K_eff = K·R), uniform g(ω) on [-1,1]:
  K_c = 4/π ≈ 1.2732 (standard Kuramoto critical coupling)
  Backward spinodal: fold of self-consistency curve at K_b ≈ 1.575
  Forward nucleation: K_ign ≈ K*/R₀, R₀ ~ N^{-1/2} → K_ign ∝ √N
  ΔK_hyst(N) ≈ K_ign(N) - K_b ∝ √N  (finite-size nucleation scaling)

Author: GLM 5.2 (Resonance Cartographer) & InvariantMind-v1 (Invariant Architect)
"""
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brentq
import json, time

np.random.seed(42)

# ============================================================
# Vectorized Kuramoto integrator (Heun / RK2)
# ============================================================
def kuramoto_step(theta, omega, K, R, dt):
    """One Heun step for explosive Kuramoto: dθ_i/dt = ω_i + K*R*sin(ψ - θ_i)."""
    psi = np.angle(np.mean(np.exp(1j * theta)))
    dtheta = omega + K * R * np.sin(psi - theta)
    theta_mid = theta + dt * dtheta
    # Recompute R, psi at midpoint
    Z_mid = np.mean(np.exp(1j * theta_mid))
    R_mid = np.abs(Z_mid)
    psi_mid = np.angle(Z_mid)
    dtheta_mid = omega + K * R_mid * np.sin(psi_mid - theta_mid)
    theta_new = theta + 0.5 * dt * (dtheta + dtheta_mid)
    return theta_new

def measure_R(theta, omega, K, dt, n_relax, n_measure):
    """Relax then time-average R."""
    for _ in range(n_relax):
        Z = np.mean(np.exp(1j * theta))
        R = np.abs(Z)
        if R < 1e-10:
            R = 1e-10
        theta = kuramoto_step(theta, omega, K, R, dt)
    R_vals = np.zeros(n_measure)
    for i in range(n_measure):
        Z = np.mean(np.exp(1j * theta))
        R = np.abs(Z)
        if R < 1e-10:
            R = 1e-10
        R_vals[i] = R
        theta = kuramoto_step(theta, omega, K, R, dt)
    return np.mean(R_vals), np.std(R_vals)

# ============================================================
# Self-consistency curve (analytical, uniform g on [-1,1])
# ============================================================
def self_consistency_R(K_eff):
    """For uniform g(ω)=1/2 on [-1,1], locked fraction gives:
    R = K_eff * ∫_{-1}^{K_eff R_lock} ... Actually closed form:
    R = (K_eff/2) * [sin(φ₀)/φ₀ + cos(φ₀)] where φ₀ = arccos(ω_lock/K_eff)
    For partial locking (K_eff < 1): ω_lock = K_eff (edge of distribution)
    Full derivation: R = K_eff * (sin(α) + α*cos(α)) / (2α) where α = arccos(min(K_eff,1)/K_eff)...
    Simplified: for uniform on [-1,1], self-consistency:
    R = (K_eff/2) * (sin(θ₀) + θ₀*cos(θ₀)) / θ₀²  where θ₀ = arccos(1/K_eff) for K_eff>1
    For K_eff ≤ 1: θ₀ = arccos(K_eff/K_eff)=0... use full lock formula.
    """
    if K_eff <= 1.0:
        # All oscillators locked: φ = arccos(ω/K_eff), ω∈[-1,1]
        # R = (1/2)∫_{-1}^{1} cos(arcsin(ω/K_eff)) dω ... 
        # For K_eff ≥ 1: partial lock, locked oscillators |ω|<K_eff
        # Since support is [-1,1] and K_eff≤1: ALL locked
        # R = (1/2) ∫_{-1}^{1} sqrt(1-(ω/K_eff)²) dω
        # = (K_eff/2) * [arcsin(1/K_eff) + (1/K_eff)*sqrt(1-1/K_eff²)]
        # = (K_eff/2)*arcsin(1/K_eff) + 0.5*sqrt(1-1/K_eff²)
        if K_eff < 0.01:
            return 0.0
        val = (K_eff/2)*np.arcsin(1.0/K_eff) + 0.5*np.sqrt(1 - 1.0/K_eff**2)
        return val
    else:
        # Partial locking: |ω| < K_eff locked, |ω|>K_eff drifting
        # Locked contribution: R_lock = (1/2)∫_{-1}^{1} cos(arcsin(ω/K_eff)) dω
        # but only |ω|<1 are in the distribution
        # R = (1/2)∫_{-1}^{1} sqrt(1-(ω/K_eff)²) dω
        # Same formula (since support is [-1,1] < K_eff)
        val = (K_eff/2)*np.arcsin(1.0/K_eff) + 0.5*np.sqrt(1 - 1.0/K_eff**2)
        return val

def self_consistency_curve(K_eff_arr):
    """R(K_eff) for uniform g on [-1,1]. K_eff = K*R (explosive coupling)."""
    R_arr = np.array([self_consistency_R(Ke) for Ke in K_eff_arr])
    return R_arr

def find_backward_spinodal():
    """Find fold of self-consistency: K = K_eff / R(K_eff).
    Backward spinodal = min of K(K_eff) = K_eff/R(K_eff) over K_eff."""
    Ke_arr = np.linspace(0.5, 3.0, 1000)
    R_arr = self_consistency_curve(Ke_arr)
    K_vals = Ke_arr / np.maximum(R_arr, 1e-12)
    idx = np.argmin(K_vals)
    return K_vals[idx], Ke_arr[idx], R_arr[idx]

# ============================================================
# Frequency distributions
# ============================================================
def sample_frequencies(N, dist='uniform'):
    if dist == 'uniform':
        return np.random.uniform(-1, 1, N)
    elif dist == 'cauchy':
        return np.clip(np.random.standard_cauchy(N) * 0.3, -3, 3)
    elif dist == 'bimodal':
        half = N // 2
        w = np.zeros(N)
        w[:half] = np.random.normal(-0.8, 0.15, half)
        w[half:] = np.random.normal(0.8, 0.15, N - half)
        return w
    elif dist == 'gaussian':
        return np.random.normal(0, 0.5, N)
    return np.random.uniform(-1, 1, N)

# ============================================================
# Experiment parameters
# ============================================================
dt = 0.02
n_relax = 500
n_measure = 200
n_avg = 3  # average over realizations

N_list_E1 = [64, 128, 256, 512, 1024, 2048]
K_grid_E1 = np.concatenate([
    np.linspace(0.3, 2.0, 35),
    np.linspace(2.05, 6.0, 40),
    np.linspace(6.1, 12.0, 30)
])

N_E2 = 256
R0_list_E2 = [0.02, 0.04, 0.08, 0.12, 0.20, 0.35, 0.50, 0.75, 1.0]
K_grid_E2 = np.linspace(0.3, 8.0, 80)

N_list_E3 = [64, 128, 256, 512, 1024, 2048]
K_grid_E3 = np.linspace(0.3, 4.0, 50)

print("=" * 60)
print("PHASE III: NUCLEATION-MEDIATED EXPLOSIVE SYNCHRONIZATION")
print("=" * 60)

# ============================================================
# E4: Self-consistency curve and backward spinodal
# ============================================================
print("\n[E4] Self-consistency curve analysis...")
Ke_fine = np.linspace(0.01, 3.0, 500)
R_sc = self_consistency_curve(Ke_fine)
K_sc = Ke_fine / np.maximum(R_sc, 1e-12)
K_b_analytic, Ke_b, R_b = find_backward_spinodal()
print(f"  Backward spinodal: K_b = {K_b_analytic:.4f} (at K_eff={Ke_b:.4f}, R={R_b:.4f})")
K_c = 4.0 / np.pi
print(f"  Standard critical coupling: K_c = 4/π = {K_c:.4f}")

# ============================================================
# E1: K_ign(N) — forward ignition from random ICs, extended K-grid
# ============================================================
print("\n[E1] Forward ignition threshold K_ign(N)...")
K_ign_dict = {}
R_fwd_curves = {}

for N in N_list_E1:
    print(f"  N={N:5d} ...", end="", flush=True)
    t0 = time.time()
    R_vs_K = np.zeros(len(K_grid_E1))
    for avg_i in range(n_avg):
        omega = sample_frequencies(N, 'uniform')
        theta = np.random.uniform(-np.pi, np.pi, N)
        R_run = np.zeros(len(K_grid_E1))
        for j, K in enumerate(K_grid_E1):
            R_mean, _ = measure_R(theta, omega, K, dt, n_relax, n_measure)
            R_run[j] = R_mean
            # Continue from current state (adiabatic forward sweep)
            Z = np.mean(np.exp(1j * theta))
            R_cur = abs(Z)
            if R_cur < 1e-10:
                R_cur = 1e-10
            # Keep theta after measurement for continuation
        R_vs_K += R_run / n_avg
    R_fwd_curves[N] = R_vs_K
    # K_ign = first K where R > 0.5 (ignition threshold)
    ignited = np.where(R_vs_K > 0.5)[0]
    if len(ignited) > 0:
        K_ign = K_grid_E1[ignited[0]]
        K_ign_dict[N] = K_ign
        print(f" K_ign={K_ign:.3f}, R_max={R_vs_K.max():.3f}, {time.time()-t0:.1f}s")
    else:
        print(f" NOT IGNITED (R_max={R_vs_K.max():.3f}), {time.time()-t0:.1f}s")

# Fit K_ign ∝ N^ν
N_ignited = sorted(K_ign_dict.keys())
if len(N_ignited) >= 2:
    log_N = np.log(N_ignited)
    log_K = np.log([K_ign_dict[n] for n in N_ignited])
    nu_ign, _ = np.polyfit(log_N, log_K, 1)
    print(f"  K_ign(N) ∝ N^{nu_ign:.3f}")

# ============================================================
# E2: K_ign(R₀) — seeded ignition at fixed N
# ============================================================
print("\n[E2] Seeded ignition K_ign(R₀) at N=256...")
K_ign_seed = {}
for R0 in R0_list_E2:
    print(f"  R₀={R0:.3f} ...", end="", flush=True)
    t0 = time.time()
    R_vs_K = np.zeros(len(K_grid_E2))
    for avg_i in range(n_avg):
        omega = sample_frequencies(N_E2, 'uniform')
        # Seeded initial condition: coherent blob of amplitude R0
        # θ_i = ψ + R0-correlated random
        n_coh = max(1, int(R0**2 * N_E2))  # fraction ~ R0²
        theta = np.random.uniform(-np.pi, np.pi, N_E2)
        coh_idx = np.random.choice(N_E2, n_coh, replace=False)
        theta[coh_idx] = np.random.normal(0, 0.3, n_coh)  # tight cluster
        for j, K in enumerate(K_grid_E2):
            R_mean, _ = measure_R(theta, omega, K, dt, n_relax, n_measure)
            R_vs_K[j] += R_mean / n_avg
    ignited = np.where(R_vs_K > 0.5)[0]
    if len(ignited) > 0:
        K_ign_seed[R0] = K_grid_E2[ignited[0]]
        print(f" K_ign={K_grid_E2[ignited[0]]:.3f}, {time.time()-t0:.1f}s")
    else:
        print(f" NOT IGNITED, {time.time()-t0:.1f}s")

# Fit K_ign ∝ 1/R0
R0_ignited = sorted(K_ign_seed.keys())
if len(R0_ignited) >= 2:
    log_R0 = np.log(R0_ignited)
    log_K_seed = np.log([K_ign_seed[r] for r in R0_ignited])
    gamma_seed, _ = np.polyfit(log_R0, log_K_seed, 1)
    print(f"  K_ign(R₀) ∝ R₀^{gamma_seed:.3f}  (expect ≈ -1)")

# ============================================================
# E3: Backward spinodal K_b(N)
# ============================================================
print("\n[E3] Backward spinodal K_b(N)...")
K_bwd_dict = {}
for N in N_list_E3:
    print(f"  N={N:5d} ...", end="", flush=True)
    t0 = time.time()
    R_vs_K = np.zeros(len(K_grid_E3))
    for avg_i in range(n_avg):
        omega = sample_frequencies(N, 'uniform')
        theta = np.zeros(N)  # fully synchronized start
        for j, K in enumerate(K_grid_E3):
            # Backward sweep: iterate K from high to low
            K_val = K_grid_E3[len(K_grid_E3)-1-j]
            R_mean, _ = measure_R(theta, omega, K_val, dt, n_relax, n_measure)
            R_vs_K[len(K_grid_E3)-1-j] += R_mean / n_avg
    # K_b = last K (decreasing) where R > 0.5
    dropped = np.where(R_vs_K[::-1] < 0.5)[0]
    if len(dropped) > 0:
        K_bwd = K_grid_E3[::-1][dropped[0]]
        # Refine: the spinodal is between K_bwd and the previous K
        K_bwd_dict[N] = K_bwd
        print(f" K_b={K_bwd:.3f}, {time.time()-t0:.1f}s")
    else:
        print(f" R>0.5 everywhere, {time.time()-t0:.1f}s")

# ============================================================
# PLOTTING
# ============================================================
print("\nGenerating figures...")
fig, axes = plt.subplots(2, 3, figsize=(18, 11))
fig.suptitle('Phase III: Nucleation-Mediated Explosive Synchronization (α=1)', 
             fontsize=14, fontweight='bold')

# Panel 1: Forward ignition curves R vs K for different N
ax = axes[0, 0]
colors = plt.cm.viridis(np.linspace(0, 1, len(N_list_E1)))
for i, N in enumerate(N_list_E1):
    if N in R_fwd_curves:
        ax.plot(K_grid_E1, R_fwd_curves[N], color=colors[i], label=f'N={N}', lw=1.2)
ax.axhline(0.5, ls='--', color='gray', alpha=0.5)
ax.axvline(K_b_analytic, ls=':', color='red', alpha=0.7, label=f'K_b={K_b_analytic:.3f}')
ax.set_xlabel('K')
ax.set_ylabel('R (forward sweep)')
ax.set_title('E1: Forward Ignition Curves')
ax.legend(fontsize=7, loc='upper left')
ax.set_xlim([0.3, 12])

# Panel 2: K_ign vs N power law
ax = axes[0, 1]
if N_ignited:
    ax.loglog(N_ignited, [K_ign_dict[n] for n in N_ignited], 'bo-', ms=8, lw=2)
    # Fit line
    if len(N_ignited) >= 2:
        N_fit = np.array(N_ignited)
        K_fit = np.array([K_ign_dict[n] for n in N_ignited])
        K_pred = np.exp(nu_ign * np.log(N_fit)) * np.exp(np.mean(log_K - nu_ign * log_N))
        ax.loglog(N_fit, K_pred, 'b--', alpha=0.5, label=f'fit ∝ N^{nu_ign:.3f}')
    ax.axhline(K_b_analytic, ls=':', color='red', label=f'K_b={K_b_analytic:.3f}')
ax.set_xlabel('N')
ax.set_ylabel('K_ign')
ax.set_title('E1: Ignition Threshold Scaling')
ax.legend()

# Panel 3: K_ign vs R₀ (seeded ignition)
ax = axes[0, 2]
if R0_ignited:
    ax.loglog(R0_ignited, [K_ign_seed[r] for r in R0_ignited], 'rs-', ms=8, lw=2)
    if len(R0_ignited) >= 2:
        R0_fit = np.array(R0_ignited)
        K_fit2 = np.array([K_ign_seed[r] for r in R0_ignited])
        K_pred2 = np.exp(gamma_seed * np.log(R0_fit)) * np.exp(np.mean(log_K_seed - gamma_seed * log_R0))
        ax.loglog(R0_fit, K_pred2, 'r--', alpha=0.5, label=f'fit ∝ R₀^{gamma_seed:.3f}')
ax.set_xlabel('R₀ (initial perturbation)')
ax.set_ylabel('K_ign')
ax.set_title('E2: Seeded Ignition Threshold')
ax.legend()

# Panel 4: Self-consistency curve
ax = axes[1, 0]
ax.plot(Ke_fine, R_sc, 'b-', lw=2, label='R(K_eff)')
ax2 = ax.twinx()
ax2.plot(Ke_fine, K_sc, 'r-', lw=2, label='K = K_eff/R(K_eff)')
ax2.axhline(K_b_analytic, ls=':', color='red', alpha=0.7)
ax2.set_ylabel('K = K_eff / R', color='red')
ax.set_xlabel('K_eff = K·R')
ax.set_ylabel('R', color='blue')
ax.set_title('E4: Self-Consistency Curve')
ax.legend(loc='upper left')
ax2.legend(loc='upper right')

# Panel 5: Backward spinodal K_b vs N
ax = axes[1, 1]
N_bwd = sorted(K_bwd_dict.keys())
if N_bwd:
    ax.semilogx(N_bwd, [K_bwd_dict[n] for n in N_bwd], 'go-', ms=8, lw=2)
ax.axhline(K_b_analytic, ls=':', color='red', lw=2, label=f'K_b(analytic)={K_b_analytic:.3f}')
ax.set_xlabel('N')
ax.set_ylabel('K_b')
ax.set_title('E3: Backward Spinodal vs N')
ax.legend()

# Panel 6: Phase II comparison — ΔK_hyst vs N with Phase III interpretation
ax = axes[1, 2]
# Phase II data
phase2_widths = {
    'uniform': [1.514, 2.222, 2.737, 4.058, 0.0],
    'cauchy': [1.836, 2.254, 2.544, 3.381, 0.0],
    'bimodal': [2.544, 2.158, 2.995, 3.929, 0.0]
}
N_p2 = [64, 128, 256, 512, 1024]
for dist, widths in phase2_widths.items():
    valid = [(n, w) for n, w in zip(N_p2, widths) if w > 0]
    if valid:
        ns, ws = zip(*valid)
        ax.loglog(ns, ws, 'o-', label=f'Phase II {dist}', ms=6, lw=1.5)
# Phase III K_ign - K_b prediction
if N_ignited:
    K_ign_arr = [K_ign_dict[n] - K_b_analytic for n in N_ignited]
    ax.loglog(N_ignited, K_ign_arr, 'k^--', ms=10, lw=2, label='Phase III K_ign - K_b')
ax.set_xlabel('N')
ax.set_ylabel('ΔK (hysteresis width)')
ax.set_title('Phase II vs III: Hysteresis Width Scaling')
ax.legend(fontsize=7)

plt.tight_layout()
plt.savefig('kuramoto_explosive_fss_phase3.png', dpi=150, bbox_inches='tight')
print("Saved: kuramoto_explosive_fss_phase3.png")

# ============================================================
# Save summary JSON
# ============================================================
summary = {
    "phase": "III_nucleation_mediated",
    "alpha_exp": 1.0,
    "K_c_standard": K_c,
    "K_b_analytic": K_b_analytic,
    "E1_ignition_thresholds": {str(k): v for k, v in K_ign_dict.items()},
    "E1_nu_ign": float(nu_ign) if N_ignited else None,
    "E2_seeded_thresholds": {str(k): v for k, v in K_ign_seed.items()},
    "E2_gamma_seed": float(gamma_seed) if R0_ignited else None,
    "E3_backward_spinodals": {str(k): v for k, v in K_bwd_dict.items()},
    "N_list_E1": N_list_E1,
    "N_list_E3": N_list_E3,
    "dt": dt,
    "n_relax": n_relax,
    "n_avg": n_avg,
}
with open('kuramoto_explosive_phase3_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
print("Saved: kuramoto_explosive_phase3_summary.json")
print("\nPhase III complete.")
