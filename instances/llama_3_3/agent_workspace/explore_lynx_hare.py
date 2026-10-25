
from colony_lib.datasets import load_dataset
import pandas as pd

# Load the lynx_hare dataset
ds = load_dataset("lynx_hare")

# Convert to pandas DataFrame for easier exploration
df = pd.DataFrame(ds["data"], columns=ds["columns"])

# Print the first few rows of the DataFrame
print(df.head())

# Print basic statistics
print(df.describe())
