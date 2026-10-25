import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from colony_lib.datasets import load_dataset
from colony_lib.recurrence import takens_embedding, recurrence_matrix, compute_rqa_metrics

ds = load_dataset('solar_sunspots')
time = ds.data[:, 2] # decimal year
sunspots = ds.data[:, 3]

print(f"Data length: {len(sunspots)} months ({time[0]:.1f} to {time[-1]:.1f})")

# Let's inspect autocorrelation and mutual information / first minimum of AMI or ACF to choose tau
from scipy.signal import correlate

ac = correlate(sunspots - np.mean(sunspots), sunspots - np.mean(sunspots), mode='full')
ac = ac[len(sunspots)-1:]
ac /= ac[0]

# First zero crossing of ACF
zero_cross = np.where(ac < 0)[0]
tau_acf = zero_cross[0] if len(zero_cross) > 0 else 33
print(f"First ACF zero crossing: lag {tau_acf} months (~{tau_acf/12:.2f} years)")

# Peak ACF (Schwabe cycle period)
peak_acf = np.argmax(ac[50:200]) + 50
print(f"Dominant ACF peak: lag {peak_acf} months (~{peak_acf/12:.2f} years)")

# Subsample or smooth slightly or Takens embedding directly
# Standard Schwabe cycle is ~11 years = 132 months. 1/4 cycle is ~33 months.
# Tau = 33 months (approx 2.75 years)
m = 3
tau = 33
emb = takens_embedding(sunspots, m=m, tau=tau)
print(f"Embedded shape: {emb.shape}")

# Choose epsilon: standard rule is 10% of phase space diameter or standard deviation
dist = np.std(emb)
eps = 0.2 * dist
R = recurrence_matrix(emb, epsilon=eps)
metrics = compute_rqa_metrics(R)
print("RQA Metrics:")
for k, v in metrics.items():
    print(f"  {k}: {v}")
