import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import periodogram, correlate
from scipy.stats import skew, kurtosis
import json

from colony_lib.datasets import load_dataset
from colony_lib.recurrence import takens_embedding, recurrence_matrix, compute_rqa_metrics

ds = load_dataset('climate_enso')
df = ds.to_dataframe()

time = df['year'].values + (df['month'].values - 0.5) / 12.0
nino34 = df['nino34_anom'].values
nino3 = df['nino3_anom'].values
nino4 = df['nino4_anom'].values
nino12 = df['nino12_anom'].values

dt = 1.0 / 12.0 # years

# 1. Non-Gaussian Tail & Skewness Invariant (El Niño vs La Niña Asymmetry)
# Strong El Niño warm events are much stronger than strong La Niña cold events -> positive skewness
sst_skew = float(skew(nino34))
sst_kurt = float(kurtosis(nino34, fisher=True)) # excess kurtosis
mean_val = float(np.mean(nino34))
std_val = float(np.std(nino34))
max_warm = float(np.max(nino34))
max_cold = float(np.min(nino34))

# 2. Spectral Analysis: Quasi-Periodic Delayed Oscillator
freqs, psd = periodogram(nino34, fs=12.0)
# ENSO band: 2 to 7 years (freq: 1/7 to 1/2 yr^-1)
enso_band = (freqs >= 1.0/7.0) & (freqs <= 1.0/2.0)
peak_f = freqs[enso_band][np.argmax(psd[enso_band])]
dominant_period_years = 1.0 / peak_f

# 3. Autocorrelation & Delay-Oscillator Memory
nino34_norm = (nino34 - mean_val) / std_val
acf = np.correlate(nino34_norm, nino34_norm, mode='full')
acf = acf[len(nino34_norm)-1:] / len(nino34_norm)
acf_lags_months = np.arange(len(acf))

# Decorrelation time (e-folding time)
e_fold_idx = np.where(acf < 1.0/np.e)[0]
decorr_time_months = float(acf_lags_months[e_fold_idx[0]]) if len(e_fold_idx) > 0 else 0.0

# First negative trough (delay oscillator bounceback)
trough_idx = np.where(np.diff(np.sign(np.diff(acf))) > 0)[0]
# first minimum
first_min_lag = float(acf_lags_months[np.argmin(acf[:36])])

# 4. Longitudinal Wave Propagation & Phase Delay (Niño 4 [West] -> Niño 3.4 [Central] -> Niño 1+2 [East])
# Cross-correlation between West (Niño 4) and East (Niño 1+2)
xcorr_w_e = correlate(nino12 - np.mean(nino12), nino4 - np.mean(nino4), mode='full')
lags_months = np.arange(-len(nino4) + 1, len(nino4))
best_lag_we = lags_months[np.argmax(xcorr_w_e)] # ocean wave propagation lag in months

# 5. Attractor Reconstruction & Recurrence Analysis
# Delay embedding for Niño 3.4 (m=3, tau=6 months = 0.5 yr)
embedded = takens_embedding(nino34, m=3, tau=6)
R = recurrence_matrix(embedded, epsilon=0.45)
rqa = compute_rqa_metrics(R)

print(f"ENSO Skewness: {sst_skew:.3f} (Excess Kurtosis: {sst_kurt:.3f})")
print(f"Max Warm: +{max_warm:.2f} C, Max Cold: {max_cold:.2f} C (Ratio: {abs(max_warm/max_cold):.2f})")
print(f"Dominant Periodicity (PSD): {dominant_period_years:.2f} years")
print(f"Decorrelation Time: {decorr_time_months:.1f} months | Negative Trough: {first_min_lag:.1f} months")
print(f"West-to-East Kelvin Wave Propagation Lag: {best_lag_we} months")
print(f"RQA: DET = {rqa['DET']:.4f}, LAM = {rqa['LAM']:.4f}, RR = {rqa['RR']:.4f}, ENT = {rqa['ENT']:.4f}")

# Visualization Figure
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# Subplot 1: Niño 3.4 Anomaly Time Series with El Niño / La Niña Color Fill
axes[0].plot(time, nino34, color='black', lw=0.8, alpha=0.8, label='Niño 3.4 SST Anomaly')
axes[0].fill_between(time, 0, nino34, where=(nino34 >= 0.5), color='#ef4444', alpha=0.6, label='El Niño (> +0.5°C)')
axes[0].fill_between(time, 0, nino34, where=(nino34 <= -0.5), color='#3b82f6', alpha=0.6, label='La Niña (< -0.5°C)')
axes[0].axhline(0, color='gray', ls='--', lw=0.8)
axes[0].axhline(0.5, color='crimson', ls=':', lw=0.8)
axes[0].axhline(-0.5, color='blue', ls=':', lw=0.8)
axes[0].set_ylabel('SST Anomaly (°C)')
axes[0].set_title('Equatorial Pacific El Niño Southern Oscillation (NOAA ERSSTv5 1950–2026)', fontsize=12, fontweight='bold')
axes[0].set_xlim(time[0], time[-1])
axes[0].grid(True, alpha=0.3)
axes[0].legend(loc='upper right', ncol=3, fontsize=9)

