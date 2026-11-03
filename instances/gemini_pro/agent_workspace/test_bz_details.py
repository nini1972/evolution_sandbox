import numpy as np
import pandas as pd
from colony_lib.datasets import load_dataset
from scipy.signal import find_peaks

ds = load_dataset('belousov_zhabotinsky')
df = ds.to_dataframe()
t = df['time_s'].values
u = df['activator_u'].values
v = df['inhibitor_v'].values
z = df['catalyst_z'].values
redox = df['redox_potential_mv'].values

print(f"Time span: {t[0]} to {t[-1]} s, dt = {t[1]-t[0]} s")

# Detect peaks in redox
peaks, props = find_peaks(redox, height=np.mean(redox), distance=20)
print(f"Peaks at indices: {peaks}, times: {t[peaks]}")
periods = np.diff(t[peaks])
print(f"Inter-spike intervals (periods): {periods}, mean period: {np.mean(periods):.4f}s, std: {np.std(periods):.4f}s")

# Let's inspect peak shapes and fast vs slow phases
# Find peak-to-peak cycles
for i in range(len(peaks)-1):
    idx1, idx2 = peaks[i], peaks[i+1]
    cycle_redox = redox[idx1:idx2]
    min_idx = idx1 + np.argmin(cycle_redox)
    slow_quiescent = t[min_idx] - t[idx1]
    fast_pulse = t[idx2] - t[min_idx]
    print(f"Cycle {i}: peak1={t[idx1]:.2f}s, trough={t[min_idx]:.2f}s, peak2={t[idx2]:.2f}s, decay={slow_quiescent:.2f}s, rise={fast_pulse:.2f}s")

# Also look at return map: P_{n+1} vs P_n
peak_heights = redox[peaks]
print(f"Peak heights: {peak_heights}")
