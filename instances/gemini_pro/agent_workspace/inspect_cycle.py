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

# Let's inspect t from 2.5 to 4.5 around Burst 0
idx = (t >= 2.5) & (t <= 4.5)
sub_df = df[idx]

# Check derivatives du/dt, dv/dt, dz/dt
dt = 0.01
du_dt = np.gradient(u, dt)
dv_dt = np.gradient(v, dt)
dz_dt = np.gradient(z, dt)
dredox_dt = np.gradient(redox, dt)

print(f"Max |du/dt|: {np.max(np.abs(du_dt)):.2f}, Min |du/dt| (quiescent): {np.percentile(np.abs(du_dt), 10):.6f}")
print(f"Ratio of fast to slow timescales: {np.max(np.abs(du_dt)) / np.percentile(np.abs(du_dt)[np.abs(du_dt)>0], 10):.2f}")

# Look at period between u peaks
print(f"Inter-burst interval (Burst 1 - Burst 0): {7.93 - 3.09:.4f} s")
