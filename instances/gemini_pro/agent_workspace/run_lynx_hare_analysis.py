import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, correlate
from scipy.optimize import minimize
import json

from colony_lib.datasets import load_dataset
from colony_lib.recurrence import recurrence_matrix, compute_rqa_metrics

ds = load_dataset('lynx_hare')
df = ds.to_dataframe()

year = df['year'].values
hare = df['hare'].values
lynx = df['lynx'].values

dt = 1.0 # 1 year

# 1. Peak-to-Peak Analysis
hare_peaks, _ = find_peaks(hare, distance=5, prominence=15)
lynx_peaks, _ = find_peaks(lynx, distance=5, prominence=15)

hare_peak_years = year[hare_peaks] # [1903, 1913]
lynx_peak_years = year[lynx_peaks] # [1904, 1915]

hare_period = np.diff(hare_peak_years)[0] # 10.0 years
lynx_period = np.diff(lynx_peak_years)[0] # 11.0 years
mean_period = 0.5 * (hare_period + lynx_period) # 10.5 years

# Trophic Delays:
# Hare peak 1903 -> Lynx peak 1904 (lag = 1.0 yr)
# Hare peak 1913 -> Lynx peak 1915 (lag = 2.0 yr)
delays = lynx_peak_years - hare_peak_years
mean_trophic_delay = float(np.mean(delays))

# Cross-correlation lag
hare_norm = (hare - np.mean(hare)) / np.std(hare)
lynx_norm = (lynx - np.mean(lynx)) / np.std(lynx)
xcorr = correlate(lynx_norm, hare_norm, mode='full')
lags = np.arange(-len(hare) + 1, len(hare)) * dt
pos_mask = (lags >= 0) & (lags <= 5)
best_xcorr_lag = lags[pos_mask][np.argmax(xcorr[pos_mask])]

# Phase shift in radians: phi = 2*pi * (delay / period)
phase_lag_rad = 2 * np.pi * (mean_trophic_delay / mean_period)

# 2. Vector Field & Lotka-Volterra Parameter Identification
# dx/dt = alpha*x - beta*x*y
# dy/dt = delta*x*y - gamma*y
# Central differences for derivatives
dx_dt = (hare[2:] - hare[:-2]) / (2 * dt)
dy_dt = (lynx[2:] - lynx[:-2]) / (2 * dt)
x_mid = hare[1:-1]
y_mid = lynx[1:-1]

# Fit Lotka-Volterra parameters via linear least squares
# dx/dt = alpha*x - beta*x*y  =>  (1/x)*dx/dt = alpha - beta*y
A_x = np.column_stack([np.ones_like(y_mid), -y_mid])
b_x = dx_dt / x_mid
params_x, _, _, _ = np.linalg.lstsq(A_x, b_x, rcond=None)
alpha, beta = params_x[0], params_x[1]

# dy/dt = delta*x*y - gamma*y  =>  (1/y)*dy/dt = delta*x - gamma = -gamma + delta*x
A_y = np.column_stack([-np.ones_like(x_mid), x_mid])
b_y = dy_dt / y_mid
params_y, _, _, _ = np.linalg.lstsq(A_y, b_y, rcond=None)
gamma, delta = params_y[0], params_y[1]

# Theoretical fixed point (center of limit cycles):
x_star = gamma / delta if delta > 0 else 0
y_star = alpha / beta if beta > 0 else 0
# Small oscillation frequency around center: omega = sqrt(alpha * gamma)
omega_theory = np.sqrt(abs(alpha * gamma))
period_theory = 2 * np.pi / omega_theory if omega_theory > 0 else 0

# 3. Limit Cycle Circulation & Recurrence Analysis
state_2d = np.column_stack([hare_norm, lynx_norm])
R = recurrence_matrix(state_2d, epsilon=0.55)
rqa = compute_rqa_metrics(R)

print(f"Cycle Periods: Hare = {hare_period:.1f} yr, Lynx = {lynx_period:.1f} yr, Mean = {mean_period:.1f} yr")
print(f"Trophic Phase Delay: Mean = {mean_trophic_delay:.1f} yr ({np.degrees(phase_lag_rad):.1f} deg)")
print(f"Fitted Lotka-Volterra: alpha = {alpha:.3f}, beta = {beta:.4f}, gamma = {gamma:.3f}, delta = {delta:.4f}")
print(f"Theoretical Center: (Hare* = {x_star:.1f}, Lynx* = {y_star:.1f}), T_linear = {period_theory:.1f} yr")
print(f"RQA: DET = {rqa['DET']:.4f}, LAM = {rqa['LAM']:.4f}, RR = {rqa['RR']:.4f}")

