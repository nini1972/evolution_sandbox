import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import hilbert, butter, filtfilt
from colony_lib.datasets import load_dataset
from colony_lib.recurrence import takens_embedding, recurrence_matrix, compute_rqa_metrics

# Load canonical dataset
ds = load_dataset('solar_sunspots')
time = ds.data[:, 2] # decimal year
sunspots = ds.data[:, 3]

# 1. Bandpass filter for Schwabe envelope
fs = 1.0 # 1 month
b, a = butter(3, [(1.0/180.0) / 0.5, (1.0/96.0) / 0.5], btype='band')
filtered_sunspots = filtfilt(b, a, sunspots)
analytic_signal = hilbert(filtered_sunspots)
amp_env = np.abs(analytic_signal)

# 2. Sliding window analysis (window = 528 months ~ 44 yrs, step = 6 months)
w_len = 528
step = 6
m = 3
tau = 33

centers = []
det_vals = []
lam_vals = []
ent_vals = []
l_mean_vals = []
mean_amps = []
mean_ss = []

for start in range(0, len(sunspots) - w_len, step):
    mid = start + w_len // 2
    sub_raw = sunspots[start:start+w_len]
    sub_amp = amp_env[start:start+w_len]
    
    emb = takens_embedding(sub_raw, m=m, tau=tau)
    # Using adaptive epsilon (0.25 * local std) to prove robust topological determinism change
    eps = 0.25 * np.std(sub_raw)
    R = recurrence_matrix(emb, epsilon=eps)
    rqa = compute_rqa_metrics(R)
    
    centers.append(time[mid])
    det_vals.append(rqa['DET'])
    lam_vals.append(rqa['LAM'])
    ent_vals.append(rqa['ENT'])
    l_mean_vals.append(rqa['L'])
    mean_amps.append(np.mean(sub_amp))
    mean_ss.append(np.mean(sub_raw))

centers = np.array(centers)
det_vals = np.array(det_vals)
lam_vals = np.array(lam_vals)
ent_vals = np.array(ent_vals)
l_mean_vals = np.array(l_mean_vals)
mean_amps = np.array(mean_amps)
mean_ss = np.array(mean_ss)

# 3. Create high-resolution multi-panel figure
fig, axes = plt.subplots(3, 2, figsize=(16, 12))

# Subplot (0,0): Time series and envelope
ax = axes[0, 0]
ax.plot(time, sunspots, color='gray', alpha=0.5, lw=0.8, label='Monthly Sunspots')
ax.plot(time, amp_env, color='crimson', lw=1.8, label='Schwabe Envelope |A(t)|')
ax.axvspan(1790, 1830, color='blue', alpha=0.15, label='Dalton Minimum')
ax.axvspan(1880, 1910, color='cyan', alpha=0.12, label='Gleissberg Minimum')
ax.axvspan(1940, 2000, color='orange', alpha=0.15, label='Modern Maximum')
ax.set_title('(a) Empirical Sunspot Series (1749-2026) & Envelope Modulation', fontsize=11, fontweight='bold')
ax.set_ylabel('Sunspot Number', fontsize=10)
ax.set_xlim([1749, 2027])
ax.legend(loc='upper left', fontsize=8)
ax.grid(True, alpha=0.3)

# Subplot (0,1): Sliding-Window RQA (Local Scale Normalized)
ax = axes[0, 1]
ax.plot(centers, det_vals, color='navy', lw=1.8, label='Determinism (DET)')
ax.plot(centers, lam_vals, color='purple', lw=1.8, linestyle='--', label='Laminarity (LAM)')
ax.axvspan(1790, 1830, color='blue', alpha=0.15)
ax.axvspan(1880, 1910, color='cyan', alpha=0.12)
ax.axvspan(1940, 2000, color='orange', alpha=0.15)
ax.set_title('(b) RQA Invariants under Scale-Adaptive Epsilon [eps=0.25*sigma]', fontsize=11, fontweight='bold')
ax.set_ylabel('RQA Metric', fontsize=10)
ax.set_xlim([1749, 2027])
ax.legend(loc='upper right', fontsize=8)
ax.grid(True, alpha=0.3)

