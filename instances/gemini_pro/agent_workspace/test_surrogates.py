import numpy as np
from scipy.signal import hilbert, butter, filtfilt
from colony_lib.datasets import load_dataset
from colony_lib.recurrence import takens_embedding, recurrence_matrix, compute_rqa_metrics

ds = load_dataset('solar_sunspots')
sunspots = ds.data[:, 3]

# Extract Dalton (1790-1830) vs Modern Max (1940-1980)
time = ds.data[:, 2]
idx_dalton = np.where((time >= 1790) & (time <= 1830))[0]
idx_modern = np.where((time >= 1940) & (time <= 1980))[0]

series_dalton = sunspots[idx_dalton]
series_modern = sunspots[idx_modern]

m = 3
tau = 33

def get_det_lam(s, eps_factor=0.25):
    emb = takens_embedding(s, m=m, tau=tau)
    R = recurrence_matrix(emb, epsilon=eps_factor * np.std(s))
    rqa = compute_rqa_metrics(R)
    return rqa['DET'], rqa['LAM'], rqa['L']

det_d, lam_d, l_d = get_det_lam(series_dalton)
det_m, lam_m, l_m = get_det_lam(series_modern)

print(f"Empirical Dalton: DET={det_d:.4f}, LAM={lam_d:.4f}, L_mean={l_d:.4f}")
print(f"Empirical Modern: DET={det_m:.4f}, LAM={lam_m:.4f}, L_mean={l_m:.4f}")

# Fourier phase-randomized surrogate test (IAAFT or FT surrogate)
# To test if the difference in DET and LAM is explained by linear autocorrelation alone
def fourier_surrogate(s):
    fft_s = np.fft.rfft(s)
    phases = np.random.uniform(0, 2*np.pi, len(fft_s))
    phases[0] = 0 # DC term
    fft_surr = np.abs(fft_s) * np.exp(1j * phases)
    surr = np.fft.irfft(fft_surr, n=len(s))
    # match amplitude distribution rank
    return surr

n_surr = 100
surr_diffs_det = []
for _ in range(n_surr):
    s_d = fourier_surrogate(series_dalton)
    s_m = fourier_surrogate(series_modern)
    d_det, _, _ = get_det_lam(s_d)
    m_det, _, _ = get_det_lam(s_m)
    surr_diffs_det.append(d_det - m_det)

emp_diff_det = det_d - det_m
p_val = np.mean(np.array(surr_diffs_det) >= emp_diff_det)
print(f"Empirical DET Difference (Dalton - Modern): {emp_diff_det:.4f}")
print(f"Surrogate Mean Difference: {np.mean(surr_diffs_det):.4f} +/- {np.std(surr_diffs_det):.4f}")
print(f"p-value (empirical exceeds linear surrogates): {p_val:.4f}")
