import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.signal import periodogram
import json

from colony_lib.datasets import load_dataset
from colony_lib.recurrence import takens_embedding, recurrence_matrix, compute_rqa_metrics

ds = load_dataset('climate_temperatures')
df = ds.to_dataframe()

t_days = df["DayIndex"].values; dates = pd.date_range("1981-01-01", periods=len(t_days), freq="D")
temp = df['Temp'].values
N = len(temp)
t_days = np.arange(N)

# 1. Harmonic Orbital Forcing Fit: T(t) = T_0 + A * cos(2*pi*t/365.25 + phi) + trend * t
def orbital_model(t, T0, A, phi, trend):
    return T0 + A * np.cos(2 * np.pi * t / 365.25 + phi) + trend * t

popt, _ = curve_fit(orbital_model, t_days, temp, p0=[np.mean(temp), 5.0, 0.0, 0.0])
T0_fit, A_fit, phi_fit, trend_fit = popt

orbital_cycle = orbital_model(t_days, T0_fit, A_fit, phi_fit, 0.0)
stochastic_residual = temp - orbital_model(t_days, *popt)

res_mean = np.mean(stochastic_residual)
res_std = np.std(stochastic_residual)

# 2. Multiscale Fluctuation & Hurst Exponent (Detrended Fluctuation Analysis - DFA)
def compute_dfa(series, min_scale=10, max_scale=500, num_scales=25):
    scales = np.unique(np.logspace(np.log10(min_scale), np.log10(max_scale), num_scales).astype(int))
    # Profile
    y = np.cumsum(series - np.mean(series))
    F = []
    valid_scales = []
    for s in scales:
        num_windows = len(y) // s
        if num_windows < 2:
            continue
        fluctuations = []
        for i in range(num_windows):
            segment = y[i*s : (i+1)*s]
            x_seg = np.arange(s)
            p = np.polyfit(x_seg, segment, 1)
            fit = np.polyval(p, x_seg)
            fluctuations.append(np.mean((segment - fit)**2))
        F.append(np.sqrt(np.mean(fluctuations)))
        valid_scales.append(s)
    
    valid_scales = np.array(valid_scales)
    F = np.array(F)
    # Fit Hurst / scaling exponent: log(F) = H * log(s) + C
    p_hurst = np.polyfit(np.log10(valid_scales), np.log10(F), 1)
    Hurst = p_hurst[0]
    return valid_scales, F, Hurst

scales, F_scales, H_exponent = compute_dfa(stochastic_residual)

# 3. Autocorrelation & Memory of Weather Fluctuations
res_norm = (stochastic_residual - res_mean) / res_std
acf = np.correlate(res_norm, res_norm, mode='full')
acf = acf[len(res_norm)-1:] / len(res_norm)
acf_lags = np.arange(len(acf))

# Decorrelation e-folding time of turbulent weather residuals
e_fold_days = float(acf_lags[np.where(acf < 1.0/np.e)[0][0]])

# 4. RQA on Weather Residuals
embedded = takens_embedding(stochastic_residual, m=3, tau=2)
R = recurrence_matrix(embedded, epsilon=0.5)
rqa = compute_rqa_metrics(R)

print(f"Orbital Forcing: Mean T0 = {T0_fit:.2f} C, Seasonal Amplitude A = {A_fit:.2f} C")
print(f"Annual Trend: {trend_fit * 365.25 * 10:.2f} C / decade")
print(f"Stochastic Residual Std: {res_std:.2f} C")
print(f"Weather Memory Decorrelation Time: {e_fold_days:.1f} days")
print(f"Turbulent Fluctuation Hurst Exponent: H = {H_exponent:.3f} (Long-range memory if H > 0.5)")
print(f"RQA Residuals: DET = {rqa['DET']:.4f}, LAM = {rqa['LAM']:.4f}, RR = {rqa['RR']:.4f}")

# Visualization Figure
fig, axes = plt.subplots(3, 1, figsize=(12, 11))

# Subplot 1: Raw Daily Temperature & Orbital Decomposition
axes[0].plot(dates, temp, color='#94a3b8', lw=0.7, alpha=0.7, label='Raw Daily Min Temp')
axes[0].plot(dates, orbital_model(t_days, *popt), color='#ef4444', lw=2.0, label=f'Orbital Harmonic Fit ($A={A_fit:.2f}^\\circ\\text{{C}}$, $T_0={T0_fit:.2f}^\\circ\\text{{C}}$)')
axes[0].set_ylabel('Temperature (°C)')
axes[0].set_title('Atmospheric Boundary Layer Dynamics (Melbourne Station, 1981–1990)', fontsize=12, fontweight='bold')
axes[0].set_xlim(dates[0], dates[-1])
axes[0].grid(True, alpha=0.3)
axes[0].legend(loc='upper right', fontsize=9)

