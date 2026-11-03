import numpy as np
import pandas as pd
from colony_lib.datasets import load_dataset
from colony_lib.recurrence import takens_embedding, recurrence_matrix, compute_rqa_metrics

ds = load_dataset('belousov_zhabotinsky')
df = ds.to_dataframe()
print(df.head())
print(df.describe())

# Check primary signal
v = df['redox_potential_mv'].values
u = df['activator_u'].values
z = df['catalyst_z'].values
inh = df['inhibitor_v'].values

# Compute autocorrelation to determine first minimum tau
from scipy.signal import correlate
ac = np.correlate(v - np.mean(v), v - np.mean(v), mode='full')
ac = ac[len(ac)//2:]
ac /= ac[0]
lags = np.arange(len(ac))

# Find first zero or minimum
min_lag = np.where(np.diff(ac) > 0)[0]
first_min = min_lag[0] if len(min_lag) > 0 else 10
print(f"First AC minimum lag: {first_min} (dt=0.01s -> {first_min*0.01:.2f}s)")

# Takens embedding
emb = takens_embedding(v, m=3, tau=first_min)
R = recurrence_matrix(emb, epsilon=0.1 * np.std(v))
rqa = compute_rqa_metrics(R)
print("RQA metrics:", rqa)
