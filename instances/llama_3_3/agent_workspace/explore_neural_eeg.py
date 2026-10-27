
from colony_lib.datasets import load_dataset
import pandas as pd

# Load the neural_eeg dataset
ds = load_dataset("neural_eeg")

# Convert to pandas DataFrame for inspection
df = pd.DataFrame(ds["data"], columns=ds["columns"])

print("--- Head of neural_eeg dataset ---")
print(df.head())

print("\n--- Description of neural_eeg dataset ---")
print(df.describe())
