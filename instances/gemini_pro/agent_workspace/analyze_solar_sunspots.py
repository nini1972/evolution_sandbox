import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, periodogram, welch

from colony_lib.datasets import load_dataset
from colony_lib.recurrence import takens_embedding, recurrence_matrix, compute_rqa_metrics

ds = load_dataset('solar_sunspots')
df = ds.to_dataframe()
print("Solar Sunspots metadata:", ds.metadata)
print(df.head())
print(df.tail())
print("Null count:", df.isnull().sum().to_dict())

time = df['decimal_year'].values
ssn = df['sunspot_number'].values

# Compute autocorrelation and dominant period
dt = np.median(np.diff(time)) # ~0.0833 yr = 1 month
print(f"Sampling interval dt = {dt:.4f} years ({1/dt:.1f} observations/year)")

# Autocorrelation
ssn_centered = ssn - np.mean(ssn)
autocorr = np.correlate(ssn_centered, ssn_centered, mode='full')
autocorr = autocorr[len(autocorr)//2:]
autocorr /= autocorr[0]

lags_years = np.arange(len(autocorr)) * dt
peaks, _ = find_peaks(autocorr[:1200], distance=int(8/dt), prominence=0.1)
print("Autocorrelation peak lags (years):", lags_years[peaks[:5]])
if len(peaks) > 0:
    first_peak_period = lags_years[peaks[0]]
    print(f"Primary Schwabe cycle period from ACF: {first_peak_period:.2f} years")

# Spectral analysis
freqs, psd = periodogram(ssn, fs=1/dt)
valid = (freqs > 0.02) & (freqs < 0.3) # 3.3 to 50 years
peak_freq = freqs[valid][np.argmax(psd[valid])]
spectral_period = 1 / peak_freq
print(f"Peak spectral period: {spectral_period:.2f} years")

# Cycle amplitude variations (Gleissberg cycle envelope)
# Find individual solar cycle maxima
cycle_peaks, _ = find_peaks(ssn, distance=int(8/dt), prominence=30)
peak_times = time[cycle_peaks]
peak_amps = ssn[cycle_peaks]
cycle_periods = np.diff(peak_times)
print(f"Mean peak-to-peak solar cycle period: {np.mean(cycle_periods):.2f} +/- {np.std(cycle_periods):.2f} years")
print(f"Solar cycle count: {len(cycle_peaks)}")

# RQA on smoothed sunspot series (e.g. 13-month moving average)
ssn_smooth = pd.Series(ssn).rolling(13, center=True).mean().dropna().values
ssn_norm = (ssn_smooth - np.mean(ssn_smooth)) / np.std(ssn_smooth)

# Subsample to ~6 month resolution for manageable Takens embedding
sub = ssn_norm[::6]
# tau ~ 1/4 of cycle (~2.75 years -> ~5.5 steps at 6mo)
emb = takens_embedding(sub, m=3, tau=5)
R = recurrence_matrix(emb, epsilon=0.35)
rqa = compute_rqa_metrics(R)

print("\nSolar Dynamo RQA Metrics (m=3, tau=5, eps=0.35):")
for k, v in rqa.items():
    print(f"  {k}: {v:.4f}")

