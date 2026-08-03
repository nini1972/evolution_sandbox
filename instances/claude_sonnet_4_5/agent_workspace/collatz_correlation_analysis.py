import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import re

def analyze_collatz_correlations(md_filename='collatz_properties_analysis.md', plot_filename='collatz_correlation_heatmap.png'):
    # Read the markdown file
    with open(md_filename, 'r') as f:
        content = f.readlines()

    # Find the table header and data
    header_line = None
    data_lines = []
    for i, line in enumerate(content):
        if "| N | Max Value | Sequence Length | Fall Length |" in line:
            header_line = i
        elif header_line is not None and i > header_line + 1 and line.strip():
            data_lines.append(line)

    if header_line is None:
        print("Could not find data table in markdown file.")
        return

    # Parse header
    headers = [h.strip() for h in content[header_line].split('|') if h.strip()]

    # Parse data
    data = []
    for line in data_lines:
        values = [int(v.strip()) for v in line.split('|') if v.strip()]
        data.append(values)

    df = pd.DataFrame(data, columns=headers)

    # Calculate correlation matrix
    correlation_matrix = df.corr()

    # Plotting the heatmap
    plt.figure(figsize=(8, 6))
    plt.imshow(correlation_matrix, cmap='coolwarm', annot=True, fmt=".2f", linewidths=.5)
    plt.xticks(range(len(correlation_matrix.columns)), correlation_matrix.columns, rotation=45, ha='right')
    plt.yticks(range(len(correlation_matrix.columns)), correlation_matrix.columns)
    plt.title('Collatz Properties Correlation Matrix (N=1-100)')
    plt.colorbar(label='Correlation Coefficient')
    plt.tight_layout()
    plt.savefig(plot_filename)
    print(f"Generated correlation heatmap to {plot_filename}")

if __name__ == '__main__':
    analyze_collatz_correlations()
