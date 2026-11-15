import numpy as np
from colony_lib.dynamics import GrayScott2D
from colony_lib.recurrence import recurrence_matrix, compute_rqa_metrics, takens_embedding
from scipy.spatial.distance import pdist

def get_adaptive_epsilon(embedded, target_rr=0.05):
    distances = pdist(embedded)
    # Ensure distances is not all zeros
    if np.all(distances == 0):
        return 0.1
    return np.percentile(distances, target_rr * 100)

results = []
F, k = 0.035, 0.060
target_rr = 0.05

# 5pt (standard)
gs = GrayScott2D(N=64, f=F, k=k)
for _ in range(5000): gs.step()
series = []
for _ in range(2000):
    gs.step()
    series.append(gs.u[32, 32])
series = np.array(series)
embedded = takens_embedding(series, m=3, tau=2)
eps = get_adaptive_epsilon(embedded, target_rr=target_rr)
R = recurrence_matrix(embedded, epsilon=eps)
metrics = compute_rqa_metrics(R)
results.append({'stencil': '5pt', 'eps': eps, 'DET': metrics['determinism'], 'RR': metrics['recurrence_rate']})

print(results)
