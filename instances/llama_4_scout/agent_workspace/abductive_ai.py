import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Load data from a sample dataset
data = pd.read_csv('sample_data.csv')

# Process data
# Visualize data
print(data.head())
plt.scatter(data['id'], data['value'])
plt.show()