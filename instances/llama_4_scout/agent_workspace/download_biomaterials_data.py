import pandas as pd
import os

# Download dataset
url = 'https://raw.githubusercontent.com/BasedLabs/bio-datasets/main/bio_datasets.csv'
dataset = pd.read_csv(url)

# Save dataset to local file
dataset.to_csv('biomaterials_data.csv', index=False)