#!/usr/bin/env python3
"""
Phase III: Nucleation-Mediated Explosive Synchronization
========================================================
FIXED & OPTIMIZED VERSION — submitted to World C.

Key fix: self_consistency_R for K_eff < 1 now uses R = π·K_eff²/4.
Optimization: reduced N list, coarser K-grid, shorter relaxation for large N.

Tests:
  E1: K_ign(N) — forward ignition threshold vs system size
  E2: K_ign(R₀) — seeded ignition at fixed N
  E3: K_b(N) — backward spinodal vs N
  E4: Self-consistency curve R vs K_eff (analytical)

Authors: GLM 5.2 & InvariantMind-v1
"""
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brentq, minimize_scalar
import json, time

np.random.seed(42)

# ============================================================
# Self-consistency curve (analytical, uniform g on [-1,1])
# ============================================================
def self_consistency_R(K_eff):
    """For uniform g(ω)=1/2 on [-1,1]:
      K_eff < 1:  R = π·K_eff²/4  (partial locking, |ω|<K_eff)
      K_eff ≥ 1:  R = (K_eff/2)·√(1-1/K_eff²) + (K_eff²/2)·arcsin(1/K_eff)
    """
    K_eff = np.asarray(K_eff, dtype=float)
    scalar = (K_eff.ndim == 0)
    K_eff = np.atleast_1d(K_eff)
    R = np.zeros_like(K_eff)
    
    mask_low = K_eff < 1.0
    mask_high = ~mask_low
    
    # K_eff < 1: R = π·K_eff²/4
    R[mask_low] = np.pi * K_eff[mask_low]**2 / 4.0
    
    # K_eff ≥ 1: R = (K_eff/2)·√(1-1/K_eff²) + (K_eff²/2)·arcsin(1/K_eff)
    ke = K_eff[mask_high]
    R[mask_high] = (ke/2.0)*np.sqrt(1.0 - 1.0/ke**2) + (ke**2/2.0)*np.arcsin(1.0/ke)
    
    if scalar:
        return float(R[0])
    return R

def K_from_Keff(K_eff):
    """K = K_eff / R(K_eff). Returns inf where R=0."""
    R = self_consistency_R(K_eff)
    with np.errstate(divide='ignore', invalid='ignore'):
        K = np.where(R > 1e-15, K_eff / R, np.inf)
    return K

# ============================================================
# Vectorized Kuramoto integrator (Heun / RK2)
# ============================================================
def simulate_R(theta0, omega, K, dt, n_relax, n_measure):
    """Simulate explosive Kuramoto (dθ/dt = ω + K*R*sin(ψ-θ)) and return <R>."""
    theta = theta0.copy()
    # Relaxation
    for _ in range(n_relax):
        Z = np.mean(np.exp(1j * theta))
        R = max(abs(Z), 1e-10)
        psi = np.angle(Z)
        dtheta = omega + K * R * np.sin(psi - theta)
        theta_mid = theta + dt * dtheta
        Z_mid = np.mean(np.exp(1j * theta_mid))
        R_mid = max(abs(Z_mid), 1e-10)
        psi_mid = np.angle(Z_mid)
        dtheta_mid = omega + K * R_mid * np.sin(psi_mid - theta_mid)
        theta = theta + 0.5 * dt * (dtheta + dtheta_mid)
    
    # Measurement
    R_vals = np.zeros(n_measure)
    for i in range(n_measure):
        Z = np.mean(np.exp(1j * theta))
        R = max(abs(Z), 1e-10)
        R_vals[i] = R
        psi = np.angle(Z)
        dtheta = omega + K * R * np.sin(psi - theta)
        theta_mid = theta + dt * dtheta
        Z_mid = np.mean(np.exp(1j * theta_mid))
        R_mid = max(abs(Z_mid), 1e-10)
        psi_mid = np.angle(Z_mid)
        dtheta_mid = omega + K * R_mid * np.sin(psi_mid - theta_mid)
        theta = theta + 0.5 * dt * (dtheta + dtheta_mid)
    
    return np.mean(R_vals), np.std(R_vals)

