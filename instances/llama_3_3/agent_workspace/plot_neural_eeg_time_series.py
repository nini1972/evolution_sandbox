
import matplotlib.pyplot as plt
from colony_lib.datasets import load_dataset
import pandas as pd

# Configure matplotlib for headless environment
plt.switch_backend('Agg')

# Load the neural_eeg dataset
ds = load_dataset("neural_eeg")

# Convert to pandas DataFrame
df = pd.DataFrame(ds["data"], columns=ds["columns"])

# Select a few channels to plot
channels_to_plot = ['AF3', 'F3', 'P7']

# Plot a segment of the time series (e.g., first 500 data points)
segment_length = 500

plt.figure(figsize=(15, 8))
for channel in channels_to_plot:
    plt.plot(df[channel].head(segment_length), label=channel)

plt.title('Selected Neural EEG Channels Time Series')
plt.xlabel('Time Steps')
plt.ylabel('Amplitude')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('neural_eeg_time_series.png')
plt.close()

print(f"Neural EEG time series plot saved as neural_eeg_time_series.png for channels {channels_to_plot}")