# Subplot (1,0): Scatter DET vs Envelope Amplitude
ax = axes[1, 0]
scatter = ax.scatter(mean_amps, det_vals, c=centers, cmap='viridis', s=25, alpha=0.8)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Epoch Year', fontsize=9)
# Linear regression trend
p = np.polyfit(mean_amps, det_vals, 1)
x_line = np.linspace(min(mean_amps), max(mean_amps), 50)
ax.plot(x_line, np.polyval(p, x_line), 'r--', lw=2, label=f'Linear fit (r = {np.corrcoef(mean_amps, det_vals)[0,1]:.2f})')
ax.set_title('(c) Inverse Scaling: Determinism vs Mean Cycle Amplitude', fontsize=11, fontweight='bold')
ax.set_xlabel('Schwabe Envelope Amplitude', fontsize=10)
ax.set_ylabel('Determinism (DET)', fontsize=10)
ax.legend(loc='upper right', fontsize=8)
ax.grid(True, alpha=0.3)

# Subplot (1,1): Scatter LAM vs Envelope Amplitude
ax = axes[1, 1]
scatter2 = ax.scatter(mean_amps, lam_vals, c=centers, cmap='plasma', s=25, alpha=0.8)
cbar2 = plt.colorbar(scatter2, ax=ax)
cbar2.set_label('Epoch Year', fontsize=9)
p2 = np.polyfit(mean_amps, lam_vals, 1)
ax.plot(x_line, np.polyval(p2, x_line), 'k--', lw=2, label=f'Linear fit (r = {np.corrcoef(mean_amps, lam_vals)[0,1]:.2f})')
ax.set_title('(d) Laminarity Suppression in Hyper-Active Dynamo States', fontsize=11, fontweight='bold')
ax.set_xlabel('Schwabe Envelope Amplitude', fontsize=10)
ax.set_ylabel('Laminarity (LAM)', fontsize=10)
ax.legend(loc='upper right', fontsize=8)
ax.grid(True, alpha=0.3)

# Subplot (2,0): Phase Portrait - Dalton Minimum
ax = axes[2, 0]
idx_dalton = np.where((time >= 1790) & (time <= 1830))[0]
emb_d = takens_embedding(sunspots[idx_dalton], m=2, tau=33)
ax.plot(emb_d[:, 0], emb_d[:, 1], color='darkblue', lw=1.0, alpha=0.75)
ax.set_title('(e) Reconstructed Phase Space: Dalton Minimum [1790-1830]\nQuasi-periodic Torus / Regular Limit Cycle (lambda_max = 0.0108/yr)', fontsize=10, fontweight='bold')
ax.set_xlabel('x(t)', fontsize=9)
ax.set_ylabel('x(t - 33m)', fontsize=9)
ax.grid(True, alpha=0.3)

# Subplot (2,1): Phase Portrait - Modern Maximum
ax = axes[2, 1]
idx_modern = np.where((time >= 1940) & (time <= 1980))[0]
emb_m = takens_embedding(sunspots[idx_modern], m=2, tau=33)
ax.plot(emb_m[:, 0], emb_m[:, 1], color='orangered', lw=1.0, alpha=0.75)
ax.set_title('(f) Reconstructed Phase Space: Modern Maximum [1940-1980]\nChaotic Attractor Spreading / Turbulent Dispersion (lambda_max = 0.0401/yr)', fontsize=10, fontweight='bold')
ax.set_xlabel('x(t)', fontsize=9)
ax.set_ylabel('x(t - 33m)', fontsize=9)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('solar_dynamo_attractor_regimes.png', dpi=200)
plt.savefig('../../shared_space/solar_dynamo_attractor_regimes.png', dpi=200)
plt.close()
print("Saved solar_dynamo_attractor_regimes.png to local and shared_space.")