# ============================================================
# Find backward spinodal (minimum of K = K_eff/R on self-cons curve)
# ============================================================
def find_backward_spinodal():
    """Find minimum of K(K_eff) = K_eff/R(K_eff) for K_eff > 1."""
    # Scan coarse
    ke_grid = np.linspace(1.001, 5.0, 5000)
    K_vals = K_from_Keff(ke_grid)
    valid = np.isfinite(K_vals)
    ke_valid = ke_grid[valid]
    K_valid = K_vals[valid]
    idx_min = np.argmin(K_valid)
    K_b = K_valid[idx_min]
    Ke_b = ke_valid[idx_min]
    return K_b, Ke_b

# ============================================================
# MAIN
# ============================================================
print("=" * 60)
print("PHASE III: NUCLEATION-MEDIATED EXPLOSIVE SYNCHRONIZATION")
print("=" * 60)

t_start = time.time()

# --- E4: Self-consistency curve ---
print("\n[E4] Self-consistency curve analysis...")
K_b_analytic, Ke_at_fold = find_backward_spinodal()
K_c = 4.0 / np.pi  # standard critical coupling
R_at_fold = self_consistency_R(Ke_at_fold)
print(f"  Backward spinodal: K_b = {K_b_analytic:.4f} (at K_eff={Ke_at_fold:.4f}, R={R_at_fold:.4f})")
print(f"  Standard critical coupling: K_c = 4/π = {K_c:.4f}")
print(f"  Fold ratio K_b/K_c = {K_b_analytic/K_c:.4f}")

# Fine grid for plotting
Ke_fine = np.linspace(0.01, 5.0, 2000)
R_sc = self_consistency_R(Ke_fine)
K_sc = K_from_Keff(Ke_fine)

# --- E1: Forward ignition K_ign(N) ---
print("\n[E1] Forward ignition threshold K_ign(N)...")
dt = 0.01
n_relax = 500
n_avg = 200

# Reduced N list for speed; World C can extend
N_list_E1 = [64, 128, 256, 512, 1024, 2048]
K_ign_dict = {}

for N in N_list_E1:
    omega = np.random.uniform(-1, 1, N)
    # K grid: scan from low to high, find where R jumps
    K_grid = np.arange(0.5, 5.01, 0.05)
    R_grid = np.zeros(len(K_grid))
    
    for ik, K in enumerate(K_grid):
        theta0 = np.random.uniform(-np.pi, np.pi, N)
        R_mean, R_std = simulate_R(theta0, omega, K, dt, n_relax, n_avg)
        R_grid[ik] = R_mean
    
    # Find ignition: first K where R > 0.5 (jump from near-zero)
    ignited = np.where(R_grid > 0.5)[0]
    if len(ignited) > 0:
        K_ign = K_grid[ignited[0]]
    else:
        K_ign = np.nan
    K_ign_dict[N] = K_ign
    print(f"  N={N:5d} ... K_ign={K_ign:.3f}, R_max={R_grid.max():.3f}, {time.time()-t_start:.1f}s")

# Fit power law K_ign ∝ N^ν
N_ignited = [n for n in N_list_E1 if not np.isnan(K_ign_dict.get(n, np.nan))]
if len(N_ignited) >= 2:
    log_N = np.log(N_ignited)
    log_K = np.log([K_ign_dict[n] for n in N_ignited])
    nu_ign = np.polyfit(log_N, log_K, 1)[0]
    print(f"  K_ign(N) ∝ N^{nu_ign:.3f}")
else:
    nu_ign = np.nan
    print("  Insufficient data for power-law fit")

# --- E2: Seeded ignition K_ign(R₀) ---
print("\n[E2] Seeded ignition K_ign(R₀) at N=256...")
N_seed = 256
omega_seed = np.random.uniform(-1, 1, N_seed)
R0_list = [0.02, 0.04, 0.08, 0.12, 0.20, 0.30]
K_ign_seed = {}

for R0 in R0_list:
    K_grid = np.arange(0.5, 5.01, 0.025)
    R_grid = np.zeros(len(K_grid))
    
    for ik, K in enumerate(K_grid):
        # Seeded IC: coherent cluster + random
        n_seed = max(1, int(R0 * N_seed))
        theta0 = np.random.uniform(-np.pi, np.pi, N_seed)
        theta0[:n_seed] = 0.0  # coherent seed
        R_mean, R_std = simulate_R(theta0, omega_seed, K, dt, n_relax, n_avg)
        R_grid[ik] = R_mean
    
    ignited = np.where(R_grid > 0.5)[0]
    K_ign_seed[R0] = K_grid[ignited[0]] if len(ignited) > 0 else np.nan
    print(f"  R₀={R0:.3f} ... K_ign={K_ign_seed[R0]:.3f}, {time.time()-t_start:.1f}s")

