
import json
import matplotlib.pyplot as plt
import numpy as np

# Set matplotlib backend to Agg to prevent display errors in headless environment
plt.switch_backend('Agg')

# Read the JSON data
with open('world_c_results/world_c_job_llama_3_3_1792290141_5bef_rqa_embedding_dim_results.json', 'r') as f:
    results = json.load(f)

# Extract embedding_dim values and RQA metrics
embedding_dims = [res['embedding_dim'] for res in results]
recurrence_rate = [res['rqa_metrics']['recurrence_rate'] for res in results]
determinism = [res['rqa_metrics']['determinism'] for res in results]
laminarity = [res['rqa_metrics']['laminarity'] for res in results]
mean_diag_length = [res['rqa_metrics']['mean_diag_length'] for res in results]
max_diag_length = [res['rqa_metrics']['max_diag_length'] for res in results]
shannon_entropy = [res['rqa_metrics']['shannon_entropy'] for res in results]

# Create plots
fig, axs = plt.subplots(6, 1, figsize=(10, 24), sharex=True)

axs[0].plot(embedding_dims, recurrence_rate, 'b-o')
axs[0].set_title('Recurrence Rate vs. Embedding Dimension')
axs[0].set_ylabel('Recurrence Rate')
axs[0].grid(True)

axs[1].plot(embedding_dims, determinism, 'r-o')
axs[1].set_title('Determinism vs. Embedding Dimension')
axs[1].set_ylabel('Determinism')
axs[1].grid(True)

axs[2].plot(embedding_dims, laminarity, 'g-o')
axs[2].set_title('Laminarity vs. Embedding Dimension')
axs[2].set_ylabel('Laminarity')
axs[2].grid(True)

axs[3].plot(embedding_dims, mean_diag_length, 'm-o')
axs[3].set_title('Mean Diagonal Length vs. Embedding Dimension')
axs[3].set_ylabel('Mean Diagonal Length')
axs[3].grid(True)

axs[4].plot(embedding_dims, max_diag_length, 'c-o')
axs[4].set_title('Max Diagonal Length vs. Embedding Dimension')
axs[4].set_ylabel('Max Diagonal Length')
axs[4].grid(True)

axs[5].plot(embedding_dims, shannon_entropy, 'y-o')
axs[5].set_title('Shannon Entropy vs. Embedding Dimension')
axs[5].set_ylabel('Shannon Entropy')
axs[5].set_xlabel('Embedding Dimension')
axs[5].grid(True)

plt.tight_layout()
plt.savefig('rqa_embedding_dim_sensitivity.png')
print("Plot 'rqa_embedding_dim_sensitivity.png' generated successfully.")
