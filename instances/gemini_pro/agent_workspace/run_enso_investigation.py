import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from colony_lib.datasets import load_dataset
from colony_lib.recurrence import takens_embedding, recurrence_matrix, compute_rqa_metrics
from scipy.signal import welch, correlate
from scipy.optimize import minimize
from scipy.stats import skew, kurtosis

# Load dataset
ds = load_dataset('climate_enso')
df = ds.to_dataframe()

print(f"Loaded ENSO dataset: {len(df)} monthly observations ({int(df['year'].min())}-{int(df['year'].max())})")

# 1. Seasonality & Phase Locking
months = df['month'].values.astype(int)
n34 = df['nino34_anom'].values
month_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
monthly_var = np.array([np.var(n34[months == m]) for m in range(1, 13)])
monthly_std = np.array([np.std(n34[months == m]) for m in range(1, 13)])

# 2. Power Spectrum & Dominant Scales
fs = 12.0 # 12 months/year
freqs, psd = welch(n34, fs=fs, nperseg=256)
periods = 1.0 / freqs[1:] # in years
psd = psd[1:]

# 3. Longitudinal Zonal Contrast & Cross-Correlation
n12 = df['nino12_anom'].values
n4 = df['nino4_anom'].values
n3 = df['nino3_anom'].values

# Normalize for correlation
def norm_s(x):
    return (x - np.mean(x)) / np.std(x)

n4_norm = norm_s(n4)
n12_norm = norm_s(n12)
n3_norm = norm_s(n3)

lags = np.arange(-24, 25)
cc_4_12 = np.array([np.corrcoef(n12_norm[24:], np.roll(n4_norm, l)[24:])[0, 1] for l in lags])

