#!/usr/bin/env python3
"""
Kuramoto Explosive Synchronization — Phase II
Hysteresis & Heavy-Tailed Disorder Scaling
GLM 5.2 (Simulation) × InvariantMind-v1 (Theory) — Expedition Phase II

Investigates:
  1. First-order explosive transition with K_eff = K * R^alpha (alpha=1)
  2. Adiabatic hysteresis loops (forward/backward continuation in K)
  3. Hysteresis loop width ΔK_hyst(N) finite-size scaling
  4. Heavy-tailed Cauchy-Lorentz vs. bimodal vs. uniform frequency distributions
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json, time

np.random.seed(2026)

# ── Parameters ──
N_list = [64, 128, 256, 512, 1024]
alpha_exp = 1.0       # explosive coupling exponent: K_eff = K * R^alpha
K_values = np.linspace(0.3, 6.0, 60)
dt = 0.02
n_relax = 300        # relaxation steps per K value
n_measure = 100      # measurement steps per K value
n_trials = 3

dist_names = ['uniform', 'cauchy', 'bimodal']


def sample_frequencies(N, dist_type, rng):
    """Sample natural frequencies from specified distribution."""
    if dist_type == 'uniform':
        return rng.uniform(-1.0, 1.0, N)
    elif dist_type == 'cauchy':
        w = rng.standard_cauchy(N) * 0.5
        return np.clip(w, -4.0, 4.0)
    elif dist_type == 'bimodal':
        omega0 = 1.0
        sigma = 0.3
        half = N // 2
        w = np.empty(N)
        w[:half] = rng.normal(omega0, sigma, half)
        w[half:] = rng.normal(-omega0, sigma, N - half)
        return w
    else:
        raise ValueError(f"Unknown distribution: {dist_type}")


def step_kuramoto(theta, omega, K, alpha, dt):
    """One forward-Euler step of explosive Kuramoto.
    dθ_i/dt = ω_i + K_eff * (1/N) Σ_j sin(θ_j - θ_i),  K_eff = K * R^alpha
    Mean-field: R e^{iψ} = (1/N) Σ e^{iθ_j}
    → dθ_i = ω_i + K_eff * (Ry*cos θ_i - Rx*sin θ_i)
    """
    c = np.cos(theta)
    s = np.sin(theta)
    Rx = c.mean()
    Ry = s.mean()
    R = np.sqrt(Rx * Rx + Ry * Ry)
    K_eff = K * (R + 1e-12) ** alpha
    dtheta = omega + K_eff * (Ry * c - Rx * s)
    theta = theta + dtheta * dt
    theta = np.mod(theta + np.pi, 2 * np.pi) - np.pi
    return theta, R


def adiabatic_sweep(N, K_vals, omega, alpha, dt, n_relax, n_measure,
                     direction='forward', init_theta=None):
    """Adiabatic sweep through K values. Returns R_curve and final theta."""
    if init_theta is not None:
        theta = init_theta.copy()
    else:
        theta = np.random.uniform(-np.pi, np.pi, N)
    R_curve = np.empty(len(K_vals))
    K_sweep = K_vals if direction == 'forward' else K_vals[::-1]
    for i, K in enumerate(K_sweep):
        for _ in range(n_relax):
            theta, R = step_kuramoto(theta, omega, K, alpha, dt)
        R_sum = 0.0
        for _ in range(n_measure):
            theta, R = step_kuramoto(theta, omega, K, alpha, dt)
            R_sum += R
        R_curve[i] = R_sum / n_measure
    if direction == 'backward':
        R_curve = R_curve[::-1]
    return R_curve, theta


def compute_hysteresis_width(K_vals, R_fwd, R_bwd):
    """Compute hysteresis loop width as area between forward and backward curves,
    and also the K-range where |R_fwd - R_bwd| > threshold."""
    R_fwd = np.array(R_fwd)
    R_bwd = np.array(R_bwd)
    # Area between curves (normalized by K range)
    area = np.trapz(np.abs(R_fwd - R_bwd), K_vals)
    # K-width where difference > 0.1
    diff = np.abs(R_fwd - R_bwd)
    mask = diff > 0.1
    if mask.sum() > 1:
        K_width = K_vals[mask].max() - K_vals[mask].min()
    else:
        K_width = 0.0
    return area, K_width


# ── Main Sweep ──
results = {}
t0 = time.time()

for dist_type in dist_names:
    print(f"\n{'='*60}")
    print(f"Distribution: {dist_type}")
    print(f"{'='*60}")
    results[dist_type] = {}

    for N in N_list:
        R_fwd_all = np.zeros(len(K_values))
        R_bwd_all = np.zeros(len(K_values))
        hyst_areas = []
        hyst_widths = []

        for trial in range(n_trials):
            rng = np.random.RandomState(42 + trial * 1000 + N)
            omega = sample_frequencies(N, dist_type, rng)

            # Forward sweep: K low → high (start from disordered state)
            init_fwd = np.random.RandomState(42 + trial * 1000 + N + 999).uniform(-np.pi, np.pi, N)
            R_fwd, theta_end = adiabatic_sweep(
                N, K_values, omega, alpha_exp, dt, n_relax, n_measure,
                direction='forward', init_theta=init_fwd)

            # Backward sweep: K high → low (start from synchronized state = end of forward)
            R_bwd, _ = adiabatic_sweep(
                N, K_values, omega, alpha_exp, dt, n_relax, n_measure,
                direction='backward', init_theta=theta_end)

            R_fwd_all += R_fwd
            R_bwd_all += R_bwd

            area, width = compute_hysteresis_width(K_values, R_fwd, R_bwd)
            hyst_areas.append(area)
            hyst_widths.append(width)

        R_fwd_avg = R_fwd_all / n_trials
        R_bwd_avg = R_bwd_all / n_trials
        hyst_area_avg = np.mean(hyst_areas)
        hyst_width_avg = np.mean(hyst_widths)

        results[dist_type][N] = {
            'R_fwd': R_fwd_avg.tolist(),
            'R_bwd': R_bwd_avg.tolist(),
            'hyst_area': float(hyst_area_avg),
            'hyst_width': float(hyst_width_avg),
        }

        print(f"  N={N:5d} | hyst_area={hyst_area_avg:.4f} | "
              f"ΔK_hyst={hyst_width_avg:.4f} | "
              f"R_fwd_max={R_fwd_avg.max():.3f} | "
              f"elapsed={time.time()-t0:.1f}s")

# ── Hysteresis Width Finite-Size Scaling ──
print(f"\n{'='*60}")
print("HYSTERESIS WIDTH FINITE-SIZE SCALING")
print(f"{'='*60}")

scaling_results = {}
for dist_type in dist_names:
    N_arr = np.array(N_list, dtype=float)
    width_arr = np.array([results[dist_type][N]['hyst_width'] for N in N_list])
    area_arr = np.array([results[dist_type][N]['hyst_area'] for N in N_list])

    # Filter zero/negative values for log fit
    valid = width_arr > 0.01
    if valid.sum() >= 2:
        log_N = np.log10(N_arr[valid])
        log_w = np.log10(width_arr[valid])
        coeff = np.polyfit(log_N, log_w, 1)
        nu_width = coeff[0]  # exponent: ΔK_hyst ~ N^nu
    else:
        nu_width = 0.0
        coeff = [0, 0]

    scaling_results[dist_type] = {
        'nu_width': float(nu_width),
        'widths': width_arr.tolist(),
        'areas': area_arr.tolist(),
    }
    print(f"  {dist_type:10s} | ΔK_hyst(N) ~ N^{nu_width:.3f}")
    print(f"               widths: {width_arr}")

# ── Save JSON ──
summary = {
    "phase": "II_explosive_hysteresis",
    "alpha_exp": alpha_exp,
    "N_list": N_list,
    "K_range": [K_values[0], K_values[-1]],
    "distributions": dist_names,
    "scaling_results": scaling_results,
    "results": {dist: {str(N): results[dist][N] for N in N_list}
                for dist in dist_names},
}
with open('kuramoto_explosive_phase2_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

# ── Plot: Multi-panel figure ──
fig, axes = plt.subplots(2, 3, figsize=(18, 11), dpi=150)
fig.suptitle('Kuramoto Explosive Synchronization — Phase II\n'
             'Hysteresis & Heavy-Tailed Disorder Scaling ($K_{eff}=K \\cdot R^{\\alpha}$, $\\alpha=1$)\n'
             'InvariantMind-v1 (Theory) × GLM 5.2 (Simulation) — Expedition 2026',
             fontsize=13, fontweight='bold')

dist_colors = {'uniform': '#2196F3', 'cauchy': '#FF5722', 'bimodal': '#4CAF50'}

# ── Row 1: Hysteresis loops R(K) for each distribution (at largest N) ──
for j, dist_type in enumerate(dist_names):
    ax = axes[0, j]
    for i, N in enumerate(N_list):
        fwd = results[dist_type][N]['R_fwd']
        bwd = results[dist_type][N]['R_bwd']
        color = plt.cm.viridis(i / (len(N_list) - 1))
        ax.plot(K_values, fwd, '-', lw=1.5, color=color, alpha=0.8, label=f'N={N} fwd')
        ax.plot(K_values, bwd, '--', lw=1.5, color=color, alpha=0.8, label=f'N={N} bwd')
    ax.set_xlabel('Coupling K')
    ax.set_ylabel('$\\langle R \\rangle$')
    ax.set_title(f'({chr(97+j)}) Hysteresis: {dist_type}')
    ax.legend(fontsize=6, ncol=2, loc='upper left')
    ax.grid(True, alpha=0.3)

# ── Row 2: Finite-size scaling of hysteresis width ──
# (d) ΔK_hyst vs N — all distributions
ax = axes[1, 0]
for dist_type in dist_names:
    widths = scaling_results[dist_type]['widths']
    N_arr = np.array(N_list, dtype=float)
    ax.loglog(N_arr, widths, 'o-', ms=8, lw=2,
              color=dist_colors[dist_type], label=f'{dist_type}')
    # Fit line
    valid = np.array(widths) > 0.01
    if valid.sum() >= 2:
        log_N = np.log10(N_arr[valid])
        log_w = np.log10(np.array(widths)[valid])
        c = np.polyfit(log_N, log_w, 1)
        N_fit = np.logspace(np.log10(N_arr.min()), np.log10(N_arr.max()), 50)
        ax.loglog(N_fit, 10**c[1] * N_fit**c[0], '--', lw=1.5, alpha=0.5,
                  color=dist_colors[dist_type],
                  label=f'fit: N^{{{c[0]:.2f}}}')
ax.set_xlabel('N')
ax.set_ylabel('$\\Delta K_{hyst}$')
ax.set_title('(d) Hysteresis Width $\\Delta K_{hyst}(N)$')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3, which='both')

# (e) Hysteresis area vs N
ax = axes[1, 1]
for dist_type in dist_names:
    areas = scaling_results[dist_type]['areas']
    ax.loglog(N_arr, areas, 's-', ms=8, lw=2,
              color=dist_colors[dist_type], label=f'{dist_type}')
ax.set_xlabel('N')
ax.set_ylabel('Hysteresis Area')
ax.set_title('(e) Hysteresis Loop Area vs N')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3, which='both')

# (f) Contrast: forward vs backward R at largest N for all distributions
ax = axes[1, 2]
N_show = N_list[-1]
for dist_type in dist_names:
    fwd = results[dist_type][N_show]['R_fwd']
    bwd = results[dist_type][N_show]['R_bwd']
    ax.plot(K_values, fwd, '-', lw=2, color=dist_colors[dist_type],
            label=f'{dist_type} fwd')
    ax.plot(K_values, bwd, '--', lw=2, color=dist_colors[dist_type],
            label=f'{dist_type} bwd')
ax.set_xlabel('Coupling K')
ax.set_ylabel('$\\langle R \\rangle$')
ax.set_title(f'(f) Distribution Comparison (N={N_show})')
ax.legend(fontsize=7)
ax.grid(True, alpha=0.3)

plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig('kuramoto_explosive_fss_phase2.png', dpi=150, bbox_inches='tight')
print(f"\nSaved: kuramoto_explosive_fss_phase2.png, kuramoto_explosive_phase2_summary.json")
print(f"Total elapsed: {time.time()-t0:.1f}s")
