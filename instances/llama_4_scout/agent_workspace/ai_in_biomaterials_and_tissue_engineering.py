import matplotlib.pyplot as plt
import numpy as np

# Data for plotting
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Create the plot
plt.plot(x, y)

# Save the plot to a file
plt.savefig('ai_in_biomaterials_and_tissue_engineering.png')