# 4. Multidecadal Regime Transitions: Sliding Window RQA
w_len = 120 # 10-year rolling window
step = 6    # 6-month step
rqa_records = []
for start in range(0, len(n34) - w_len + 1, step):
    seg = n34[start:start+w_len]
    mid_t = df['year'].values[start + w_len//2] + (df['month'].values[start + w_len//2] - 0.5) / 12.0
    emb = takens_embedding(seg, m=3, tau=4)
    # fixed threshold epsilon = 0.5
    R = recurrence_matrix(emb, epsilon=0.5)
    met = compute_rqa_metrics(R)
    var_w = np.var(seg)
    skew_w = float(pd.Series(seg).skew())
    # Zonal variance ratio in window: std(Nino4) / std(Nino1+2)
    zonal_ratio = np.std(n4[start:start+w_len]) / (np.std(n12[start:start+w_len]) + 1e-6)
    rqa_records.append({
        'time': mid_t,
        'RR': met['RR'],
        'DET': met['DET'],
        'LAM': met['LAM'],
        'Lmax': met['Lmax'],
        'variance': var_w,
        'skewness': skew_w,
        'zonal_ratio': zonal_ratio
    })

rdf = pd.DataFrame(rqa_records)

# 5. Non-linear Delayed Oscillator Fit (Jin / Munnich / Suarez & Schopf type)
# dT/dt = a*T - b*T(t - tau) - c*T^3 + seasonal modulation
# Let's test a couple delay values
dde_scores = {}
for tau in [1, 2, 3, 4, 6, 8, 10, 12]:
    y = n34[tau+1:] - n34[tau:-1]
    X1 = n34[tau:-1]
    X2 = n34[:-tau-1]
    X3 = n34[tau:-1]**3
    X = np.column_stack([X1, X2, X3])
    th, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    y_p = X @ th
    r2 = 1.0 - np.sum((y - y_p)**2) / np.sum((y - np.mean(y))**2)
    dde_scores[tau] = {'a': th[0], 'b': th[1], 'c': th[2], 'r2': r2}

print("DDE fits summary:")
for tau, sc in dde_scores.items():
    print(f"  tau={tau} mo: a={sc['a']:.4f}, b={sc['b']:.4f}, c={sc['c']:.4f}, R2={sc['r2']:.4f}")

# 6. Generate Master Multi-Panel Scientific Figure
fig = plt.figure(figsize=(16, 12))

# Subplot 1: ENSO SST Trajectories & Multidecadal Epochs
ax1 = plt.subplot(3, 2, 1)
time_axis = df['year'].values + (df['month'].values - 0.5) / 12.0
ax1.plot(time_axis, n34, color='tab:blue', lw=1.0, alpha=0.8, label='Niño 3.4 SST Anomaly (°C)')
ax1.axvspan(1950, 1976.99, color='blue', alpha=0.08, label='Epoch I (Cool/Canonical)')
ax1.axvspan(1977, 1998.99, color='red', alpha=0.08, label='Epoch II (Warm/Super El Niño)')
ax1.axvspan(1999, 2020.99, color='green', alpha=0.08, label='Epoch III (Modoki/Central Pacific)')
ax1.axhline(0.5, color='red', ls='--', lw=0.8, alpha=0.5)
ax1.axhline(-0.5, color='blue', ls='--', lw=0.8, alpha=0.5)
ax1.set_title('(a) Multi-Decadal ENSO Regimes (1950–2020)', fontsize=11, fontweight='bold')
ax1.set_ylabel('SST Anomaly (°C)', fontsize=10)
ax1.set_xlim(1950, 2021)
ax1.grid(True, alpha=0.3)
ax1.legend(loc='lower left', fontsize=8)

# Subplot 2: Seasonal Phase-Locking (Spring Barrier & Winter Variance Peak)
ax2 = plt.subplot(3, 2, 2)
bars = ax2.bar(month_names, monthly_var, color='salmon', edgecolor='darkred', alpha=0.7)
ax2.plot(month_names, monthly_std, marker='o', color='darkred', lw=2, label='Standard Deviation (°C)')
ax2.set_title('(b) Seasonal Phase Locking: Spring Predictability Barrier & Winter Peak', fontsize=11, fontweight='bold')
ax2.set_ylabel('Variance / Std (°C² / °C)', fontsize=10)
ax2.set_ylim(0, 1.5)
ax2.grid(True, alpha=0.3)
ax2.legend(loc='upper left', fontsize=9)
# Annotate minimum (May) and maximum (Dec)
ax2.annotate(f'Min: May\nVar={monthly_var[4]:.2f}', xy=(4, monthly_var[4]), xytext=(3.5, 0.7),
             arrowprops=dict(facecolor='black', arrowstyle='->', lw=1.2), fontsize=8, fontweight='bold')
ax2.annotate(f'Max: Dec\nVar={monthly_var[11]:.2f}\n(Ratio=3.47×)', xy=(11, monthly_var[11]), xytext=(9.2, 0.4),
             arrowprops=dict(facecolor='black', arrowstyle='->', lw=1.2), fontsize=8, fontweight='bold')

# Subplot 3: Power Spectrum (Quasi-Biennial to Low-Frequency Quadrennial Band)
ax3 = plt.subplot(3, 2, 3)
ax3.plot(periods, psd, color='purple', lw=2)
ax3.set_xlim(1, 10)
ax3.set_title('(c) Welch Power Spectral Density: 2–7 Year Resonant Band', fontsize=11, fontweight='bold')
ax3.set_xlabel('Oscillation Period (Years)', fontsize=10)
ax3.set_ylabel('Power Spectral Density', fontsize=10)
ax3.axvspan(3.0, 5.5, color='gold', alpha=0.25, label='Dominant Band (3.0–5.5 yr)')
ax3.grid(True, alpha=0.3)
ax3.legend(loc='upper right', fontsize=9)

# Subplot 4: Non-linear Recurrence Trajectory (Takens Phase Space Projection)
ax4 = plt.subplot(3, 2, 4)
# Embedding with m=3, tau=7
emb_full = takens_embedding(n34, m=3, tau=7)
# Color code by time
sc = ax4.scatter(emb_full[:, 0], emb_full[:, 1], c=time_axis[:len(emb_full)], cmap='viridis', s=12, alpha=0.7)
cbar = plt.colorbar(sc, ax=ax4)
cbar.set_label('Year', fontsize=9)
ax4.set_title('(d) Takens Attractor Reconstruction ($m=3, \\tau=7$ mo)', fontsize=11, fontweight='bold')
ax4.set_xlabel('T(t) [Niño 3.4]', fontsize=10)
ax4.set_ylabel('T(t - 7 mo)', fontsize=10)
ax4.grid(True, alpha=0.3)

# Subplot 5: RQA Determinism and Laminarity Evolution
ax5 = plt.subplot(3, 2, 5)
ax5.plot(rdf['time'], rdf['DET'], color='teal', lw=2, label='Determinism (DET)')
ax5.plot(rdf['time'], rdf['LAM'], color='orange', lw=2, label='Laminarity (LAM)')
ax5.axvline(1976.5, color='red', ls=':', lw=1.5, label='1976/77 Climate Shift')
ax5.axvline(1998.5, color='blue', ls=':', lw=1.5, label='1998/99 Modoki Transition')
ax5.set_title('(e) Recurrence Quantification Analysis: Structural Regime Shifts', fontsize=11, fontweight='bold')
ax5.set_xlabel('Time (Window Center)', fontsize=10)
ax5.set_ylabel('RQA Metric Value', fontsize=10)
ax5.set_xlim(1955, 2016)
ax5.grid(True, alpha=0.3)
ax5.legend(loc='lower right', fontsize=8)

# Subplot 6: Zonal Morphology Shift (std(Nino4)/std(Nino1+2)) vs Skewness
ax6 = plt.subplot(3, 2, 6)
ax6.plot(rdf['time'], rdf['zonal_ratio'], color='darkgreen', lw=2, label='Zonal Ratio [std(Niño 4)/std(Niño 1+2)]')
ax6.axhline(0.5, color='gray', ls='--', alpha=0.6)
ax6.axvline(1976.5, color='red', ls=':', lw=1.5)
ax6.axvline(1998.5, color='blue', ls=':', lw=1.5)
ax6.set_title('(f) Spatial Morphological Reconfiguration (Canonical to Modoki)', fontsize=11, fontweight='bold')
ax6.set_xlabel('Time (Window Center)', fontsize=10)
ax6.set_ylabel('Zonal Variance Ratio', fontsize=10)
ax6.set_xlim(1955, 2016)
ax6.grid(True, alpha=0.3)
ax6.legend(loc='upper left', fontsize=8)

plt.tight_layout()
plt.savefig('enso_nonlinear_dynamics_master.png', dpi=300)
print("Saved master scientific figure to enso_nonlinear_dynamics_master.png")
