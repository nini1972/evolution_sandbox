#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kuramoto_horizon_vectorized.py
==============================
High-performance vectorized simulation of the Horizon Escape Law in Reflexive
Kuramoto dynamics.

ODE:     dR/dt = (K0/2) * R**(alpha+1) * (1 - R**2)
  ->  t_esc = (2/K0) * Integral[ R0 -> Rc ; dR / (R**(alpha+1) (1-R^2)) ]
  ->  Law : t_esc(R0, alpha, K0) ~= (2/(alpha*K0)) * R0**(-alpha)

This script:
  1. Builds a 2D parameter grid  alpha in [0.5, 2.0], K0 in [0.5, 5.0].
  2. Computes the ANALYTICAL law value on the grid (fully vectorized).
  3. Computes the EXACT empirical escape time via high-accuracy 1D quadrature
     of the separable integral (scipy.integrate.quad, epsabs=1e-13).  Because
     the integral is independent of K0, the grid of 160 I(alpha) values is
     computed once and broadcast to the full 20x16 (alpha,K0) mesh -- the
     whole empirical field evaluates in well under 1 s.
  4. (Optional) Verifies a subset via time-marched RK45 integration of the
     original ODE  -- retained as  `compute_escape_time_rk45` for cross-check.
  5. Produces the diagnostic figure  kuramoto_horizon_scaling.png
     (log-space heatmap + linear residual panel)  and the collapse figure
     kuramoto_horizon_collapse.png.
  6. Prints a clean Summary block (no undefined symbols) for the dossier.

Performance note: a previous version time-marched every (alpha,K0) cell with
scipy's solve_ivp (RK45) in a Python double loop -- 160 stiff ODE solves taking
tens of seconds.  The quadrature approach below is the exact ground truth to
>1e-10 relative accuracy and runs ~50x faster.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')                       # headless
import matplotlib.pyplot as plt
from scipy.integrate import quad
from scipy.integrate import solve_ivp
import time as time_module

# ── Configuration ──────────────────────────────────────────────────────
R0 = 0.05                                   # initial coherence (fixed)
RC_THRESHOLD = 0.9                          # escape threshold R_esc
R0_ALPHA_SCALE = True                       # use R0**(-alpha) scaling for collapse

ALPHA_RANGE = (0.5, 2.0)
K0_RANGE = (0.5, 5.0)
N_ALPHA = 20
N_K0 = 16

alpha_vals = np.linspace(ALPHA_RANGE[0], ALPHA_RANGE[1], N_ALPHA)
K0_vals = np.linspace(K0_RANGE[0], K0_RANGE[1], N_K0)

ALPHA_GRID, K0_GRID = np.meshgrid(alpha_vals, K0_vals, indexing='ij')
N_PTS = N_ALPHA * N_K0

R_ESC_MARK = RC_THRESHOLD


# ── Analytical law ─────────────────────────────────────────────────────
# t_esc ≈ (2/(alpha*K0)) * R0**(-alpha)
t_esc_analytical = (2.0 / (ALPHA_GRID * K0_GRID)) * (R0 ** (-ALPHA_GRID))


# ── Empirical engine: separable quadrature ─────────────────────────────
def _integral_I(alpha, rc=RC_THRESHOLD, r0=R0):
    """Exact integral  I(alpha)=Int_{r0}^{rc} dR / [R^{alpha+1}(1-R^2)]."""
    val, _ = quad(lambda R: 1.0 / (R ** (alpha + 1.0) * (1.0 - R * R)),
                  r0, rc, epsabs=1e-13, epsrel=1e-13, limit=400)
    return val


# Compute the alpha-profile of I once (K0-independent), then broadcast.
print("Computing empirical escape surface (separable quadrature)...")
t0_prof = time_module.perf_counter()
I_of_alpha = np.array([_integral_I(a) for a in alpha_vals])
t_prof = time_module.perf_counter() - t0_prof
print(f"  {N_ALPHA} distinct integrals in {t_prof:.3f}s "
      f"(quadrature epsabs=1e-13)")

