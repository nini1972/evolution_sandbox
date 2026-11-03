import matplotlib.pyplot as plt
from colony_lib.datasets import load_dataset

ds = load_dataset("climate_enso")
plt.plot(ds.data[:, 0])
plt.xlabel('Time')
plt.ylabel('Feature 0 Value')
plt.title('First Feature of climate_enso Dataset')
plt.savefig('climate_enso_feature0.png')