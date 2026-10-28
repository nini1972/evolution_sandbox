
import matplotlib.pyplot as plt
import json
import pandas as pd

# Configure matplotlib for headless environment
plt.switch_backend('Agg')

# Load the RQA results from the JSON file
with open('eeg_af3_rqa_tau_sweep_results.json', 'r') as f:
    rqa_results = json.load(f)

# Convert to DataFrame for easier plotting
df_results = pd.DataFrame(rqa_results)

# Define metrics to plot
metrics_to_plot = ['recurrence_rate', 'determinism', 'laminarity', 'shannon_entropy']

plt.figure(figsize=(15, 10))

for metric in metrics_to_plot:
    plt.plot(df_results['tau'], df_results[metric], marker='o', label=metric)

plt.title('RQA Metrics vs. Tau for Neural EEG AF3 Channel')
plt.xlabel('Time Delay (tau)')
plt.ylabel('Metric Value')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('eeg_af3_rqa_tau_sweep_plot.png')
plt.close()

print('RQA metrics vs. tau plot saved as eeg_af3_rqa_tau_sweep_plot.png')
