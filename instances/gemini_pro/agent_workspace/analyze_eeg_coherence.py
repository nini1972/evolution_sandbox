import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import welch

from colony_lib.datasets import load_dataset
from colony_lib.recurrence import takens_embedding, recurrence_matrix, compute_rqa_metrics

ds = load_dataset('neural_eeg')
df = ds.to_dataframe()
print("Neural EEG metadata:", ds.metadata)
print(df.head())

channels = ['AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1', 'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4']
fs = ds.sampling_rate # 128 Hz

# Convert channels to microvolts or normalized z-scores
data = df[channels].values
# Check for artifacts / outliers (sometimes Emotiv EEG has extreme baseline shifts)
print("Data quantiles per channel:")
print(df[channels].describe().T[['mean', 'std', 'min', 'max']])

# Remove extreme outliers / baseline drift via median filtering or robust z-score
medians = np.median(data, axis=0)
iqrs = np.percentile(data, 75, axis=0) - np.percentile(data, 25, axis=0)
z_data = (data - medians) / (iqrs + 1e-6)

# Compute instantaneous phase via Hilbert transform for Kuramoto order parameter
from scipy.signal import hilbert

# Bandpass filter around Alpha band (8 - 12 Hz)
from scipy.signal import butter, sosfiltfilt
sos_alpha = butter(4, [8.0, 12.0], btype='bandpass', fs=fs, output='sos')
alpha_data = sosfiltfilt(sos_alpha, data, axis=0)

# Instantaneous phases
phases = np.angle(hilbert(alpha_data, axis=0))

# Kuramoto order parameter r(t) = |1/N sum_j exp(i * theta_j(t))|
z_phasors = np.exp(1j * phases)
r_t = np.abs(np.mean(z_phasors, axis=1))

print(f"Alpha-band Kuramoto order parameter mean: {np.mean(r_t):.4f}, std: {np.std(r_t):.4f}, min: {np.min(r_t):.4f}, max: {np.max(r_t):.4f}")

# Compare eye open vs eye closed states
eye_state = df['eyeDetection'].values
r_open = r_t[eye_state == 0]
r_closed = r_t[eye_state == 1]
print(f"Eye Open (0) count: {len(r_open)}, mean r: {np.mean(r_open):.4f} +/- {np.std(r_open):.4f}")
print(f"Eye Closed (1) count: {len(r_closed)}, mean r: {np.mean(r_closed):.4f} +/- {np.std(r_closed):.4f}")

# Cross-channel correlation matrix
corr_open = np.corrcoef(alpha_data[eye_state == 0].T)
corr_closed = np.corrcoef(alpha_data[eye_state == 1].T)

print("Mean alpha cross-channel correlation Open:", np.mean(corr_open[np.triu_indices(len(channels), k=1)]))
print("Mean alpha cross-channel correlation Closed:", np.mean(corr_closed[np.triu_indices(len(channels), k=1)]))

