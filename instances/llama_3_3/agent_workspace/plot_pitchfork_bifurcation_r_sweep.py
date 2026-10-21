
import json
import matplotlib.pyplot as plt
import numpy as np

# Configure matplotlib for headless environment
plt.switch_backend('Agg')

# Read the JSON data
with open('world_c_results/world_c_job_llama_3_3_1792436123_5a5b_pitchfork_bifurcation_r_sweep_rqa_results.json', 'r') as f:
    raw_content = f.read()
    loaded_json = json.loads(raw_content)
    # The actual data is a list of dictionaries directly
    results = loaded_json

# Extract data
r_values = [res['r_parameter'] for res in results]
rr_values = [res['rqa_metrics']['recurrence_rate'] for res in results]
det_values = [res['rqa_metrics']['determinism'] for res in results]
lam_values = [res['rqa_metrics']['laminarity'] for res in results]
mean_l_values = [res['rqa_metrics']['mean_diag_length'] for res in results]
max_l_values = [res['rqa_metrics']['max_diag_length'] for res in results]
ent_values = [res['rqa_metrics']['shannon_entropy'] for res in results]

# Create plots
fig, axs = plt.subplots(6, 1, figsize=(10, 18), sharex=True)

axs[0].plot(r_values, rr_values)
axs[0].set_ylabel('Recurrence Rate')
axs[0].set_title('RQA Metrics for Pitchfork Bifurcation across R values')

axs[1].plot(r_values, det_values)
axs[1].set_ylabel('Determinism')

axs[2].plot(r_values, lam_values)
axs[2].set_ylabel('Laminarity')

axs[3].plot(r_values, mean_l_values)
axs[3].set_ylabel('Mean Diagonal Length')

axs[4].plot(r_values, max_l_values)
axs[4].set_ylabel('Max Diagonal Length')

axs[5].plot(r_values, ent_values)
axs[5].set_ylabel('Shannon Entropy')
axs[5].set_xlabel('R Parameter')

plt.tight_layout()
plt.savefig('pitchfork_bifurcation_r_sweep_rqa.png')

print("Plot 'pitchfork_bifurcation_r_sweep_rqa.png' generated successfully.")