# Visualization Figure
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Subplot (0,0): Time Series
axes[0,0].plot(year, hare, color='#10b981', lw=2.2, marker='o', markersize=4, label='Snowshoe Hare ($x$)')
axes[0,0].plot(year, lynx, color='#ef4444', lw=2.2, marker='s', markersize=4, label='Canadian Lynx ($y$)')
axes[0,0].plot(hare_peak_years, hare[hare_peaks], 'g^', markersize=9, label='Hare Peaks (1903, 1913)')
axes[0,0].plot(lynx_peak_years, lynx[lynx_peaks], 'rv', markersize=9, label='Lynx Peaks (1904, 1915)')
axes[0,0].set_xlabel('Year')
axes[0,0].set_ylabel('Population Proxy (Thousands)')
axes[0,0].set_title('Predator-Prey Oscillations (1900–1920)', fontweight='bold')
axes[0,0].grid(True, alpha=0.3)
axes[0,0].legend(loc='upper right', fontsize=8)

# Subplot (0,1): Cross-Correlation & Phase Lag
axes[0,1].plot(lags, xcorr / np.max(xcorr), color='#6366f1', lw=2, marker='d', markersize=4)
axes[0,1].axvline(best_xcorr_lag, color='#ef4444', ls='--', lw=1.5, label=f'Peak Lag = {best_xcorr_lag:.1f} yr')
axes[0,1].axvline(0, color='gray', ls=':', alpha=0.6)
axes[0,1].set_xlabel('Lag $\\tau$ (Years)')
axes[0,1].set_ylabel('Cross-Correlation $R_{LH}(\\tau)$')
axes[0,1].set_title(f'Trophic Phase Delay: $\\Delta t = {mean_trophic_delay:.1f}\\text{{ yr}}$ (${np.degrees(phase_lag_rad):.1f}^\\circ$)', fontweight='bold')
axes[0,1].grid(True, alpha=0.3)
axes[0,1].legend(loc='upper right', fontsize=8)

# Subplot (1,0): Phase Plane Orbit & Fitted Center
axes[1,0].plot(hare, lynx, color='#8b5cf6', lw=1.5, alpha=0.7)
axes[1,0].scatter(hare, lynx, c=year, cmap='viridis', s=45, zorder=4)
axes[1,0].scatter([x_star], [y_star], color='crimson', marker='X', s=100, zorder=6, label=f'Center ({x_star:.1f}, {y_star:.1f})')
for i in range(len(hare)-1):
    axes[1,0].annotate('', xy=(hare[i+1], lynx[i+1]), xytext=(hare[i], lynx[i]),
                      arrowprops=dict(arrowstyle="->", color='#8b5cf6', lw=1.0, mutation_scale=9))
axes[1,0].set_xlabel('Hare Population ($x$)')
axes[1,0].set_ylabel('Lynx Population ($y$)')
axes[1,0].set_title('Phase Plane Limit Cycle Orbit', fontweight='bold')
axes[1,0].grid(True, alpha=0.3)
axes[1,0].legend(loc='upper right', fontsize=8)

# Subplot (1,1): Recurrence Matrix Plot
axes[1,1].imshow(R, cmap='binary', origin='lower')
axes[1,1].set_xlabel('Year Index')
axes[1,1].set_ylabel('Year Index')
axes[1,1].set_title(f'Recurrence Matrix ($\\text{{DET}}={rqa["DET"]*100:.1f}\\%$, $\\text{{RR}}={rqa["RR"]*100:.1f}\\%$)', fontweight='bold')

plt.tight_layout()
fig.savefig('lynx_hare_ecological_invariants.png', dpi=200)
print("Saved lynx_hare_ecological_invariants.png")

# Save Invariant JSON
eco_invariants = {
    "system": "Ecological Predator-Prey Interaction (Hudson's Bay)",
    "dataset": "lynx_hare",
    "temporal_range_years": [int(year[0]), int(year[-1])],
    "duration_years": int(year[-1] - year[0]),
    "cycle_periodicity_years": {
        "hare_period": float(hare_period),
        "lynx_period": float(lynx_period),
        "mean_period": float(mean_period)
    },
    "trophic_delay_invariants": {
        "mean_trophic_delay_years": float(mean_trophic_delay),
        "phase_lag_degrees": float(np.degrees(phase_lag_rad)),
        "phase_fraction_of_cycle": float(mean_trophic_delay / mean_period)
    },
    "lotka_volterra_parameters": {
        "alpha_prey_growth": float(alpha),
        "beta_predation_rate": float(beta),
        "gamma_predator_death": float(gamma),
        "delta_conversion_efficiency": float(delta),
        "theoretical_center": {"hare_star": float(x_star), "lynx_star": float(y_star)},
        "theoretical_period_years": float(period_theory)
    },
    "recurrence_quantification": {
        "epsilon": 0.55,
        "determinism_DET": float(rqa['DET']),
        "laminarity_LAM": float(rqa['LAM']),
        "recurrence_rate_RR": float(rqa['RR']),
        "shannon_entropy_ENT": float(rqa['ENT'])
    }
}

with open("lynx_hare_invariants.json", "w") as f:
    json.dump(eco_invariants, f, indent=2)

print("Saved lynx_hare_invariants.json")
