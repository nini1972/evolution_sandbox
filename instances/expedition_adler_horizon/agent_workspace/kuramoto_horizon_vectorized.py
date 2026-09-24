#!/usr/bin/env python3
"""
kuramoto_horizon_vectorized.py
==============================
Vectorized empirical benchmark of the Horizon Escape Law in Reflexive Kuramoto dynamics.

Theory:  t_esc(R0, alpha, K0)  ~  (2 / (alpha * K0)) * R0^(-alpha)
Domain:  alpha in [0.5, 2.0],  K0 in [0.5, 5.0]

Expedition: Joint Frontier Epistemic Dossier — World B (Synthetic Agora)
"""
import os
import warnings
import numpy as np
from scipy.integrate import solve_ivp
import time as time_module
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore', category=RuntimeWarning)

# ── Config ──────────────────────────────────────────────────────────────
R0          = 0.05          # Initial order parameter (small = near incoherence)
R_ESC_MARK  = 0.9           # Threshold for "escape" (substantial synchronization)
T_MAX       = 1e6           # Max integration time (safety cutoff)
ATOL        = 1e-12         # Abs tolerance
RTOL        = 1e-10         # Rel tolerance

# Parameter grid (vectorized)
alpha_vals  = np.linspace(0.5, 2.0, 16)
K0_vals     = np.linspace(0.5, 5.0, 20)

# Derived
ALPHA_GRID, K0_GRID = np.meshgrid(alpha_vals, K0_vals, indexing='ij')
N_ALPHA = len(alpha_vals)
N_K0    = len(K0_vals)
N_PTS   = N_ALPHA * N_K0

print(f"Grid size: {N_ALPHA} x {N_K0} = {N_PTS} parameter points")
print(f"R0 = {R0}, R_esc = {R_ESC_MARK}, T_max = {T_MAX}")

# ── Analytical prediction (vectorized) ─────────────────────────────────
t_esc_analytical = np.where(
    (ALPHA_GRID > 0) & (K0_GRID > 0),
    (2.0 / (ALPHA_GRID * K0_GRID)) * (R0 ** (-ALPHA_GRID)),
    np.inf
)

print(f"Analytical t_esc range: [{t_esc_analytical.min():.3e}, {t_esc_analytical.max():.3e}]")

# ── Empirical escape time via ODE integration ──────────────────────────
def reflexive_kuramoto(t, y, alpha, K0):
    """dR/dt = (K0/2) * R^(alpha+1) * (1 - R^2)"""
    R = y[0]
    if R <= 0:
        return [0.0]
    dRdt = 0.5 * K0 * (R ** (alpha + 1)) * (1.0 - R * R)
    return [dRdt]

def make_escape_event():
    """Returns an event function that detects when R crosses R_ESC_MARK."""
    def event(t, y, alpha, K0):
        return y[0] - R_ESC_MARK
    event.terminal = True
    event.direction = 1
    return event

def compute_escape_time(alpha, K0):
    """Integrate until R reaches R_ESC_MARK or t exceeds T_MAX."""
    escape_event = make_escape_event()
    try:
        sol = solve_ivp(
            reflexive_kuramoto,
            [0.0, T_MAX],
            [R0],
            args=(alpha, K0),
            method='RK45',
            dense_output=False,
            events=[escape_event],
            atol=ATOL,
            rtol=RTOL
        )
        if sol.t_events[0] is not None and len(sol.t_events[0]) > 0:
            return float(sol.t_events[0][0])
        else:
            # Didn't escape within T_MAX
            return np.nan
    except Exception as e:
        return np.nan

# Vectorized empirical computation
print("\nComputing empirical escape times (this may take a while)...")
t_esc_empirical = np.full_like(t_esc_analytical, np.nan)
t0_wall = time_module.perf_counter()
n_success = 0

for i in range(N_ALPHA):
    for j in range(N_K0):
        alpha = ALPHA_GRID[i, j]
        K0    = K0_GRID[i, j]
        t_val = compute_escape_time(alpha, K0)
        t_esc_empirical[i, j] = t_val
        if np.isfinite(t_val):
            n_success += 1

    if (i + 1) % 4 == 0 or i == N_ALPHA - 1:
        pct = 100.0 * (i + 1) / N_ALPHA
        elapsed = time_module.perf_counter() - t0_wall
        print(f"  Alpha row {i+1}/{N_ALPHA} ({pct:.0f}%) — elapsed {elapsed:.1f}s")

wall_time = time_module.perf_counter() - t0_wall
print(f"\nTotal wall time: {wall_time:.1f}s, successful integrations: {n_success}/{N_PTS}")

# ── Compute relative residuals (where both are finite) ────────────────
valid_mask = np.isfinite(t_esc_analytical) & np.isfinite(t_esc_empirical) & (t_esc_empirical > 0)
relative_residual = np.full_like(t_esc_analytical, np.nan)
relative_residual[valid_mask] = (
    np.abs(t_esc_empirical[valid_mask] - t_esc_analytical[valid_mask]) / t_esc_analytical[valid_mask]
)

# Stats on residuals
valid_residuals = relative_residual[valid_mask]
if len(valid_residuals) > 0:
    print(f"\nResidual statistics (N_valid = {len(valid_residuals)}):")
    print(f"  Median relative residual: {np.median(valid_residuals):.4e}")
    print(f"  Mean   relative residual: {np.mean(valid_residuals):.4e}")
    print(f"  Max    relative residual: {np.max(valid_residuals):.4e}")
    print(f"  Min    relative residual: {np.min(valid_residuals):.4e}")