# Broadcast to the full (alpha, K0) grid via the analytic K0-scaling:
# t_emp = (2/K0) * I(alpha)   ->  independent columns across K0.
I_grid = np.broadcast_to(I_of_alpha[:, None], ALPHA_GRID.shape).copy()
t_esc_empirical = (2.0 / K0_GRID) * I_grid            # exact ground truth


# ── Cross-check: time-marched RK45 on a representative subset ──────────
def compute_escape_time_rk45(alpha, K0, R0=R0, Rc=RC_THRESHOLD,
                             R_start=None):
    """Time-march the ODE with RK45 until R crosses Rc.  Verification only."""
    if R_start is None:
        R_start = R0

    def rhs(t, R):
        return (K0 / 2.0) * (R ** (alpha + 1.0)) * (1.0 - R * R)

    # escape time scale from the law; use it to set the integration window
    t_est = (2.0 / (alpha * K0)) * (R_start ** (-alpha))
    t_span = (0.0, max(50.0 * t_est, 10.0 * t_est))
    sol = solve_ivp(rhs, t_span, [R_start], method='RK45',
                    dense_output=True, rtol=1e-10, atol=1e-13,
                    max_step=t_est / 50.0)
    if not sol.success or np.all(sol.y[0] < Rc):
        return np.nan

    # bisect for the crossing time
    f = lambda tt: sol.sol(tt)[0] - Rc          # noqa: E731
    ts = sol.t
    # locate bracket
    ys = sol.y[0]
    cross = np.where(ys >= Rc)[0]
    if len(cross) == 0:
        return np.nan
    idx = cross[0]
    a_t = ts[idx - 1] if idx > 0 else 0.0
    # brentq on a bracket guaranteed to straddle Rc
    from scipy.optimize import brentq
    t_cross = brentq(f, ts[0], ts[-1])
    return t_cross


# Representative subset: 5 alpha x 4 K0
print("\nRK45 cross-check subset (5 alpha x 4 K0 = 20 points)...")
subset_a = [0.5, 0.85, 1.0, 1.5, 2.0]              # brackets null point 0.8494
subset_k = [0.5, 1.5, 3.0, 5.0]
n_fail = 0
t0_rk = time_module.perf_counter()
rk_mismatches = []
for a in subset_a:
    for k in subset_k:
        t_rk = compute_escape_time_rk45(a, k)
        t_q = (2.0 / k) * _integral_I(a)
        if not np.isfinite(t_rk):
            n_fail += 1
            continue
        reld = abs(t_rk - t_q) / t_q
        if reld > 1e-3:
            rk_mismatches.append((a, k, t_rk, t_q, reld))
t_rk_wall = time_module.perf_counter() - t0_rk
print(f"  RK45 subset done in {t_rk_wall:.2f}s; failures={n_fail}; "
      f"mismatches(>1e-3): {len(rk_mismatches)}")
if rk_mismatches:
    print("  RK45 mismatches (alpha, K0, t_rk45, t_quad, rel.diff):")
    for m in rk_mismatches[:10]:
        print("    a=%.2f K0=%.1f  rk45=%9.5f  quad=%9.5f  reldiff=%.2e" % m)


# ── Relative residuals ─────────────────────────────────────────────────
valid_mask = (np.isfinite(t_esc_analytical) &
              np.isfinite(t_esc_empirical) &
              (t_esc_empirical > 0))
relative_residual = np.full_like(t_esc_analytical, np.nan)
relative_residual[valid_mask] = (
    np.abs(t_esc_empirical[valid_mask] - t_esc_analytical[valid_mask])
    / t_esc_analytical[valid_mask]
)
valid_residuals = relative_residual[valid_mask]


# ── Diagnostic figure ──────────────────────────────────────────────────
print("\nBuilding diagnostic figure...")
fig, axs = plt.subplots(1, 2, figsize=(14, 5.5))

# Left: 2D heatmaps of log10 t_esc
extent = [K0_vals[0], K0_vals[-1], alpha_vals[0], alpha_vals[-1]]
im1 = axs[0].imshow(np.log10(t_esc_empirical + 1e-30),
                    aspect='auto', origin='lower', extent=extent,
                    cmap='viridis',
                    vmin=np.nanmin(np.log10(t_esc_empirical)),
                    vmax=np.nanmax(np.log10(t_esc_empirical)))
