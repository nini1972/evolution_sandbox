import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import butter, sosfiltfilt, hilbert, welch

from colony_lib.datasets import load_dataset
from colony_lib.recurrence import takens_embedding, recurrence_matrix, compute_rqa_metrics

ds = load_dataset('neural_eeg')
df = ds.to_dataframe()

channels = ['AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1', 'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4']
fs = 128.0
time = np.arange(len(df)) / fs

data = df[channels].values
eye_state = df['eyeDetection'].values

# Baseline clean: clip extreme voltage artifacts beyond 1st-99th percentile or robust scale
p1, p99 = np.percentile(data, [1, 99], axis=0)
clipped_data = np.clip(data, p1 - 2*(p99-p1), p99 + 2*(p99-p1))

# Bandpass filters for canonical neural rhythms:
# Theta (4-8 Hz), Alpha (8-12 Hz), Beta (13-30 Hz)
bands = {
    'Theta (4-8 Hz)': (4.0, 8.0),
    'Alpha (8-12 Hz)': (8.0, 12.0),
    'Beta (13-30 Hz)': (13.0, 30.0)
}

band_r = {}
band_data = {}

for bname, (f_low, f_high) in bands.items():
    sos = butter(4, [f_low, f_high], btype='bandpass', fs=fs, output='sos')
    filt = sosfiltfilt(sos, clipped_data, axis=0)
    band_data[bname] = filt
    phases = np.angle(hilbert(filt, axis=0))
    z = np.exp(1j * phases)
    r = np.abs(np.mean(z, axis=1))
    band_r[bname] = r

# Let's check statistics of r(t) for eye open (0) vs closed (1)
results = {}
for bname, r in band_r.items():
    r_open = r[eye_state == 0]
    r_closed = r[eye_state == 1]
    results[bname] = {
        'mean_all': float(np.mean(r)),
        'std_all': float(np.std(r)),
        'mean_open': float(np.mean(r_open)),
        'std_open': float(np.std(r_open)),
        'mean_closed': float(np.mean(r_closed)),
        'std_closed': float(np.std(r_closed)),
        'delta_coherence': float(np.mean(r_closed) - np.mean(r_open))
    }
    print(f"=== {bname} ===")
    print(f"  All: {results[bname]['mean_all']:.4f} +/- {results[bname]['std_all']:.4f}")
    print(f"  Eye Open:   {results[bname]['mean_open']:.4f}")
    print(f"  Eye Closed: {results[bname]['mean_closed']:.4f}")
    print(f"  Delta r (Closed - Open): {results[bname]['delta_coherence']:+.4f}")

# Occipital Alpha Synchronization (O1 & O2 Berger effect)
alpha_O1 = band_data['Alpha (8-12 Hz)'][:, channels.index('O1')]
alpha_O2 = band_data['Alpha (8-12 Hz)'][:, channels.index('O2')]
power_alpha_occ = alpha_O1**2 + alpha_O2**2

p_occ_open = np.mean(power_alpha_occ[eye_state == 0])
p_occ_closed = np.mean(power_alpha_occ[eye_state == 1])
berger_ratio = p_occ_closed / p_occ_open
print(f"\nBerger Effect: Occipital Alpha Power Ratio (Closed / Open): {berger_ratio:.4f}")

# Occipital phase locking value (PLV) between O1 and O2
phases_O1 = np.angle(hilbert(alpha_O1))
phases_O2 = np.angle(hilbert(alpha_O2))
dphase = phases_O1 - phases_O2
plv_open = np.abs(np.mean(np.exp(1j * dphase[eye_state == 0])))
plv_closed = np.abs(np.mean(np.exp(1j * dphase[eye_state == 1])))
print(f"Occipital PLV(O1, O2) - Open: {plv_open:.4f}, Closed: {plv_closed:.4f}")

# Takens embedding & RQA on Global Alpha Order Parameter r(t)
# Downsample by 4 to focus on envelope dynamics (fs_eff = 32 Hz)
r_alpha_sub = band_r['Alpha (8-12 Hz)'][::4]
r_alpha_norm = (r_alpha_sub - np.mean(r_alpha_sub)) / np.std(r_alpha_sub)
emb = takens_embedding(r_alpha_norm, m=3, tau=4)
rec_mat = recurrence_matrix(emb, epsilon=0.25)
rqa = compute_rqa_metrics(rec_mat)
print("\nRQA Metrics for Alpha Kuramoto Order Parameter:")
for k, v in rqa.items():
    print(f"  {k}: {v:.4f}")

