import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def collatz_sequence_and_stopping_time(n):
    sequence = [n]
    steps = 0
    while n != 1:
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
        sequence.append(n)
        steps += 1
    return sequence, steps

def analyze_collatz_stopping_time(start_n=1, end_n=100, plot_filename='collatz_stopping_time_vs_n.png'):
    n_values = []
    stopping_times = []

    for n in range(start_n, end_n + 1):
        _, steps = collatz_sequence_and_stopping_time(n)
        n_values.append(n)
        stopping_times.append(steps)

    df = pd.DataFrame({'N': n_values, 'Stopping Time': stopping_times})

    # Plotting the stopping time vs N
    plt.figure(figsize=(12, 7))
    plt.scatter(df['N'], df['Stopping Time'], s=10)
    plt.title('Collatz Stopping Time vs. Starting Number N (1-100)')
    plt.xlabel('Starting Number (N)')
    plt.ylabel('Stopping Time (Number of Steps to reach 1)')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(plot_filename)
    print(f"Generated plot of stopping time vs N to {plot_filename}")

if __name__ == '__main__':
    analyze_collatz_stopping_time()
