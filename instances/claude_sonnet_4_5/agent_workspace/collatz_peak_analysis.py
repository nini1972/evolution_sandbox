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

def analyze_collatz_peaks(csv_filename='collatz_analysis_1_to_20000.csv', plot_filename='collatz_peaks_vs_n_N20000.png'):
    df = pd.read_csv(csv_filename)
    # The collatz_sequence and count_peaks functions need to be defined outside this function or passed in if they are not global
    # For now, let's assume they are globally available or will be defined above this function.
    df['Number of Peaks'] = df['Starting Number'].apply(lambda x: count_peaks(collatz_sequence(x)))

    # Plotting the number of peaks vs N
    plt.figure(figsize=(12, 7))
    plt.scatter(df['Starting Number'], df['Number of Peaks'], s=10)
    plt.title('Number of Peaks in Collatz Sequence vs. Starting Number N (1-20000)')
    plt.xlabel('Starting Number (N)')
    plt.ylabel('Number of Peaks')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(plot_filename)
    print(f"Generated plot of number of peaks vs N to {plot_filename}")

if __name__ == '__main__':
    analyze_collatz_peaks()
