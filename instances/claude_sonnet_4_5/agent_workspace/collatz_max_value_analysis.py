import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def analyze_max_values(csv_filename='collatz_analysis_1_to_20000.csv', plot_filename='collatz_max_value_vs_n_N20000.png'):
    df = pd.read_csv(csv_filename)

    plt.figure(figsize=(12, 7))
    plt.scatter(df['Starting Number'], df['Max Value'], s=10)
    plt.title('Maximum Value in Collatz Sequence vs. Starting Number N (1-20000)')
    plt.xlabel('Starting Number (N)')
    plt.ylabel('Maximum Value Reached')
    plt.yscale('log') # Max values can vary greatly, so a log scale is appropriate
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(plot_filename)
    print(f"Generated plot of maximum value vs N to {plot_filename}")

if __name__ == '__main__':
    analyze_max_values()