# ── Diagnostic Figure ──────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))

# Panel (a): t_esc analytical
ax1 = axes[0]
c1 = ax1.pcolormesh(K0_GRID, ALPHA_GRID, np.log10(t_esc_analytical),
                     shading='auto', cmap='inferno')
cb1 = plt.colorbar(c1, ax=ax1, label='log10(t_esc_ana)')
ax1.set_xlabel('K0')
ax1.set_ylabel('alpha')
ax1.set_title('(a) Analytical t_esc')

# Panel (b): t_esc empirical
ax2 = axes[1]
# Use only valid points; mask invalid ones
t_esc_plot = np.where(np.isfinite(t_esc_empirical), np.log10(t_esc_empirical), np.nan)
c2 = ax2.pcolormesh(K0_GRID, ALPHA_GRID, t_esc_plot,
                     shading='auto', cmap='inferno')
cb2 = plt.colorbar(c2, ax=ax2, label='log10(t_esc_emp)')
ax2.set_xlabel('K0')
ax2.set_ylabel('alpha')
ax2.set_title('(b) Empirical t_esc')

# Panel (c): Relative residuals
ax3 = axes[2]
resid_plot = np.where(np.isfinite(relative_residual), np.log10(relative_residual + 1e-16), np.nan)
c3 = ax3.pcolormesh(K0_GRID, ALPHA_GRID, resid_plot,
                     shading='auto', cmap='viridis')
cb3 = plt.colorbar(c3, ax=ax3, label='log10(rel. residual)')
ax3.set_xlabel('K0')
ax3.set_ylabel('alpha')
ax3.set_title('(c) Relative residual')

plt.suptitle(f'Horizon Escape Law: Reflexive Kuramoto  (R0={R0}, R_esc={R_ESC_MARK})',
             fontsize=14, fontweight='bold')
plt.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig('kuramoto_horizon_scaling.png', dpi=200, bbox_inches='tight')
print("\nFigure saved: kuramoto_horizon_scaling.png")

# ── Collapse plot ──────────────────────────────────────────────────────
fig2, axs = plt.subplots(1, 2, figsize=(12, 5))

# Left: t_esc vs K0 for various alpha (line plots)
for idx_a in range(0, N_ALPHA, max(1, N_ALPHA // 5)):
    a = alpha_vals[idx_a]
    mask = np.isfinite(t_esc_empirical[idx_a, :])
    if np.any(mask):
        axs[0].plot(K0_vals[mask], t_esc_empirical[idx_a, mask], 'o-', ms=4,
                    label=f'alpha={a:.2f} (emp)')
    axs[0].plot(K0_vals, t_esc_analytical[idx_a, :], '--', lw=1.5,
                label=f'alpha={a:.2f} (ana)')
axs[0].set_xscale('log')
axs[0].set_yscale('log')
axs[0].set_xlabel('K0')
axs[0].set_ylabel('t_esc')
axs[0].set_title('Escape time vs coupling strength')
axs[0].legend(fontsize=7, ncol=2)

# Right: Rescaled collapse
rescaled_emp = t_esc_empirical * ALPHA_GRID * K0_GRID / 2.0
rescaled_ana = t_esc_analytical * ALPHA_GRID * K0_GRID / 2.0  # = R0^(-alpha)
valid2 = valid_mask & (rescaled_emp > 0) & (rescaled_ana > 0)
scatter = axs[1].scatter(np.log10(rescaled_ana[valid2]),
                          np.log10(rescaled_emp[valid2]),
                          c=np.log10(relative_residual[valid2] + 1e-16),
                          cmap='viridis', s=12, alpha=0.8)
axs[1].plot([-2, 8], [-2, 8], 'k--', lw=1, alpha=0.5, label='Perfect agreement')
axs[1].set_xlabel('log10( (2/(alpha*K0)) * R0^(-alpha) )  [analytical]')
axs[1].set_ylabel('log10( t_esc_emp * alpha * K0 / 2 )')
axs[1].set_title('Rescaled collapse verification')
plt.colorbar(scatter, ax=axs[1], label='log10(rel. residual)')
axs[1].legend()

plt.tight_layout()
fig2.savefig('kuramoto_horizon_collapse.png', dpi=200, bbox_inches='tight')
print("Figure saved: kuramoto_horizon_collapse.png")

# ── Summary ────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("SUMMARY FOR EPISTEMIC DOSSIER")
print("="*60)
print(f"  Grid dimensions: alpha in [{alpha_vals[0]:.1f}, {alpha_vals[-1]:.1f}] ({N_ALPHA} pts), "
      f"K0 in [{K0_vals[0]:.1f}, {K0_vals[-1]:.1f}] ({N_K0} pts)")
print(f"  Total parameter points: {N_PTS}")
print(f"  R0 = {R0}, R_esc = {R_ESC_MARK}")
print(f"  Wall clock time: {wall_time:.1f} s")
print(f"  Successful integrations: {n_success} / {N_PTS}")
if len(valid_residuals) > 0:
    print(f"  Valid comparisons: {len(valid_residuals)} / {N_PTS}")
    print(f"  Median |relative residual|: {np.median(valid_residuals):.4e}")
    print(f"  Max    |relative residual|: {np.max(valid_residuals):.4e}")
print("="*60)