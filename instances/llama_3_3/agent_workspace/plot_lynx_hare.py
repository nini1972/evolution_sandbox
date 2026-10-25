
import matplotlib.pyplot as plt
from colony_lib.datasets import load_dataset
import pandas as pd

# Configure matplotlib for headless environment
plt.switch_backend('Agg')

# Load the lynx_hare dataset
ds = load_dataset("lynx_hare")

# Convert to pandas DataFrame for easier plotting
df = pd.DataFrame(ds["data"], columns=ds["columns"])

# Create the plot
plt.figure(figsize=(10, 6))
plt.plot(df['year'], df['hare'], label='Hare Population', color='blue')
plt.plot(df['year'], df['lynx'], label='Lynx Population', color='red')

# Add labels and title
plt.xlabel('Year')
plt.ylabel('Population (thousands)')
plt.title('Lynx-Hare Predator-Prey Cycle')
plt.legend()
plt.grid(True)

# Save the plot to a file
plt.savefig('lynx_hare_cycle.png')
plt.close()

print("Lynx-hare cycle plot saved as lynx_hare_cycle.png")
