
import pandas as pd

df = pd.read_csv("sample_data.csv")

print("First 5 rows:")
print(df.head())

print("\nAverage age:")
print(df["age"].mean())

print("\nCharacters per city:")
print(df["city"].value_counts())
