import numpy as np
from scipy.signal import hilbert, butter, filtfilt
from colony_lib.datasets import load_dataset
from colony_lib.recurrence import takens_embedding, recurrence_matrix, compute_rqa_metrics

ds = load_dataset('solar_sunspots')
time = ds.data[:, 2]
sunspots = ds.data[:, 3]

# Compute amplitude envelope
fs = 1.0
b, a = butter(3, [(1.0/180.0) / 0.5, (1.0/96.0) / 0.5], btype='band')
filtered_sunspots = filtfilt(b, a, sunspots)
amplitude_envelope = np.abs(hilbert(filtered_sunspots))

w_len = 528
step = 12
m = 3
tau = 33

# Let's test two types of epsilon:
# 1. Fixed global epsilon: eps = 0.25 * std(overall)
# 2. Local adaptive epsilon: eps = 0.25 * std(window)

results_global = []
results_local = []
mean_amps = []

for start in range(0, len(sunspots) - w_len, step):
    sub = sunspots[start:start+w_len]
    sub_amp = np.mean(amplitude_envelope[start:start+w_len])
    mean_amps.append(sub_amp)
    
    emb = takens_embedding(sub, m=m, tau=tau)
    
    # Global eps
    eps_g = 0.25 * np.std(sunspots)
    Rg = recurrence_matrix(emb, epsilon=eps_g)
    rqa_g = compute_rqa_metrics(Rg)
    results_global.append(rqa_g)
    
    # Local eps
    eps_l = 0.25 * np.std(sub)
    Rl = recurrence_matrix(emb, epsilon=eps_l)
    rqa_l = compute_rqa_metrics(Rl)
    results_local.append(rqa_l)

mean_amps = np.array(mean_amps)

det_g = np.array([r['DET'] for r in results_global])
lam_g = np.array([r['LAM'] for r in results_global])
rr_g = np.array([r['RR'] for r in results_global])

det_l = np.array([r['DET'] for r in results_local])
lam_l = np.array([r['LAM'] for r in results_local])
rr_l = np.array([r['RR'] for r in results_local])

print("GLOBAL EPSILON:")
print(f"  Corr(Amp, DET): {np.corrcoef(mean_amps, det_g)[0,1]:.4f}")
print(f"  Corr(Amp, LAM): {np.corrcoef(mean_amps, lam_g)[0,1]:.4f}")
print(f"  Corr(Amp, RR):  {np.corrcoef(mean_amps, rr_g)[0,1]:.4f}")

print("\nLOCAL ADAPTIVE EPSILON (controlling for density / scale):")
print(f"  Corr(Amp, DET): {np.corrcoef(mean_amps, det_l)[0,1]:.4f}")
print(f"  Corr(Amp, LAM): {np.corrcoef(mean_amps, lam_l)[0,1]:.4f}")
print(f"  Corr(Amp, RR):  {np.corrcoef(mean_amps, rr_l)[0,1]:.4f}")

# Also compute mean diagonal length L
l_g = np.array([r['L'] for r in results_global])
l_l = np.array([r['L'] for r in results_local])
print(f"  Corr(Amp, L_mean [global]): {np.corrcoef(mean_amps, l_g)[0,1]:.4f}")
print(f"  Corr(Amp, L_mean [local]):  {np.corrcoef(mean_amps, l_l)[0,1]:.4f}")
