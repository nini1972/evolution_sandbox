import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from colony_lib.datasets import load_dataset
from colony_lib.recurrence import takens_embedding, recurrence_matrix, compute_rqa_metrics

ds = load_dataset('solar_sunspots')
time = ds.data[:, 2] # decimal year
sunspots = ds.data[:, 3]

# Sliding window RQA: window of 44 years (approx 4 Schwabe cycles = ~528 months)
# step of 1 year = 12 months
w_len = 528
step = 12
m = 3
tau = 33

results = []
window_times = []

for start in range(0, len(sunspots) - w_len, step):
    sub_series = sunspots[start:start+w_len]
    mid_time = time[start + w_len // 2]
    emb = takens_embedding(sub_series, m=m, tau=tau)
    # fixed epsilon based on overall std or local std
    eps = 0.3 * np.std(sunspots)
    R = recurrence_matrix(emb, epsilon=eps)
    rqa = compute_rqa_metrics(R)
    window_times.append(mid_time)
    results.append(rqa)

print(f"Computed {len(results)} windows from {window_times[0]:.1f} to {window_times[-1]:.1f}")
det_vals = [r['DET'] for r in results]
lam_vals = [r['LAM'] for r in results]
ent_vals = [r['ENT'] for r in results]
rr_vals = [r['RR'] for r in results]

# Let's inspect correlation with Dalton minimum (approx 1790-1830) and Modern Maximum (1940-2000)
print(f"Min DET: {np.min(det_vals):.4f} at year {window_times[np.argmin(det_vals)]:.1f}")
print(f"Max DET: {np.max(det_vals):.4f} at year {window_times[np.argmax(det_vals)]:.1f}")
print(f"Min LAM: {np.min(lam_vals):.4f} at year {window_times[np.argmin(lam_vals)]:.1f}")
print(f"Max LAM: {np.max(lam_vals):.4f} at year {window_times[np.argmax(lam_vals)]:.1f}")