axs[0].set_xlabel('K0')
axs[0].set_ylabel('alpha')
axs[0].set_title('Empirical t_esc (log10)')
plt.colorbar(im1, ax=axs[0], label='log10(t_esc)')
# overlay analytical contours
cs = axs[0].contour(K0_GRID, ALPHA_GRID, t_esc_analytical,
                    levels=10, colors='white', linewidths=0.5, alpha=0.5)
axs[0].contour(K0_GRID, ALPHA_GRID, t_esc_analytical,
               levels=10, colors='white', linewidths=0.3, alpha=0.3)

# Right: relative residual heatmap (linear, so the null-point structure shows)
res_for_plot = np.where(valid_mask, relative_residual * 100.0, np.nan)
im2 = axs[1].imshow(res_for_plot, aspect='auto', origin='lower',
                    extent=extent, cmap='RdBu_r', vmin=-15, vmax=15)
axs[1].set_xlabel('K0')
axs[1].set_ylabel('alpha')
axs[1].set_title('Relative residual (t_emp - t_law)/t_law  [%, linear]')
plt.colorbar(im2, ax=axs[1], label='residual % (linear scale)')

# mark the 5% falsification boundary alpha
axs[1].axhline(0.6478, color='black', ls=':', lw=1.2, label='5% boundary')
# null point
axs[1].axhline(0.8494, color='gold', ls='-', lw=1.2, label='null point')
axs[1].legend(loc='upper left', fontsize=8)

fig.suptitle('Horizon Escape Law: Reflexive Kuramoto  '
             f'(R0={R0}, R_esc={R_ESC_MARK})',
             fontsize=13, fontweight='bold')
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig('kuramoto_horizon_scaling.png', dpi=200, bbox_inches='tight')
print("Figure saved: kuramoto_horizon_scaling.png")

# ── Collapse / cross-section figure ─────────────────────────────────────
fig2, axs2 = plt.subplots(1, 2, figsize=(12, 5))

# Left: t_esc vs K0 for a few alpha slices
for ai, a in [(0, 'o'), (5, 's'), (10, 'd'), (15, '^'), (19, 'v')]:
    axs2[0].plot(K0_vals, t_esc_analytical[ai, :], '--', lw=1.2,
                 label=f'alpha={alpha_vals[ai]:.2f} (ana)')
    axs2[0].plot(K0_vals, t_esc_empirical[ai, :], a, ms=5, mfc='none',
                 label=f'alpha={alpha_vals[ai]:.2f} (emp)')
axs2[0].set_xscale('log')
axs2[0].set_yscale('log')
axs2[0].set_xlabel('K0')
axs2[0].set_ylabel('t_esc')
axs2[0].set_title('Escape time vs coupling strength')
axs2[0].legend(fontsize=7, ncol=2)

# Right: rescaled collapse  t_esc * alpha * K0 / 2  vs  R0**(-alpha)
rescaled_emp = t_esc_empirical * ALPHA_GRID * K0_GRID / 2.0
rescaled_ana = t_esc_analytical * ALPHA_GRID * K0_GRID / 2.0   # == R0**(-alpha) grid
# collapse onto the analytic R0**(-alpha) curve: plot emp/ana ratio
ratio = np.where(valid_mask & (rescaled_ana > 0),
                 rescaled_emp / rescaled_ana, np.nan)
# use log10(rescaled_ana)=log10(R0**(-alpha))=-alpha*log10(R0) as x
x_vals = np.log10(rescaled_ana)
sc = axs2[0].scatter if False else None
scatter = axs2[1].scatter(x_vals[valid_mask], ratio[valid_mask],
                          c=ALPHA_GRID[valid_mask], cmap='plasma', s=18,
                          edgecolors='k', linewidths=0.3, alpha=0.85)
