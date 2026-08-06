import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import re

def plot_sequence_length_distribution(csv_filename='collatz_analysis_1_to_10000.csv', plot_filename='collatz_sequence_length_distribution_N10000.png'):
    df = pd.read_csv(csv_filename)

    # Plotting the histogram of Sequence Length
    plt.figure(figsize=(10, 6))
    plt.hist(df['Sequence Length'], bins=20, edgecolor='black')
    plt.title('Distribution of Collatz Sequence Lengths (N=1-10000)')
    plt.xlabel('Sequence Length')
    plt.ylabel('Frequency')
    plt.grid(axis='y', alpha=0.75)
    plt.tight_layout()
    plt.savefig(plot_filename)
    print(f"Generated sequence length distribution plot to {plot_filename}")

if __name__ == '__main__':
    plot_sequence_length_distribution()
