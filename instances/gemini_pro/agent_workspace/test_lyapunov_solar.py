import numpy as np
from colony_lib.datasets import load_dataset
from colony_lib.recurrence import takens_embedding

ds = load_dataset('solar_sunspots')
time = ds.data[:, 2]
sunspots = ds.data[:, 3]

# Estimate maximal Lyapunov exponent via Rosenstein algorithm
def rosenstein_lyapunov(series, m=3, tau=33, max_iter=50, mean_period=130):
    emb = takens_embedding(series, m=m, tau=tau)
    N = len(emb)
    # Find nearest neighbors outside mean period
    nn_indices = np.zeros(N, dtype=int)
    for i in range(N):
        dists = np.linalg.norm(emb - emb[i], axis=1)
        # exclude temporal window around i
        mask = np.abs(np.arange(N) - i) > mean_period
        dists[~mask] = np.inf
        nn_indices[i] = np.argmin(dists)
        
    divergence = np.zeros(max_iter)
    counts = np.zeros(max_iter)
    for k in range(1, max_iter):
        valid_i = [i for i in range(N - k) if nn_indices[i] + k < N]
        if len(valid_i) > 0:
            d_k = [np.linalg.norm(emb[i + k] - emb[nn_indices[i] + k]) for i in valid_i]
            d_k = [d for d in d_k if d > 1e-10]
            if len(d_k) > 0:
                divergence[k] = np.mean(np.log(d_k))
                counts[k] = len(d_k)
                
    # Linear fit over initial slope (e.g. k=5 to 25)
    ks = np.arange(5, 25)
    slope, intercept = np.polyfit(ks, divergence[5:25], 1)
    return slope, ks, divergence

idx_dalton = np.where((time >= 1790) & (time <= 1830))[0]
idx_modern = np.where((time >= 1940) & (time <= 1980))[0]

lambda_dalton, _, _ = rosenstein_lyapunov(sunspots[idx_dalton])
lambda_modern, _, _ = rosenstein_lyapunov(sunspots[idx_modern])
lambda_full, ks, div_full = rosenstein_lyapunov(sunspots)

print(f"Maximal Lyapunov Exponent (Dalton Minimum): {lambda_dalton:.5f} / month ({lambda_dalton*12:.4f} / year)")
print(f"Maximal Lyapunov Exponent (Modern Maximum): {lambda_modern:.5f} / month ({lambda_modern*12:.4f} / year)")
print(f"Maximal Lyapunov Exponent (Full 277 Years): {lambda_full:.5f} / month ({lambda_full*12:.4f} / year)")
