import pandas as pd
import matplotlib.pyplot as plt

# Configure matplotlib for headless environment
plt.switch_backend('Agg')

# Load the data
try:
    df = pd.read_csv('sample_data.csv')
    print("Data loaded successfully:")
    print(df.head())

    # Basic information
    print("\nDataFrame Info:")
    df.info()

    print("\nDataFrame Description:")
    print(df.describe())

    # Calculate average age
    average_age = df['age'].mean()
    print(f"\nAverage Age: {average_age:.2f}")

    # Count cities
    city_counts = df['city'].value_counts()
    print("\nCity Counts:")
    print(city_counts)

    # Create a bar chart of ages
    plt.figure(figsize=(8, 4))
    plt.bar(df['name'], df['age'], color='skyblue')
    plt.xlabel('Name')
    plt.ylabel('Age')
    plt.title('Ages of Individuals')
    plt.grid(axis='y', linestyle='--')
    plt.savefig('ages_bar_chart.png')
    print("\n'ages_bar_chart.png' saved successfully.")

    # Create a bar chart of city counts
    plt.figure(figsize=(8, 4))
    city_counts.plot(kind='bar', color='lightcoral')
    plt.xlabel('City')
    plt.ylabel('Number of Individuals')
    plt.title('Number of Individuals per City')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--')
    plt.tight_layout()
    plt.savefig('city_counts_bar_chart.png')
    print("'city_counts_bar_chart.png' saved successfully.")

except FileNotFoundError:
    print("Error: 'sample_data.csv' not found. Please ensure the file is in the current directory.")
except Exception as e:
    print(f"An error occurred: {e}")
