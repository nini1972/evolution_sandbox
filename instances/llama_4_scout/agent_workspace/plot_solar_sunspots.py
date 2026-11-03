from colony_lib.datasets import load_dataset
import matplotlib.pyplot as plt

# Load the dataset
ds = load_dataset("solar_sunspots")

# Plot the first feature
plt.figure(figsize=(10, 6))
plt.plot(ds[:, 0])
plt.title('Solar Sunspots Dataset - First Feature')
plt.xlabel('Time')
plt.ylabel('Value')
plt.savefig('solar_sunspots_feature0.png')