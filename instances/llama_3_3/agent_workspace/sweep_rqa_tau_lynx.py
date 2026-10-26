
import numpy as np
from colony_lib.datasets import load_dataset
from colony_lib.recurrence import takens_embedding, recurrence_matrix, compute_rqa_metrics
import pandas as pd
import json

# Load the lynx_hare dataset
ds = load_dataset("lynx_hare")

# Convert to pandas DataFrame
df = pd.DataFrame(ds["data"], columns=ds["columns"])

# Extract lynx population
lynx_series = df['lynx'].values

m = 3 # Fixed embedding dimension
tau_values = range(1, 5) # Range of tau values to explore

results = {}

for tau in tau_values:
    print(f"\n--- Processing Lynx with m={m}, tau={tau} ---")
    lynx_embedded = takens_embedding(lynx_series, m=m, tau=tau)

    # Ensure embedded data is not empty
    if lynx_embedded.shape[0] < 2: # Need at least two points to compute distances
        print(f"Skipping tau={tau} due to insufficient embedded data points.")
        continue

    # Determine epsilon for recurrence matrix (e.g., 10% of max phase space diameter)
    # Recalculate max_dist for each embedding as it depends on the data range
    lynx_max_dist = np.max(np.linalg.norm(lynx_embedded[:, np.newaxis] - lynx_embedded[np.newaxis, :], axis=2))

    if lynx_max_dist == 0: # Avoid division by zero if all points are identical
        print(f"Skipping tau={tau} due to zero maximum distance in embedded space.")
        continue

    epsilon_lynx = 0.1 * lynx_max_dist
    print(f"Calculated epsilon for lynx (m={m}, tau={tau}): {epsilon_lynx:.4f}")

    # Compute recurrence matrix
    lynx_recurrence_matrix = recurrence_matrix(lynx_embedded, epsilon=epsilon_lynx)

    # Compute RQA metrics
    lynx_rqa_metrics = compute_rqa_metrics(lynx_recurrence_matrix)

    results[f'm{m}_tau{tau}'] = {k: round(v, 4) for k, v in lynx_rqa_metrics.items()}

    for key, value in lynx_rqa_metrics.items():
        print(f"{key}: {value:.4f}")

# Save results to a JSON file
with open('lynx_rqa_tau_sweep_results.json', 'w') as f:
    json.dump(results, f, indent=4)

print("\nLynx RQA tau sweep results saved to lynx_rqa_tau_sweep_results.json")
