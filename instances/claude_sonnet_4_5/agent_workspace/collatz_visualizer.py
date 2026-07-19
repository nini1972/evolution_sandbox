
import pandas as pd
import matplotlib.pyplot as plt
import os

# Set the matplotlib backend to 'Agg' for non-interactive plotting
import matplotlib
matplotlib.use('Agg')

def plot_collatz_data(filepath):
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
    plt.scatter(df['Starting Number'], df['Stopping Time'], s=5, alpha=0.7)
    plt.title(f'Collatz Stopping Times for {base_filename}')
    plt.xlabel('Starting Number')
    plt.ylabel('Stopping Time')
    plt.grid(True)
    plt.tight_layout()
    stopping_time_plot_path = f'{base_filename}_stopping_time.png'
    plt.savefig(stopping_time_plot_path)
    plt.close()
    print(f"Saved stopping time plot to {stopping_time_plot_path}")

    # Plotting Maximum Values
    plt.figure(figsize=(12, 6))
    plt.scatter(df['Starting Number'], df['Max Value'], s=5, alpha=0.7, color='red')
    plt.title(f'Collatz Maximum Values for {base_filename}')
    plt.xlabel('Starting Number')
    plt.ylabel('Maximum Value')
    plt.grid(True)
    plt.tight_layout()
    max_value_plot_path = f'{base_filename}_max_value.png'
    plt.savefig(max_value_plot_path)
    plt.close()
    print(f"Saved maximum value plot to {max_value_plot_path}")

if __name__ == "__main__":
    print("Generating visualizations...")
    
    # Plot for range 1-100
    plot_collatz_data("collatz_analysis_1_to_100.csv")
    
    # Plot and extended analysis for range 1-2000
    filepath_2000 = "collatz_analysis_1_to_2000.csv"
    plot_collatz_data(filepath_2000)
    generate_histograms(filepath_2000)
    plot_correlation(filepath_2000)
