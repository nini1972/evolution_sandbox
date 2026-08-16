import pandas as pd

# Load the data
data = pd.read_csv('biomatdb_analysis_results.csv')

# Print the basic information of the data
print(data.head())
print(data.info())
print(data.describe())