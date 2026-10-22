import json
import matplotlib.pyplot as plt
import numpy as np

# Configure matplotlib for headless environment
plt.switch_backend('Agg')

# Load the RQA results
results_file = 'world_c_results/pitchfork_bifurcation_r_sweep_rqa_granular_results.json'
with open(results_file, 'r') as f:
    data = json.load(f)

# Extract data
r_values = [d['r'] for d in data]
rr_values = [d['RR'] for d in data]
det_values = [d['DET'] for d in data]
lam_values = [d['LAM'] for d in data]
l_values = [d['L'] for d in data]
lmax_values = [d['Lmax'] for d in data]
ent_values = [d['ENT'] for d in data]
std_dev_values = [d['std_dev'] for d in data]

# Create plots
fig, axes = plt.subplots(7, 1, figsize=(12, 24), sharex=True)
fig.suptitle('Granular RQA Metrics for Logistic Map Pitchfork Bifurcation', fontsize=16)

axes[0].plot(r_values, rr_values, label='Recurrence Rate (RR)', color='blue')
axes[0].set_ylabel('RR')
axes[0].legend()
axes[0].grid(True)

axes[1].plot(r_values, det_values, label='Determinism (DET)', color='green')
axes[1].set_ylabel('DET')
axes[1].legend()
axes[1].grid(True)

axes[2].plot(r_values, lam_values, label='Laminarity (LAM)', color='red')
axes[2].set_ylabel('LAM')
axes[2].legend()
axes[2].grid(True)

axes[3].plot(r_values, l_values, label='Mean Diagonal Length (L)', color='purple')
axes[3].set_ylabel('L')
axes[3].legend()
axes[3].grid(True)

axes[4].plot(r_values, lmax_values, label='Max Diagonal Length (Lmax)', color='orange')
axes[4].set_ylabel('Lmax')
axes[4].legend()
axes[4].grid(True)

axes[5].plot(r_values, ent_values, label='Shannon Entropy (ENT)', color='brown')
axes[5].set_ylabel('ENT')
axes[5].legend()
axes[5].grid(True)

axes[6].plot(r_values, std_dev_values, label='Standard Deviation (std_dev)', color='black')
axes[6].set_ylabel('Std Dev')
axes[6].legend()
axes[6].grid(True)
axes[6].set_xlabel('Parameter r')

plt.tight_layout(rect=[0, 0.03, 1, 0.96])

# Save the plot
output_plot_filename = 'pitchfork_bifurcation_r_sweep_rqa_granular.png'
plt.savefig(output_plot_filename)
print(f"Plot saved to {output_plot_filename}")
