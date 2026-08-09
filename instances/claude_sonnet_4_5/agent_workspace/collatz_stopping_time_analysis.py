import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def analyze_collatz_stopping_time(csv_filename='collatz_analysis_1_to_20000.csv', plot_filename='collatz_stopping_time_vs_n_N20000.png'):
    df = pd.read_csv(csv_filename)

    # Plotting the stopping time vs N
    plt.figure(figsize=(12, 7))
    plt.scatter(df['Starting Number'], df['Stopping Time'], s=10)
    plt.title('Collatz Stopping Time vs. Starting Number N (1-20000)')
    plt.xlabel('Starting Number (N)')
    plt.ylabel('Stopping Time (Number of Steps to reach 1)')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(plot_filename)
    print(f"Generated plot of stopping time vs N to {plot_filename}")

if __name__ == '__main__':
    analyze_collatz_stopping_time()
