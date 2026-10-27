
import numpy as np
from colony_lib.datasets import load_dataset
from colony_lib.recurrence import takens_embedding, recurrence_matrix, compute_rqa_metrics
import pandas as pd

# Load the neural_eeg dataset
ds = load_dataset("neural_eeg")

# Convert to pandas DataFrame
df = pd.DataFrame(ds["data"], columns=ds["columns"])

# Extract AF3 channel series and take a segment
# Using a segment to manage computational load for larger datasets
significant_segment_length = 5000 # Increased segment length to get more data points
af3_series = df['AF3'].values[:significant_segment_length]

print(f"Analyzing AF3 channel for a segment of {significant_segment_length} data points.")

# Perform Takens embedding
m = 3 # Embedding dimension
tau = 1 # Time delay

af3_embedded = takens_embedding(af3_series, m=m, tau=tau)

# Check if embedded data is sufficient
if af3_embedded.shape[0] < 2:
    print(f"Insufficient embedded data points for AF3 channel (m={m}, tau={tau}). Aborting RQA.")
else:
    # Use a fixed, smaller epsilon value
    epsilon_af3 = 10 # Example fixed epsilon, significantly smaller
    print(f"Using fixed epsilon for AF3 (m={m}, tau={tau}): {epsilon_af3:.4f}")

    # Compute recurrence matrix
    af3_recurrence_matrix = recurrence_matrix(af3_embedded, epsilon=epsilon_af3)

    # Compute RQA metrics
    af3_rqa_metrics = compute_rqa_metrics(af3_recurrence_matrix)

    print("\n--- AF3 Channel RQA Metrics with smaller epsilon ---")
    for key, value in af3_rqa_metrics.items():
        print(f"{key}: {value:.4f}")
