from colony_lib.datasets import load_dataset
import matplotlib.pyplot as plt

# Load the solar_sunspots dataset
dataset = load_dataset('solar_sunspots')

# Plot the dataset
plt.figure(figsize=(10, 6))
plt.plot(dataset)
plt.title('Solar Sunspots Dataset')
plt.xlabel('Time')
plt.ylabel('Sunspots')
plt.grid(True)
plt.savefig('solar_sunspots.png')
