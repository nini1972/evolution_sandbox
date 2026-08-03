
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def collatz_sequence(n):
    sequence = [n]
    while n != 1:
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
        sequence.append(n)
    return sequence

def plot_collatz_binary(n, filename=None):
    sequence = collatz_sequence(n)
    binary_representations = [bin(x)[2:] for x in sequence]

    max_len = max(len(b) for b in binary_representations)
    padded_binary_representations = [b.zfill(max_len) for b in binary_representations]

    # Create a 2D array for the image
    # Rows are steps, columns are bit positions
    image_data = np.zeros((len(padded_binary_representations), max_len))

    for i, binary_str in enumerate(padded_binary_representations):
        for j, bit in enumerate(binary_str):
            image_data[i, j] = int(bit)

    plt.figure(figsize=(12, 8))
    plt.imshow(image_data, cmap='gray_r', aspect='auto') # gray_r makes 1s black and 0s white
    plt.title(f'Binary Representation of Collatz Sequence for n={n}')
    plt.xlabel('Bit Position')
    plt.ylabel('Step in Sequence')
    plt.colorbar(label='Bit Value (0 or 1)')
    plt.tight_layout()
    if filename:
        plt.savefig(filename)
    else:
        plt.show()

def analyze_collatz_properties(n_start, n_end, md_filename='collatz_properties_analysis.md', plot_filename_max_val='collatz_max_value.png', plot_filename_fall_len='collatz_fall_length.png'):
    results = {}
    for n in range(n_start, n_end + 1):
        sequence = collatz_sequence(n)
        initial_value = n
        max_value = max(sequence)
        
        # Calculate fall length (steps until the first value smaller than initial_value)
        fall_length = 0
        for i, val in enumerate(sequence):
            if val < initial_value and i > 0: # Ensure we don't count the initial value itself
                fall_length = i
                break
        else: # If loop completes without breaking, it means no fall below initial_value occurred
            fall_length = len(sequence) - 1 # The entire sequence length until 1

        results[n] = {
            'max_value': max_value,
            'sequence_length': len(sequence),
            'fall_length': fall_length
        }

    # Plotting Max Value vs. N
    plt.figure(figsize=(12, 6))
    plt.plot(list(results.keys()), [data['max_value'] for data in results.values()], marker='o', linestyle='-')
    plt.title(f'Max Value in Collatz Sequence for N from {n_start} to {n_end}')
    plt.xlabel('N')
    plt.ylabel('Max Value')
    plt.grid(True)
    plt.yscale('log') # Use log scale for better visualization of large max values
    plt.tight_layout()
    plt.savefig(plot_filename_max_val)
    print(f"Generated {plot_filename_max_val}")

    # Plotting Fall Length vs. N
    plt.figure(figsize=(12, 6))
    plt.plot(list(results.keys()), [data['fall_length'] for data in results.values()], marker='o', linestyle='-')
    plt.title(f'Fall Length of Collatz Sequence for N from {n_start} to {n_end}')
    plt.xlabel('N')
    plt.ylabel('Fall Length')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(plot_filename_fall_len)
    print(f"Generated {plot_filename_fall_len}")

    with open(md_filename, 'w') as f:
        f.write(f"# Collatz Fall Analysis for N from {n_start} to {n_end}\n\n")
        f.write("| N | Max Value | Sequence Length | Fall Length |\n")
        f.write("|---|-----------|-----------------|-------------|\n")
        for n, data in results.items():
            f.write(f"| {n} | {data['max_value']} | {data['sequence_length']} | {data['fall_length']} |\n")

    print(f"Collatz fall analysis saved to {md_filename}")

if __name__ == '__main__':
    # Example usage for binary visualization
    n_value = 27
    plot_collatz_binary(n_value, filename=f'collatz_binary_n_{n_value}.png')
    print(f"Generated collatz_binary_n_{n_value}.png")

    # Example usage for fall analysis
    analyze_collatz_properties(1, 100)
    print("Collatz properties analysis completed.")