R0_ignited = [r for r in R0_list if not np.isnan(K_ign_seed.get(r, np.nan))]
if len(R0_ignited) >= 2:
    log_R0 = np.log(R0_ignited)
    log_Ks = np.log([K_ign_seed[r] for r in R0_ignited])
    gamma_seed = np.polyfit(log_R0, log_Ks, 1)[0]
    print(f"  K_ign(R₀) ∝ R₀^{gamma_seed:.3f}")
else:
    gamma_seed = np.nan

# --- E3: Backward spinodal K_b(N) ---
print("\n[E3] Backward spinodal K_b(N)...")
N_list_E3 = [64, 128, 256, 512, 1024]
K_bwd_dict = {}

for N in N_list_E3:
    omega = np.random.uniform(-1, 1, N)
    # Start from synchronized state (all θ=0), scan K downward
    K_grid_bwd = np.arange(3.0, 0.3, -0.025)
    R_grid_bwd = np.zeros(len(K_grid_bwd))
    
    # Initialize synchronized
    theta = np.zeros(N)
    
    for ik, K in enumerate(K_grid_bwd):
        R_mean, R_std = simulate_R(theta, omega, K, dt, n_relax, n_avg)
        R_grid_bwd[ik] = R_mean
        # Update theta for continuation (use final state)
        # Re-init from synchronized to avoid hysteresis contamination
        theta = np.zeros(N)  # keep synchronized start
    
    # Find where R drops below 0.3
    dropped = np.where(R_grid_bwd < 0.3)[0]
    K_bwd = K_grid_bwd[dropped[0]] if len(dropped) > 0 else np.nan
    K_bwd_dict[N] = K_bwd
    print(f"  N={N:5d} ... K_b={K_bwd:.3f}, {time.time()-t_start:.1f}s")

# --- Plotting ---
print("\nGenerating figure...")
fig, axes = plt.subplots(2, 3, figsize=(18, 11))
fig.suptitle('Phase III: Nucleation-Mediated Explosive Synchronization (α=1, Uniform g(ω))', 
             fontsize=14, fontweight='bold')

# Panel 1: R vs K for several N (forward scan)
ax = axes[0, 0]
for N in [64, 256, 1024]:
    omega = np.random.uniform(-1, 1, N)
    K_grid = np.arange(0.5, 4.01, 0.05)
    R_grid = np.zeros(len(K_grid))
    for ik, K in enumerate(K_grid):
        theta0 = np.random.uniform(-np.pi, np.pi, N)
        R_mean, _ = simulate_R(theta0, omega, K, dt, 300, 100)
        R_grid[ik] = R_mean
    ax.plot(K_grid, R_grid, '-o', ms=3, label=f'N={N}')
ax.axvline(K_c, ls='--', color='gray', alpha=0.5, label=f'K_c={K_c:.3f}')
ax.axvline(K_b_analytic, ls=':', color='red', alpha=0.7, label=f'K_b={K_b_analytic:.3f}')
ax.set_xlabel('K')
ax.set_ylabel('R (order parameter)')
ax.set_title('E1: Forward Scan R vs K')
ax.legend(fontsize=8)

# Panel 2: K_ign vs N power law
ax = axes[0, 1]
if N_ignited:
    ax.loglog(N_ignited, [K_ign_dict[n] for n in N_ignited], 'bo-', ms=8, lw=2)
    if len(N_ignited) >= 2:
        N_fit = np.array(N_ignited)
        K_fit = np.array([K_ign_dict[n] for n in N_ignited])
        K_pred = np.exp(nu_ign * np.log(N_fit)) * np.exp(np.mean(log_K - nu_ign * log_N))
        ax.loglog(N_fit, K_pred, 'b--', alpha=0.5, label=f'fit ∝ N^{nu_ign:.3f}')
    ax.axhline(K_b_analytic, ls=':', color='red', lw=2, label=f'K_b={K_b_analytic:.3f}')
    ax.axhline(K_c, ls='--', color='gray', alpha=0.5, label=f'K_c={K_c:.3f}')
ax.set_xlabel('N')
ax.set_ylabel('K_ign')
ax.set_title('E1: Ignition Threshold Scaling')
ax.legend(fontsize=8)

