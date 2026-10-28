
import numpy as np
from scipy.signal import butter, lfilter
from colony_lib.datasets import load_dataset
from colony_lib.recurrence import takens_embedding, recurrence_matrix, compute_rqa_metrics
import pandas as pd
import json
import matplotlib.pyplot as plt

# Configure matplotlib for headless environment
plt.switch_backend('Agg')

# --- 1. Load Data ---

ds = load_dataset("neural_eeg")
df = pd.DataFrame(ds.data, columns=ds.columns)

# Extract AF3 channel and segment
segment_length = 5000
af3_series = df['AF3'].values[:segment_length]

# Attempt to get sampling rate from metadata
sampling_rate = None
if hasattr(ds, 'metadata') and 'sampling_rate' in ds.metadata:
    sampling_rate = ds.metadata['sampling_rate']
elif hasattr(ds, 'metadata'):
    print(f"Warning: 'sampling_rate' not found in ds.metadata. Available metadata keys: {ds.metadata.keys()}")
else:
    print("Warning: ds has no 'metadata' attribute.")

if sampling_rate is None:
    # Fallback to a common sampling rate for EEG if not found, or raise an error
    # For 'neural_eeg', the problem description mentioned '128 Hz'.
    # It's better to explicitly use the stated rate or report an issue if it's not discoverable.
    # For now, let's assume 128Hz as per problem description if not found.
    print("Falling back to assumed sampling rate of 128 Hz for neural_eeg as it was not found in dataset metadata.")
    sampling_rate = 128

print(f"Analyzing AF3 channel for a segment of {segment_length} data points with sampling rate {sampling_rate} Hz.")

# --- 2. Define Frequency Bands and Filter Function ---

frequency_bands = {
    "Delta": (0.5, 4),
    "Theta": (4, 8),
    "Alpha": (8, 12),
    "Beta": (12, 30),
    "Gamma": (30, 45) # Limiting Gamma to 45Hz for practical filtering
}

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    y = lfilter(b, a, data)
    return y

# --- 3. Perform RQA for each Frequency Band ---

rqa_band_results = {}
rqa_metrics_to_plot = ['recurrence_rate', 'determinism', 'laminarity', 'shannon_entropy']

# RQA Parameters (fixed for all bands)
m = 3
tau = 2 # Based on previous sweep analysis for a balance of RR and DET
epsilon = 10

for band_name, (low_freq, high_freq) in frequency_bands.items():
    print(f"\n--- Processing {band_name} Band ({low_freq}-{high_freq} Hz) ---")

    # Apply bandpass filter
    filtered_series = butter_bandpass_filter(af3_series, low_freq, high_freq, sampling_rate)

    # Perform Takens embedding
    embedded_data = takens_embedding(filtered_series, m=m, tau=tau)

    if embedded_data.shape[0] < 2:
        print(f"Insufficient embedded data points for {band_name} band. Skipping RQA.")
        rqa_band_results[band_name] = {'error': 'Insufficient data'}
        continue

    # Compute recurrence matrix
    recurrence_matrix_band = recurrence_matrix(embedded_data, epsilon=epsilon)

    # Compute RQA metrics
    rqa_metrics_band = compute_rqa_metrics(recurrence_matrix_band)

    rqa_band_results[band_name] = {
        'm': m,
        'tau': tau,
        'epsilon': epsilon,
        'segment_length': segment_length,
        'low_freq': low_freq,
        'high_freq': high_freq,
    }
    for key in rqa_metrics_to_plot: # Only store metrics intended for plotting
        rqa_band_results[band_name][key] = rqa_metrics_band.get(key, np.nan)

    for key, value in rqa_band_results[band_name].items():
        if isinstance(value, (int, float)):
            print(f"{key}: {value:.4f}")
        else:
            print(f"{key}: {value}")

# --- 4. Save Results to JSON ---
output_json_filename = 'eeg_af3_rqa_frequency_bands_results.json'
with open(output_json_filename, 'w') as f:
    json.dump(rqa_band_results, f, indent=4)
print(f"\nAF3 RQA frequency band results saved to {output_json_filename}")

# --- 5. Plot Results ---

fig, axes = plt.subplots(len(rqa_metrics_to_plot), 1, figsize=(10, 15), sharex=True)

bands = list(rqa_band_results.keys())
x_pos = np.arange(len(bands))

for i, metric in enumerate(rqa_metrics_to_plot):
    values = [rqa_band_results[band].get(metric, np.nan) for band in bands]
    axes[i].bar(x_pos, values, align='center', alpha=0.7)
    axes[i].set_ylabel(metric)
    axes[i].set_xticks(x_pos)
    axes[i].set_xticklabels(bands)
    axes[i].set_title(f'{metric} across EEG Frequency Bands')
    axes[i].grid(axis='y', linestyle='--', alpha=0.7)

plt.xlabel('EEG Frequency Band')
plt.tight_layout()
output_plot_filename = 'eeg_af3_rqa_frequency_bands_plot.png'
plt.savefig(output_plot_filename)
plt.close()
print(f"RQA metrics across frequency bands plot saved as {output_plot_filename}")
