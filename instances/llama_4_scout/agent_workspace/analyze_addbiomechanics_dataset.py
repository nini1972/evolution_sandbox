import pandas as pd

# Load the AddBiomechanics Dataset
df = pd.read_csv('addbiomechanics_dataset.csv')

# Analyze the dataset
print(df.head())
print(df.info())
print(df.describe())