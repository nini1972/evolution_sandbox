import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import re

def plot_sequence_length_distribution(md_filename='collatz_properties_analysis.md', plot_filename='collatz_sequence_length_distribution.png'):
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

    # Plotting the histogram of Sequence Length
    plt.figure(figsize=(10, 6))
    plt.hist(df['Sequence Length'], bins=20, edgecolor='black')
    plt.title('Distribution of Collatz Sequence Lengths (N=1-100)')
    plt.xlabel('Sequence Length')
    plt.ylabel('Frequency')
    plt.grid(axis='y', alpha=0.75)
    plt.tight_layout()
    plt.savefig(plot_filename)
    print(f"Generated sequence length distribution plot to {plot_filename}")

if __name__ == '__main__':
    plot_sequence_length_distribution()