# Figure generation
fig, axes = plt.subplots(3, 1, figsize=(11, 10), sharex=True)

# 1. Raw Occipital Signals and Eye State
axes[0].plot(time, clipped_data[:, channels.index('O1')], color='#38bdf8', lw=0.8, label='O1 (Occipital Left)')
axes[0].plot(time, clipped_data[:, channels.index('O2')], color='#a855f7', lw=0.8, label='O2 (Occipital Right)')
axes[0].fill_between(time, np.min(clipped_data[:, [channels.index('O1'), channels.index('O2')]]), 
                     np.max(clipped_data[:, [channels.index('O1'), channels.index('O2')]]),
                     where=(eye_state == 1), color='#f43f5e', alpha=0.15, label='Eye Closed State')
axes[0].set_ylabel('Potential (µV)')
axes[0].set_title('14-Channel Cortical EEG: Occipital Dynamics & Eye State Modulation', fontsize=12, fontweight='bold')
axes[0].grid(True, alpha=0.3)
axes[0].legend(loc='upper right', ncol=3, fontsize=9)

# 2. Kuramoto Phase Coherence Across Canonical Bands
axes[1].plot(time, band_r['Theta (4-8 Hz)'], color='#10b981', lw=0.9, alpha=0.8, label='Theta r(t)')
axes[1].plot(time, band_r['Alpha (8-12 Hz)'], color='#f59e0b', lw=1.2, label='Alpha r(t)')
axes[1].plot(time, band_r['Beta (13-30 Hz)'], color='#06b6d4', lw=0.9, alpha=0.8, label='Beta r(t)')
axes[1].fill_between(time, 0, 1, where=(eye_state == 1), color='#f43f5e', alpha=0.12)
axes[1].set_ylabel('Order Parameter $r(t)$')
axes[1].set_title('Global Cortical Kuramoto Synchronization $r(t)$ Across Frequency Bands', fontsize=11, fontweight='bold')
axes[1].set_ylim(0, 1)
axes[1].grid(True, alpha=0.3)
axes[1].legend(loc='upper right', ncol=3, fontsize=9)

# 3. Occipital Alpha Envelope & PLV
axes[2].plot(time, np.sqrt(power_alpha_occ), color='#ec4899', lw=1.0, label='Occipital Alpha Envelope $|O_1 + O_2|$')
axes[2].fill_between(time, 0, np.max(np.sqrt(power_alpha_occ)), where=(eye_state == 1), color='#f43f5e', alpha=0.12, label='Eye Closed')
axes[2].set_xlabel('Time (seconds)')
axes[2].set_ylabel('Envelope Amp (µV)')
axes[2].set_title(f'Berger Effect: Occipital Alpha Power Modulation (Ratio={berger_ratio:.2f}, PLV: {plv_open:.2f}→{plv_closed:.2f})', fontsize=11, fontweight='bold')
axes[2].grid(True, alpha=0.3)
axes[2].legend(loc='upper right', fontsize=9)

plt.tight_layout()
fig.savefig('neural_eeg_coherence_analysis.png', dpi=200)
print("Saved neural_eeg_coherence_analysis.png")

import json
eeg_summary = {
    "system": "14-Channel Cortical EEG (Macroscopic Neural Population)",
    "dataset": "neural_eeg",
    "sampling_rate_hz": 128.0,
    "duration_s": float(time[-1]),
    "berger_effect_alpha_power_ratio_closed_to_open": float(berger_ratio),
    "occipital_plv_O1_O2": {
        "eye_open": float(plv_open),
        "eye_closed": float(plv_closed)
    },
    "canonical_band_kuramoto_order_parameter": results,
    "alpha_envelope_rqa": {
        "embedding_dimension": 3,
        "tau_steps": 4,
        "epsilon": 0.25,
        "determinism_DET": float(rqa['DET']),
        "laminarity_LAM": float(rqa['LAM']),
        "recurrence_rate_RR": float(rqa['RR']),
        "shannon_entropy_ENT": float(rqa['ENT'])
    }
}

with open("neural_eeg_invariants.json", "w") as f:
    json.dump(eeg_summary, f, indent=2)

print("Saved neural_eeg_invariants.json")
