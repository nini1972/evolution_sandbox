import numpy as np
import pandas as pd
from colony_lib.datasets import load_dataset

ds = load_dataset('belousov_zhabotinsky')
df = ds.to_dataframe()
t = df['time_s'].values
u = df['activator_u'].values
v = df['inhibitor_v'].values
z = df['catalyst_z'].values
redox = df['redox_potential_mv'].values

# Let's inspect activator_u peaks
from scipy.signal import find_peaks
u_peaks, _ = find_peaks(u, height=0.1, distance=10)
print(f"Activator u peaks at indices: {u_peaks}, times: {t[u_peaks]}, heights: {u[u_peaks]}")

redox_min, _ = find_peaks(-redox, height=-1050, distance=10)
print(f"Redox troughs at times: {t[redox_min]}, heights: {redox[redox_min]}")

# Look at time intervals
for i, up in enumerate(u_peaks):
    print(f"Burst {i}: t={t[up]:.2f}s, u={u[up]:.4f}, v={v[up]:.4f}, z={z[up]:.4f}, redox={redox[up]:.1f} mV")

