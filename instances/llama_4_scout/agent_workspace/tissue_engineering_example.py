import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# Generate a random dataset
data = np.random.rand(100, 10)
df = pd.DataFrame(data, columns=[f'feature_{i}' for i in range(10)])

# Perform PCA
pca = PCA(n_components=2)
df_pca = pca.fit_transform(df)

# Visualize the results
plt.scatter(df_pca[:, 0], df_pca[:, 1])
plt.show()