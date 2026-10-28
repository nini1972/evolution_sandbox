
import numpy as np
from colony_lib.datasets import load_dataset
from colony_lib.recurrence import takens_embedding, recurrence_matrix, compute_rqa_metrics
import pandas as pd
import json

# Load the neural_eeg dataset
ds = load_dataset("neural_eeg")

# Convert to pandas DataFrame
df = pd.DataFrame(ds["data"], columns=ds["columns"])

# Extract AF3 channel series and take a segment
segment_length = 5000
af3_series = df['AF3'].values[:segment_length]

print(f"Analyzing AF3 channel for a segment of {segment_length} data points for tau sweep.")

# RQA parameters
m = 3  # Embedding dimension
epsilon = 10 # Fixed epsilon

tau_values = range(1, 11) # Sweep tau from 1 to 10

rqa_results = []

for tau in tau_values:
    print(f"\n--- Processing AF3 with m={m}, tau={tau}, epsilon={epsilon} ---")

    af3_embedded = takens_embedding(af3_series, m=m, tau=tau)

    if af3_embedded.shape[0] < 2:
        print(f"Insufficient embedded data points for AF3 channel (m={m}, tau={tau}). Skipping RQA.")
        continue

    # Compute recurrence matrix
    af3_recurrence_matrix = recurrence_matrix(af3_embedded, epsilon=epsilon)

    # Compute RQA metrics
    af3_rqa_metrics = compute_rqa_metrics(af3_recurrence_matrix)

    # Add parameters to results
    af3_rqa_metrics['m'] = m
    af3_rqa_metrics['tau'] = tau
    af3_rqa_metrics['epsilon'] = epsilon
    af3_rqa_metrics['segment_length'] = segment_length

    rqa_results.append(af3_rqa_metrics)

    for key, value in af3_rqa_metrics.items():
        if isinstance(value, (int, float)):
            print(f"{key}: {value:.4f}")
        else:
            print(f"{key}: {value}")

# Save results to a JSON file
output_filename = 'eeg_af3_rqa_tau_sweep_results.json'
with open(output_filename, 'w') as f:
    json.dump(rqa_results, f, indent=4)

print(f"\nAF3 RQA tau sweep results saved to {output_filename}")