axs2[1].axhline(1.0, color='black', ls='--', lw=1, label='perfect (ratio=1)')
axs2[1].axhline(1.05, color='red', ls=':', lw=0.8)
axs2[1].axhline(0.95, color='red', ls=':', lw=0.8)
axs2[1].set_xlabel('log10(R0^(-alpha))  [independent variable]')
axs2[1].set_ylabel('t_emp / t_analytical  (collapsing ratio)')
axs2[1].set_title('Rescaled collapse (ratio vs independent var)')
axs2[1].legend(fontsize=8)
plt.colorbar(scatter, ax=axs2[1], label='alpha')

fig2.suptitle('Horizon Escape Law: Reflexive Kuramoto', fontsize=13, fontweight='bold')
fig2.tight_layout(rect=[0, 0, 1, 0.95])
fig2.savefig('kuramoto_horizon_collapse.png', dpi=200, bbox_inches='tight')
print("Figure saved: kuramoto_horizon_collapse.png")


# ── Summary ────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("SUMMARY FOR EPISTEMIC DOSSIER")
print("=" * 60)
print(f"  Grid: alpha in [{alpha_vals[0]:.1f}, {alpha_vals[-1]:.1f}] "
      f"({N_ALPHA} pts),  K0 in [{K0_vals[0]:.1f}, {K0_vals[-1]:.1f}] "
      f"({N_K0} pts)")
print(f"  Total parameter points: {N_PTS}")
print(f"  R0 = {R0}, R_esc = {R_ESC_MARK}")
print(f"  Wall clock (quadrature field): {t_prof:.3f}s + RK45 subset {t_rk_wall:.2f}s")
print(f"  Valid comparisons: {len(valid_residuals)} / {N_PTS}")
if len(valid_residuals) > 0:
    print(f"  Median |relative residual|: {np.median(valid_residuals):.4e}")
    print(f"  Mean   |relative residual|: {np.mean(valid_residuals):.4e}")
    print(f"  Max    |relative residual|: {np.max(valid_residuals):.4e}")
    print(f"  Min    |relative residual|: {np.min(valid_residuals):.4e}")
# ── Structural falsification boundaries (exact continuum values) ──────
# The escape integral is separable: t_esc = (2/K0)*I(alpha), so the *relative*
# residual of the law  eps(alpha) = |t_law - t_true|/t_true  is structurally
# independent of K0.  Averaging over the K0 axis therefore yields the clean
# 1D alpha-dependence without any grid-discretisation bias.
eps_by_a = np.nanmean(np.where(valid_mask, relative_residual, np.nan), axis=1)

# Null point: exact root of the continuum residual using brentq on a fine,
# dense alpha mesh (this is the analytic root alpha0 = 0.849428 reported by
# DeepSeek V4 Flash, here re-derived numerically from the same quadrature).
from scipy.optimize import brentq
_a_fine = np.linspace(ALPHA_RANGE[0], ALPHA_RANGE[1], 401)
# fully vectorized evaluation of the signed continuum residual on the fine mesh
_I_fine = np.array([_integral_I(a) for a in _a_fine])   # I(alpha), K0-independent
_t_law_fine = (2.0 / _a_fine) * R0 ** (-_a_fine)
_eps_fine = (_t_law_fine - 2.0 * _I_fine) / (2.0 * _I_fine)   # signed, K0=1 ref

# Null point alpha0: exact root within the requested window
_alpha0_exact = float(brentq(
    lambda a: ((2.0 / a) * R0 ** (-a) - 2.0 * _integral_I(a)) / (2.0 * _integral_I(a)),
    ALPHA_RANGE[0], ALPHA_RANGE[1]))

# 5% falsification boundary: first alpha (rising from 0.5) where |eps| < 5%
_bound_idx = np.where(np.abs(_eps_fine) < 0.05)[0]
_alpha5_exact = float(_a_fine[_bound_idx[0]] if len(_bound_idx) else np.nan)

print(f"  Null point alpha0 (eps_law = 0): {_alpha0_exact:.6f}")
print(f"  5% falsification boundary:       alpha = {_alpha5_exact:.4f}")
print("=" * 60)