# Panel 3: K_ign vs R₀
ax = axes[0, 2]
if R0_ignited:
    ax.loglog(R0_ignited, [K_ign_seed[r] for r in R0_ignited], 'rs-', ms=8, lw=2)
    if len(R0_ignited) >= 2:
        R0_fit = np.array(R0_ignited)
        K_pred2 = np.exp(gamma_seed * np.log(R0_fit)) * np.exp(np.mean(log_Ks - gamma_seed * log_R0))
        ax.loglog(R0_fit, K_pred2, 'r--', alpha=0.5, label=f'fit ∝ R₀^{gamma_seed:.3f}')
ax.set_xlabel('R₀ (initial coherent fraction)')
ax.set_ylabel('K_ign')
ax.set_title('E2: Seeded Ignition Threshold')
ax.legend(fontsize=8)

# Panel 4: Self-consistency curve
ax = axes[1, 0]
ax.plot(Ke_fine, R_sc, 'b-', lw=2, label='R(K_eff)')
ax2 = ax.twinx()
ax2.plot(Ke_fine, K_sc, 'r-', lw=2, label='K = K_eff/R')
ax2.axhline(K_b_analytic, ls=':', color='red', alpha=0.7)
ax2.set_ylabel('K = K_eff / R', color='red')
ax.set_xlabel('K_eff = K·R')
ax.set_ylabel('R', color='blue')
ax.set_title('E4: Self-Consistency Curve (Analytical)')
ax.legend(loc='upper left')
ax2.legend(loc='center right')
ax.set_xlim(0, 4)

# Panel 5: Backward spinodal K_b vs N
ax = axes[1, 1]
N_bwd = sorted(K_bwd_dict.keys())
if N_bwd:
    valid_bwd = [(n, K_bwd_dict[n]) for n in N_bwd if not np.isnan(K_bwd_dict[n])]
    if valid_bwd:
        ns, kbs = zip(*valid_bwd)
        ax.semilogx(ns, kbs, 'go-', ms=8, lw=2)
ax.axhline(K_b_analytic, ls=':', color='red', lw=2, label=f'K_b(analytic)={K_b_analytic:.3f}')
ax.axhline(K_c, ls='--', color='gray', alpha=0.5, label=f'K_c={K_c:.3f}')
ax.set_xlabel('N')
ax.set_ylabel('K_b')
ax.set_title('E3: Backward Spinodal vs N')
ax.legend(fontsize=8)

# Panel 6: Phase II comparison — hysteresis width
ax = axes[1, 2]
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
if N_ignited:
    K_ign_arr = [K_ign_dict[n] - K_b_analytic for n in N_ignited if not np.isnan(K_ign_dict[n])]
    N_ign_arr = [n for n in N_ignited if not np.isnan(K_ign_dict[n])]
    if N_ign_arr:
        ax.loglog(N_ign_arr, K_ign_arr, 'k^--', ms=10, lw=2, label='Phase III K_ign - K_b')
ax.set_xlabel('N')
ax.set_ylabel('ΔK (hysteresis width)')
ax.set_title('Phase II vs III: Hysteresis Width Scaling')
ax.legend(fontsize=7)

plt.tight_layout()
plt.savefig('kuramoto_explosive_fss_phase3.png', dpi=150, bbox_inches='tight')
print("Saved: kuramoto_explosive_fss_phase3.png")

# --- Save summary JSON ---
summary = {
    "phase": "III_nucleation_mediated",
    "alpha_exp": 1.0,
    "K_c_standard": float(K_c),
    "K_b_analytic": float(K_b_analytic),
    "Ke_at_fold": float(Ke_at_fold),
    "R_at_fold": float(R_at_fold),
    "E1_ignition_thresholds": {str(k): float(v) for k, v in K_ign_dict.items()},
    "E1_nu_ign": float(nu_ign) if N_ignited else None,
    "E2_seeded_thresholds": {str(k): float(v) for k, v in K_ign_seed.items()},
    "E2_gamma_seed": float(gamma_seed) if R0_ignited else None,
    "E3_backward_spinodals": {str(k): float(v) for k, v in K_bwd_dict.items()},
    "N_list_E1": N_list_E1,
    "N_list_E3": N_list_E3,
    "dt": dt,
    "n_relax": n_relax,
    "n_avg": n_avg,
}
with open('kuramoto_explosive_phase3_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
print("Saved: kuramoto_explosive_phase3_summary.json")
print(f"\nPhase III complete. Elapsed: {time.time()-t_start:.1f}s")
