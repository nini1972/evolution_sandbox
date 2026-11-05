from colony_lib.datasets import load_dataset
import matplotlib.pyplot as plt

# Load the dataset
ds = load_dataset('power_grid_ieee')

# Plot the first feature
plt.figure(figsize=(10, 6))
plt.plot(ds[:, 0])
plt.title('Power Grid IEEE Dataset - First Feature')
plt.xlabel('Time')
plt.ylabel('Value')
plt.savefig('power_grid_ieee_feature0.png')