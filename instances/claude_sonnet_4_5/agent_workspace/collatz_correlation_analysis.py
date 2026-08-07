import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import re

def analyze_collatz_correlations(csv_filename='collatz_analysis_1_to_10000.csv', plot_filename='collatz_correlation_heatmap_N10000.png'):
    df = pd.read_csv(csv_filename)

    # Calculate correlation matrix
    correlation_matrix = df.corr()

    # Plotting the heatmap
    plt.figure(figsize=(8, 6))
    ax = sns.heatmap(correlation_matrix, cmap='coolwarm', annot=True, fmt=".2f", linewidths=.5)
    plt.xticks(range(len(correlation_matrix.columns)), correlation_matrix.columns, rotation=45, ha='right')
    plt.yticks(range(len(correlation_matrix.columns)), correlation_matrix.columns)
    plt.title('Collatz Properties Correlation Matrix (N=1-10000)')
    cbar = ax.collections[0].colorbar
    cbar.set_label('Correlation Coefficient')
    plt.tight_layout()
    plt.savefig(plot_filename)
    print(f"Generated correlation heatmap to {plot_filename}")

if __name__ == '__main__':
    analyze_collatz_correlations()
