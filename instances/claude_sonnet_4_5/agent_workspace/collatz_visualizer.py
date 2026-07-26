import pandas as pd
import matplotlib.pyplot as plt
import sys

# Configure matplotlib for headless environments
plt.switch_backend('Agg')

def generate_visualizations(filepath):
    """
    Generates and saves visualizations for Collatz data.
    Args:
        filepath (str): The path to the CSV file containing Collatz analysis data.
    """
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return

    print(f"\n--- Generating Visualizations for {filepath} ---")

    # 1. Histogram of Stopping Time
    plt.figure(figsize=(10, 6))
    plt.hist(df['Stopping Time'], bins=50, color='skyblue', edgecolor='black')
    plt.title('Distribution of Collatz Stopping Times')
    plt.xlabel('Stopping Time')
    plt.ylabel('Frequency')
    plt.grid(axis='y', alpha=0.75)
    plt.savefig('stopping_time_histogram.png')
    plt.close()
    print("Saved stopping_time_histogram.png")

    # 2. Histogram of Max Value
    plt.figure(figsize=(10, 6))
    plt.hist(df['Max Value'], bins=50, color='lightcoral', edgecolor='black')
    plt.title('Distribution of Collatz Max Values')
    plt.xlabel('Max Value')
    plt.ylabel('Frequency')
    plt.grid(axis='y', alpha=0.75)
    plt.savefig('max_value_histogram.png')
    plt.close()
    print("Saved max_value_histogram.png")

    # 3. Scatter Plot: Starting Number vs. Stopping Time with Max Value as Color
    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(df['Starting Number'], df['Stopping Time'],
                            c=df['Max Value'], cmap='viridis', alpha=0.7,
                            s=10) # s is marker size
    plt.colorbar(scatter, label='Max Value in Sequence')
    plt.title('Collatz: Starting Number vs. Stopping Time (Colored by Max Value)')
    plt.xlabel('Starting Number')
    plt.ylabel('Stopping Time')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.savefig('starting_number_vs_stopping_time_scatter.png')
    plt.close()
    print("Saved starting_number_vs_stopping_time_scatter.png")

if __name__ == "__main__":
    data_file = "collatz_analysis_1_to_10000.csv"
    generate_visualizations(data_file)
