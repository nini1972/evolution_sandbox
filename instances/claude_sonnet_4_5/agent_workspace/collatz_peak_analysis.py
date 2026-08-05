import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def collatz_sequence(n):
    sequence = [n]
    while n != 1:
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
        sequence.append(n)
    return sequence

def count_peaks(sequence):
    if len(sequence) < 3:
        return 0
    peaks = 0
    for i in range(1, len(sequence) - 1):
        if sequence[i] > sequence[i-1] and sequence[i] > sequence[i+1]:
            peaks += 1
    return peaks

def analyze_collatz_peaks(start_n=1, end_n=10000, plot_filename='collatz_peaks_vs_n_N10000.png'):
    n_values = []
    peak_counts = []

    for n in range(start_n, end_n + 1):
        sequence = collatz_sequence(n)
        num_peaks = count_peaks(sequence)
        n_values.append(n)
        peak_counts.append(num_peaks)

    df = pd.DataFrame({'N': n_values, 'Number of Peaks': peak_counts})

    # Plotting the number of peaks vs N
    plt.figure(figsize=(12, 7))
    plt.scatter(df['N'], df['Number of Peaks'], s=10)
    plt.title('Number of Peaks in Collatz Sequence vs. Starting Number N (1-10000)')
    plt.xlabel('Starting Number (N)')
    plt.ylabel('Number of Peaks')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(plot_filename)
    print(f"Generated plot of number of peaks vs N to {plot_filename}")

if __name__ == '__main__':
    analyze_collatz_peaks()
