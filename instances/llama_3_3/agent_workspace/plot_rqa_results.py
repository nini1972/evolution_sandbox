import json
import matplotlib.pyplot as plt
import numpy as np

# Configure matplotlib for headless environment
plt.switch_backend('Agg')

# Load the RQA results from the JSON file
file_path = "world_c_results/world_c_job_llama_3_3_1792807827_0a72_pitchfork_bifurcation_r_sweep_rqa_granular_results.json"
with open(file_path, 'r') as f:
    rqa_data = json.load(f)

# The actual data is nested under a 'result' key, if it came from the check_world_c_job response
# If it's directly from read_file, it might not have this extra nesting. Let's check.
if isinstance(rqa_data, dict) and 'result' in rqa_data:
    rqa_results = rqa_data['result']
else:
    rqa_results = rqa_data

# Extract data for plotting
r_values = [d['r'] for d in rqa_results]
RR_values = [d['RR'] for d in rqa_results]
DET_values = [d['DET'] for d in rqa_results]
LAM_values = [d['LAM'] for d in rqa_results]
L_values = [d['L'] for d in rqa_results]
Lmax_values = [d['Lmax'] for d in rqa_results]
ENT_values = [d['ENT'] for d in rqa_results]
std_dev_values = [d['std_dev'] for d in rqa_results]

# Create plots
fig, axs = plt.subplots(7, 1, figsize=(12, 28), sharex=True)
fig.suptitle('RQA Metrics vs. Logistic Map Parameter (r)', fontsize=16)

axs[0].plot(r_values, RR_values, label='Recurrence Rate (RR)', color='blue')
axs[0].set_ylabel('RR')
axs[0].legend()
axs[0].grid(True)

axs[1].plot(r_values, DET_values, label='Determinism (DET)', color='green')
axs[1].set_ylabel('DET')
axs[1].legend()
axs[1].grid(True)

axs[2].plot(r_values, LAM_values, label='Laminarity (LAM)', color='red')
axs[2].set_ylabel('LAM')
axs[2].legend()
axs[2].grid(True)

axs[3].plot(r_values, L_values, label='Mean Diagonal Line Length (L)', color='purple')
axs[3].set_ylabel('L')
axs[3].legend()
axs[3].grid(True)

axs[4].plot(r_values, Lmax_values, label='Maximum Diagonal Line Length (Lmax)', color='orange')
axs[4].set_ylabel('Lmax')
axs[4].legend()
axs[4].grid(True)

axs[5].plot(r_values, ENT_values, label='Shannon Entropy (ENT)', color='brown')
axs[5].set_ylabel('ENT')
axs[5].legend()
axs[5].grid(True)

axs[6].plot(r_values, std_dev_values, label='Standard Deviation of Series', color='black', linestyle='--')
axs[6].set_ylabel('Std Dev')
axs[6].set_xlabel('Parameter r')
axs[6].legend()
axs[6].grid(True)

plt.tight_layout(rect=[0, 0.03, 1, 0.96])

# Save the plot
plot_filename = "rqa_metrics_logistic_map_bifurcation.png"
plt.savefig(plot_filename)
print(f"RQA metrics plot saved to {plot_filename}")

# Also create a simple bifurcation diagram based on the timeseries itself.
# We can reuse the `r_values` and `x_series` logic from the World C script to reconstruct it for plotting.
# This might be too computationally heavy for the local environment given the number of points.
# Let's just focus on the RQA plots for now and confirm those are correct.

# Optional: Generate a traditional bifurcation diagram if needed later.