# Subplot 2: Stochastic Weather Residuals
axes[1].plot(dates, stochastic_residual, color='#0284c7', lw=0.8, alpha=0.8, label=f'Detrended Weather Residuals ($\\sigma={res_std:.2f}^\\circ\\text{{C}}$)')
axes[1].axhline(0, color='gray', ls='--', lw=0.8)
axes[1].axhline(2*res_std, color='crimson', ls=':', lw=0.8, label='$\\pm 2\\sigma$ Fluctuation')
axes[1].axhline(-2*res_std, color='crimson', ls=':', lw=0.8)
axes[1].set_ylabel('Residual (°C)')
axes[1].set_title(f'Stochastic Turbulent Weather Fluctuations: Decorrelation $\\tau_e = {e_fold_days:.1f}\\text{{ days}}$', fontsize=11, fontweight='bold')
axes[1].set_xlim(dates[0], dates[-1])
axes[1].grid(True, alpha=0.3)
axes[1].legend(loc='upper right', fontsize=9)

# Subplot 3: DFA Scaling Law (Hurst Exponent) & Autocorrelation
axes[2].remove()
gs = fig.add_gridspec(3, 2)
ax_dfa = fig.add_subplot(gs[2, 0])
ax_acf = fig.add_subplot(gs[2, 1])

ax_dfa.loglog(scales, F_scales, 'o', color='#8b5cf6', markersize=5, label='DFA $F(s)$')
fit_F = 10**(np.polyval([H_exponent, np.polyfit(np.log10(scales), np.log10(F_scales), 1)[1]], np.log10(scales)))
ax_dfa.loglog(scales, fit_F, 'r--', lw=1.8, label=f'Scaling Fit: $H = {H_exponent:.3f}$')
ax_dfa.set_xlabel('Scale $s$ (Days)')
ax_dfa.set_ylabel('Fluctuation $F(s)$')
ax_dfa.set_title(f'Detrended Fluctuation Analysis (Hurst $H = {H_exponent:.3f}$)', fontsize=11, fontweight='bold')
ax_dfa.grid(True, alpha=0.3)
ax_dfa.legend(loc='lower right', fontsize=8)

ax_acf.plot(acf_lags[:40], acf[:40], color='#10b981', lw=1.8, marker='d', markersize=3)
ax_acf.axhline(1.0/np.e, color='#ef4444', ls='--', lw=1.2, label=f'1/e Threshold ($\\tau_e = {e_fold_days:.1f}$ d)')
ax_acf.axhline(0, color='gray', ls=':', lw=0.8)
ax_acf.set_xlabel('Lag $\\tau$ (Days)')
ax_acf.set_ylabel('Autocorrelation $R(\\tau)$')
ax_acf.set_title('Weather Memory Autocorrelation Decay', fontsize=11, fontweight='bold')
ax_acf.grid(True, alpha=0.3)
ax_acf.legend(loc='upper right', fontsize=8)

plt.tight_layout()
fig.savefig('climate_temperatures_invariants.png', dpi=200)
print("Saved climate_temperatures_invariants.png")

# Save Invariants JSON
temp_invariants = {
    "system": "Atmospheric Planetary Boundary Layer Dynamics",
    "dataset": "climate_temperatures",
    "temporal_range_dates": [str(dates[0].date()), str(dates[-1].date())],
    "duration_days": N,
    "orbital_harmonic_forcing": {
        "mean_baseline_celsius": float(T0_fit),
        "seasonal_amplitude_celsius": float(A_fit),
        "phase_radians": float(phi_fit),
        "linear_trend_celsius_per_decade": float(trend_fit * 365.25 * 10.0)
    },
    "turbulent_weather_stochastics": {
        "residual_std_celsius": float(res_std),
        "decorrelation_time_days": float(e_fold_days),
        "hurst_exponent_dfa": float(H_exponent),
        "scaling_regime": "Persistent long-range memory" if H_exponent > 0.5 else "Sub-diffusive / mean-reverting"
    },
    "recurrence_quantification": {
        "embedding_dimension": 3,
        "embedding_delay_days": 2,
        "epsilon": 0.5,
        "determinism_DET": float(rqa['DET']),
        "laminarity_LAM": float(rqa['LAM']),
        "recurrence_rate_RR": float(rqa['RR']),
        "shannon_entropy_ENT": float(rqa['ENT'])
    }
}

with open("climate_temperatures_invariants.json", "w") as f:
    json.dump(temp_invariants, f, indent=2)

print("Saved climate_temperatures_invariants.json")
