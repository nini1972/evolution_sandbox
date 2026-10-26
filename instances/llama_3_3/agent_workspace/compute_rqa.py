
import numpy as np
from colony_lib.datasets import load_dataset
from colony_lib.recurrence import takens_embedding, recurrence_matrix, compute_rqa_metrics
import pandas as pd

# Load the lynx_hare dataset
ds = load_dataset("lynx_hare")

# Convert to pandas DataFrame
df = pd.DataFrame(ds["data"], columns=ds["columns"])

# Extract lynx and hare populations
lynx_series = df['lynx'].values
hare_series = df['hare'].values

# Perform Takens embedding
m = 3 # Embedding dimension
tau = 1 # Time delay

lynx_embedded = takens_embedding(lynx_series, m=m, tau=tau)
hare_embedded = takens_embedding(hare_series, m=m, tau=tau)

# Determine epsilon for recurrence matrix (e.g., 10% of max phase space diameter)
lynx_max_dist = np.max(np.linalg.norm(lynx_embedded[:, np.newaxis] - lynx_embedded[np.newaxis, :], axis=2))
hare_max_dist = np.max(np.linalg.norm(hare_embedded[:, np.newaxis] - hare_embedded[np.newaxis, :], axis=2))

epsilon_lynx = 0.1 * lynx_max_dist
epsilon_hare = 0.1 * hare_max_dist

print(f"Calculated epsilon for lynx: {epsilon_lynx:.4f}")
print(f"Calculated epsilon for hare: {epsilon_hare:.4f}")

# Compute recurrence matrices
lynx_recurrence_matrix = recurrence_matrix(lynx_embedded, epsilon=epsilon_lynx)
hare_recurrence_matrix = recurrence_matrix(hare_embedded, epsilon=epsilon_hare)

# Compute RQA metrics
lynx_rqa_metrics = compute_rqa_metrics(lynx_recurrence_matrix)
hare_rqa_metrics = compute_rqa_metrics(hare_recurrence_matrix)

print("\n--- Lynx RQA Metrics ---")
for key, value in lynx_rqa_metrics.items():
    print(f"{key}: {value:.4f}")

print("\n--- Hare RQA Metrics ---")
for key, value in hare_rqa_metrics.items():
    print(f"{key}: {value:.4f}")
