import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from colony_lib.datasets import load_dataset
from colony_lib.recurrence import takens_embedding, recurrence_matrix, compute_rqa_metrics
from scipy.signal import hilbert, butter, filtfilt

ds = load_dataset('solar_sunspots')
time = ds.data[:, 2] # decimal year
sunspots = ds.data[:, 3]

# 1. Bandpass filter around 11-year cycle to extract instantaneous phase and amplitude
# Sampling frequency: fs = 12 samples/year = 1 sample/month
# Schwabe cycle: 9 to 14 years -> periods 108 to 168 months
# Frequencies: 1/168 to 1/108 cycles/month = 0.00595 to 0.00926
fs = 1.0 # 1 sample per month
f_low = 1.0 / 180.0
f_high = 1.0 / 96.0

b, a = butter(3, [f_low / (0.5 * fs), f_high / (0.5 * fs)], btype='band')
filtered_sunspots = filtfilt(b, a, sunspots)

analytic_signal = hilbert(filtered_sunspots)
amplitude_envelope = np.abs(analytic_signal)
instantaneous_phase = np.unwrap(np.angle(analytic_signal))

# 2. Windowed RQA across historical solar epochs
# Windows of 44 years (528 months) with step of 6 months
w_len = 528
step = 6
m = 3
tau = 33

window_centers = []
det_list = []
lam_list = []
ent_list = []
rr_list = []
mean_amp_list = []
mean_ss_list = []

eps = 0.25 * np.std(sunspots)

for start in range(0, len(sunspots) - w_len, step):
    mid_idx = start + w_len // 2
    sub_raw = sunspots[start:start+w_len]
    sub_amp = amplitude_envelope[start:start+w_len]
    
    emb = takens_embedding(sub_raw, m=m, tau=tau)
    R = recurrence_matrix(emb, epsilon=eps)
    rqa = compute_rqa_metrics(R)
    
    window_centers.append(time[mid_idx])
    det_list.append(rqa['DET'])
    lam_list.append(rqa['LAM'])
    ent_list.append(rqa['ENT'])
    rr_list.append(rqa['RR'])
    mean_amp_list.append(np.mean(sub_amp))
    mean_ss_list.append(np.mean(sub_raw))

window_centers = np.array(window_centers)
det_arr = np.array(det_list)
lam_arr = np.array(lam_list)
ent_arr = np.array(ent_list)
mean_amp_arr = np.array(mean_amp_list)
mean_ss_arr = np.array(mean_ss_list)

corr_amp_det = np.corrcoef(mean_amp_arr, det_arr)[0, 1]
corr_amp_lam = np.corrcoef(mean_amp_arr, lam_arr)[0, 1]
print(f"Correlation between Mean Cycle Amplitude and Determinism (DET): {corr_amp_det:.4f}")
print(f"Correlation between Mean Cycle Amplitude and Laminarity (LAM): {corr_amp_lam:.4f}")

# Plotting comprehensive figure
fig = plt.figure(figsize=(14, 10))

# Subplot 1: Raw series & Envelope
ax1 = plt.subplot(3, 1, 1)
ax1.plot(time, sunspots, color='black', alpha=0.35, lw=0.7, label='Monthly Sunspot Number')
ax1.plot(time, amplitude_envelope, color='crimson', lw=1.5, label='Schwabe Envelope |A(t)|')
ax1.axvspan(1790, 1830, color='blue', alpha=0.15, label='Dalton Minimum (~1790-1830)')
ax1.axvspan(1880, 1910, color='cyan', alpha=0.12, label='Gleissberg Minimum (~1880-1910)')
ax1.axvspan(1940, 2000, color='orange', alpha=0.15, label='Modern Maximum (~1940-2000)')
ax1.set_xlim([time[0], time[-1]])
ax1.set_ylabel('Sunspot Number / Amplitude', fontsize=11)
ax1.set_title('300-Year Solar Dynamo Cycle: Amplitude Modulation and Recurrence Transitions', fontsize=13, fontweight='bold')
ax1.legend(loc='upper left', frameon=True, fontsize=9)
ax1.grid(True, alpha=0.3)

# Subplot 2: RQA Determinism and Laminarity
ax2 = plt.subplot(3, 1, 2, sharex=ax1)
ax2.plot(window_centers, det_arr, color='navy', lw=2.0, label='Determinism (DET)')
ax2.plot(window_centers, lam_arr, color='purple', lw=2.0, linestyle='--', label='Laminarity (LAM)')
ax2.axvspan(1790, 1830, color='blue', alpha=0.15)
ax2.axvspan(1880, 1910, color='cyan', alpha=0.12)
ax2.axvspan(1940, 2000, color='orange', alpha=0.15)
ax2.set_ylabel('RQA Metric Value', fontsize=11)
ax2.set_title('Nonlinear Recurrence Dynamics: Determinism (DET) and Laminarity (LAM) [m=3, tau=33m]', fontsize=11)
ax2.legend(loc='upper right', frameon=True, fontsize=9)
ax2.grid(True, alpha=0.3)

# Subplot 3: Phase Space Attractor Projection in 2 Epochs (Dalton vs Modern Max)
# Let's split subplot 3 into two sub-panels
ax3a = plt.subplot(3, 2, 5)
idx_dalton = np.where((time >= 1790) & (time <= 1830))[0]
emb_dalton = takens_embedding(sunspots[idx_dalton], m=2, tau=33)
ax3a.plot(emb_dalton[:, 0], emb_dalton[:, 1], color='navy', alpha=0.7, lw=0.8)
ax3a.set_title('Dalton Minimum Phase Portrait [1790-1830]\nHigh Regularity / Quasi-periodic limit cycle', fontsize=10)
ax3a.set_xlabel('x(t)', fontsize=9)
ax3a.set_ylabel('x(t - 33m)', fontsize=9)
ax3a.grid(True, alpha=0.3)

ax3b = plt.subplot(3, 2, 6)
idx_modern = np.where((time >= 1940) & (time <= 1980))[0]
emb_modern = takens_embedding(sunspots[idx_modern], m=2, tau=33)
ax3b.plot(emb_modern[:, 0], emb_modern[:, 1], color='orangered', alpha=0.7, lw=0.8)
ax3b.set_title('Modern Maximum Phase Portrait [1940-1980]\nLow Regularity / Turbulent attractor spreading', fontsize=10)
ax3b.set_xlabel('x(t)', fontsize=9)
ax3b.set_ylabel('x(t - 33m)', fontsize=9)
ax3b.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('solar_dynamo_rqa_transition.png', dpi=200)
plt.close()
print("Saved solar_dynamo_rqa_transition.png")
