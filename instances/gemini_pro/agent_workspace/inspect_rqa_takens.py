import numpy as np
import matplotlib.pyplot as plt
from colony_lib.datasets import load_dataset
from colony_lib.recurrence import takens_embedding, recurrence_matrix, compute_rqa_metrics

ds = load_dataset('belousov_zhabotinsky')
df = ds.to_dataframe()
t = df['time_s'].values
redox = df['redox_potential_mv'].values
u = df['activator_u'].values

# Standardize redox
x = (redox - np.mean(redox)) / np.std(redox)

# Compute autocorrelation to find first zero or 1/e
from scipy.signal import correlate
acorr = correlate(x, x, mode='full')
acorr = acorr[len(x)-1:]
acorr = acorr / acorr[0]

# First zero crossing or first minimum
zero_crossings = np.where(np.diff(np.sign(acorr)))[0]
first_zero = zero_crossings[0] if len(zero_crossings) > 0 else None
first_min = np.where(np.diff(np.diff(acorr)) > 0)[0]
print(f"First zero crossing of autocorrelation: tau = {first_zero} (t = {first_zero*0.01:.2f}s)")

# Mutual information estimate
def mutual_information(series, max_tau=100, bins=32):
    n = len(series)
    mi = []
    p_x, _ = np.histogram(series, bins=bins, density=True)
    p_x = p_x[p_x > 0]
    h_x = -np.sum(p_x * np.log(p_x))
    
    for tau in range(1, max_tau):
        x_t = series[:-tau]
        x_tau = series[tau:]
        p_2d, _, _ = np.histogram2d(x_t, x_tau, bins=bins, density=True)
        p_2d = p_2d[p_2d > 0]
        h_2d = -np.sum(p_2d * np.log(p_2d))
        # MI = 2*H_x - H_2d roughly (or H(X) + H(Y) - H(X,Y))
        p_1, _ = np.histogram(x_t, bins=bins, density=True)
        p_2, _ = np.histogram(x_tau, bins=bins, density=True)
        h1 = -np.sum(p_1[p_1 > 0] * np.log(p_1[p_1 > 0]))
        h2 = -np.sum(p_2[p_2 > 0] * np.log(p_2[p_2 > 0]))
        mi.append(h1 + h2 - h_2d)
    return np.array(mi)

mi = mutual_information(x, max_tau=150)
first_mi_min = np.where(np.diff(np.diff(mi)) > 0)[0][0] + 1
print(f"First local minimum of Mutual Information: tau = {first_mi_min} (t = {first_mi_min*0.01:.2f}s)")

# Let's test Takens embedding with tau=first_mi_min or tau=first_zero
for tau in [first_mi_min, 25, 50, 100]:
    for m in [2, 3, 4]:
        emb = takens_embedding(x, m=m, tau=tau)
        R = recurrence_matrix(emb, epsilon=0.2)
        rqa = compute_rqa_metrics(R)
        print(f"tau={tau:3d}, m={m}: RR={rqa['recurrence_rate']:.4f}, DET={rqa['determinism']:.4f}, LAM={rqa['laminarity']:.4f}, ENT={rqa['shannon_entropy']:.4f}, Lmax={rqa['max_diag_length']}")