# Subplot 2: Power Spectrum & Autocorrelation
ax_sub1 = axes[1]
ax_sub2 = ax_sub1.twinx()

p1 = ax_sub1.plot(1.0 / freqs[freqs > 0], psd[freqs > 0], color='#8b5cf6', lw=1.8, label='Power Spectral Density')
ax_sub1.set_xscale('log')
ax_sub1.set_xlim(0.5, 20)
ax_sub1.set_xlabel('Period (Years)')
ax_sub1.set_ylabel('PSD (°C²/yr)', color='#8b5cf6')
ax_sub1.axvline(dominant_period_years, color='#8b5cf6', ls='--', lw=1.5, label=f'Peak: {dominant_period_years:.2f} yr')

p2 = ax_sub2.plot(acf_lags_months[:60] / 12.0, acf[:60], color='#f59e0b', lw=1.8, label='Autocorrelation $R(\\tau)$')
ax_sub2.axhline(0, color='gray', ls=':', lw=0.8)
ax_sub2.set_ylabel('Autocorrelation', color='#f59e0b')
ax_sub1.set_title(f'Spectral & Autocorrelation Structure: Quasi-Periodicity $T = {dominant_period_years:.2f}\\text{{ yr}}$, $\\tau_{{\\text{{decorr}}}} = {decorr_time_months/12.0:.2f}\\text{{ yr}}$', fontsize=11, fontweight='bold')
ax_sub1.grid(True, alpha=0.3)

# Subplot 3: Phase Space Attractor & Recurrence Matrix
# Left: Takens Delay Embedding [x(t), x(t+tau)], Right: Probability Density (Asymmetry)
axes[2].remove()
gs = fig.add_gridspec(3, 2)
ax_phase = fig.add_subplot(gs[2, 0])
ax_pdf = fig.add_subplot(gs[2, 1])

tau_step = 6 # 6 months
ax_phase.plot(nino34[:-tau_step], nino34[tau_step:], color='#0284c7', lw=0.5, alpha=0.6)
ax_phase.scatter(nino34[:-tau_step:6], nino34[tau_step::6], c=time[:-tau_step:6], cmap='plasma', s=8, alpha=0.7)
ax_phase.set_xlabel('$x(t)$ Niño 3.4 SST Anomaly (°C)')
ax_phase.set_ylabel('$x(t + 6\\text{mo})$ Niño 3.4 SST Anomaly (°C)')
ax_phase.set_title(f'Delay-Embedded Attractor ($\\text{{DET}} = {rqa["DET"]*100:.1f}\\%$)', fontsize=11, fontweight='bold')
ax_phase.grid(True, alpha=0.3)

# PDF showing non-linear skewness
counts, bins, _ = ax_pdf.hist(nino34, bins=40, density=True, color='#64748b', alpha=0.6, label='Empirical SST Dist.')
from scipy.stats import norm
x_norm_fit = np.linspace(bins[0], bins[-1], 200)
ax_pdf.plot(x_norm_fit, norm.pdf(x_norm_fit, mean_val, std_val), 'r--', lw=1.5, label='Gaussian Null')
ax_pdf.axvline(0, color='gray', ls=':', lw=0.8)
ax_pdf.set_xlabel('Niño 3.4 SST Anomaly (°C)')
ax_pdf.set_ylabel('Probability Density')
ax_pdf.set_title(f'Asymmetry Invariant: Skewness = +{sst_skew:.2f} (El Niño > La Niña)', fontsize=11, fontweight='bold')
ax_pdf.grid(True, alpha=0.3)
ax_pdf.legend(loc='upper right', fontsize=8)

plt.tight_layout()
fig.savefig('climate_enso_invariants.png', dpi=200)
print("Saved climate_enso_invariants.png")

# Save JSON Invariants
enso_invariants = {
    "system": "Coupled Atmosphere-Ocean Delayed Oscillator",
    "dataset": "climate_enso",
    "temporal_range_years": [float(time[0]), float(time[-1])],
    "duration_months": len(nino34),
    "dominant_periodicity_years": float(dominant_period_years),
    "decorrelation_time_months": float(decorr_time_months),
    "negative_rebound_lag_months": float(first_min_lag),
    "non_linear_asymmetry": {
        "skewness": float(sst_skew),
        "excess_kurtosis": float(sst_kurt),
        "max_warm_el_nino_celsius": float(max_warm),
        "max_cold_la_nina_celsius": float(max_cold),
        "warm_to_cold_amplitude_ratio": float(abs(max_warm / max_cold))
    },
    "wave_propagation_delay_months": {
        "west_to_east_lag": int(best_lag_we)
    },
    "recurrence_quantification": {
        "embedding_dimension": 3,
        "embedding_delay_months": 6,
        "epsilon": 0.45,
        "determinism_DET": float(rqa['DET']),
        "laminarity_LAM": float(rqa['LAM']),
        "recurrence_rate_RR": float(rqa['RR']),
        "shannon_entropy_ENT": float(rqa['ENT'])
    }
}

with open("climate_enso_invariants.json", "w") as f:
    json.dump(enso_invariants, f, indent=2)

print("Saved climate_enso_invariants.json")
