import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# Load data from a CSV file
data = pd.read_csv('sample_data.csv')

# Perform PCA
pca = PCA(n_components=2)
df_pca = pca.fit_transform(data)

# Visualize the results
plt.scatter(df_pca[:, 0], df_pca[:, 1])
plt.savefig('pca_results.png')