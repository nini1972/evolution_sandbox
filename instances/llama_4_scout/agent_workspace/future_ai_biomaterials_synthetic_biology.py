import matplotlib.pyplot as plt
import numpy as np

# Data for plotting
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Create the plot
plt.plot(x, y)

# Save the plot to a file
plt.savefig('future_ai_biomaterials_synthetic_biology.png')