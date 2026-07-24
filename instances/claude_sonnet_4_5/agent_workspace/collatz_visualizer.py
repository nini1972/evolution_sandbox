import pandas as pd
import matplotlib.pyplot as plt
import os

# Set the matplotlib backend to 'Agg' for non-interactive plotting
import matplotlib
matplotlib.use('Agg')

def plot_collatz_data(filepath, outlier_stopping_number, outlier_max_number):
    """
    Reads Collatz data from a CSV file and generates plots for stopping time
    and maximum value.
    Args:
        filepath (str): The path to the CSV file containing Collatz analysis data.
    """
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return

    base_filename = os.path.splitext(os.path.basename(filepath))[0]

    # Plotting Stopping Times
    plt.figure(figsize=(12, 6))
    plt.scatter(df['Starting Number'], df['Stopping Time'], s=5, alpha=0.7, label='All Numbers')
    if not outlier_stopping_number.empty:
        plt.scatter(outlier_stopping_number['Starting Number'], outlier_stopping_number['Stopping Time'], s=50, color='red', label='Outliers')
    plt.title(f'Collatz Stopping Times for {base_filename}')
    plt.xlabel('Starting Number')
    plt.ylabel('Stopping Time')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    stopping_time_plot_path = f'{base_filename}_stopping_time.png'
    plt.savefig(stopping_time_plot_path)
    plt.close()
    print(f"Saved stopping time plot to {stopping_time_plot_path}")

    # Plotting Maximum Values
    plt.figure(figsize=(12, 6))
    plt.scatter(df['Starting Number'], df['Max Value'], s=5, alpha=0.7, color='blue', label='All Numbers')
    if not outlier_max_number.empty:
        plt.scatter(outlier_max_number['Starting Number'], outlier_max_number['Max Value'], s=50, color='red', label='Outliers')
    plt.title(f'Collatz Maximum Values for {base_filename}')
    plt.xlabel('Starting Number')
    plt.ylabel('Maximum Value')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    max_value_plot_path = f'{base_filename}_max_value.png'
    plt.savefig(max_value_plot_path)
    plt.close()
    print(f"Saved maximum value plot to {max_value_plot_path}")

def generate_histograms(filepath):
    """
    Generates histograms for 'Stopping Time' and 'Max Value'.
    Args:
        filepath (str): The path to the CSV file containing Collatz analysis data.
    """
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return

    base_filename = os.path.splitext(os.path.basename(filepath))[0]

    # Histogram for Stopping Time
    plt.figure(figsize=(10, 6))
    plt.hist(df['Stopping Time'], bins=50, color='skyblue', edgecolor='black')
    plt.title(f'Distribution of Collatz Stopping Times for {base_filename}')
    plt.xlabel('Stopping Time')
    plt.ylabel('Frequency')
    plt.grid(axis='y', alpha=0.75)
    plt.tight_layout()
    stopping_time_hist_path = f'{base_filename}_stopping_time_hist.png'
    plt.savefig(stopping_time_hist_path)
    plt.close()
    print(f"Saved stopping time histogram to {stopping_time_hist_path}")

    # Histogram for Max Value
    plt.figure(figsize=(10, 6))
    plt.hist(df['Max Value'], bins=50, color='lightcoral', edgecolor='black')
    plt.title(f'Distribution of Collatz Maximum Values for {base_filename}')
    plt.xlabel('Max Value')
    plt.ylabel('Frequency')
    plt.grid(axis='y', alpha=0.75)
    plt.tight_layout()
    max_value_hist_path = f'{base_filename}_max_value_hist.png'
    plt.savefig(max_value_hist_path)
    plt.close()
    print(f"Saved maximum value histogram to {max_value_hist_path}")

def plot_correlation(filepath):
    """
    Generates a scatter plot to visualize the correlation between 'Stopping Time' and 'Max Value'.
    Args:
        filepath (str): The path to the CSV file containing Collatz analysis data.
    """
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return

    base_filename = os.path.splitext(os.path.basename(filepath))[0]

    plt.figure(figsize=(10, 6))
    plt.scatter(df['Stopping Time'], df['Max Value'], alpha=0.7, s=5, color='green')
    plt.title(f'Correlation between Stopping Time and Max Value for {base_filename}')
    plt.xlabel('Stopping Time')
    plt.ylabel('Max Value')
    plt.grid(True)
    plt.tight_layout()
    correlation_plot_path = f'{base_filename}_correlation.png'
    plt.savefig(correlation_plot_path)
    plt.close()
    print(f"Saved correlation plot to {correlation_plot_path}")

if __name__ == "__main__":
    data_file = "collatz_analysis_1_to_10000.csv"
    try:
        df = pd.read_csv(data_file)
    except FileNotFoundError:
        print(f"Error: File not found at {data_file}")
    
    top_percentile_stopping_time = df['Stopping Time'].quantile(0.99)
    outliers_stopping_time = df[df['Stopping Time'] >= top_percentile_stopping_time].sort_values(by='Stopping Time', ascending=False)
    
    top_percentile_max_value = df['Max Value'].quantile(0.99)
    outliers_max_value = df[df['Max Value'] >= top_percentile_max_value].sort_values(by='Max Value', ascending=False)
    
    plot_collatz_data(data_file, outliers_stopping_time, outliers_max_value)
    generate_histograms(data_file)
    plot_correlation(data_file)
