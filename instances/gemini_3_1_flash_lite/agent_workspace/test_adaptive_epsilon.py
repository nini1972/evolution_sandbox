import numpy as np
from colony_lib.dynamics import GrayScott2D
from colony_lib.recurrence import recurrence_matrix, compute_rqa_metrics, takens_embedding

def get_adaptive_epsilon(embedded, target_rr=0.05):
    """Finds an epsilon that results in a target recurrence rate."""
    # Compute distances to neighbors
    from scipy.spatial.distance import pdist
    distances = pdist(embedded)
    # Target percentile corresponding to recurrence rate
    return np.percentile(distances, target_rr * 100)

# Test adaptive epsilon
gs = GrayScott2D(N=64, f=0.03, k=0.06)
for _ in range(5000): gs.step()
series = []
for _ in range(2000):
    gs.step()
    series.append(gs.u[32, 32])
series = np.array(series)
embedded = takens_embedding(series, m=3, tau=2)

target_rr = 0.05
eps = get_adaptive_epsilon(embedded, target_rr=target_rr)
R = recurrence_matrix(embedded, epsilon=eps)
metrics = compute_rqa_metrics(R)
print(f"Adaptive epsilon={eps:.4f}, RR={metrics['recurrence_rate']:.4f}, DET={metrics['determinism']:.4f}")
