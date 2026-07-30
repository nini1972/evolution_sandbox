import matplotlib
# Use the Agg backend for headless environments
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def collatz_sequence_binary_visualization(n, filename='collatz_binary_pattern.png'):
    sequence_binary_lists = []
    current_n = n
    max_len = 0

    print(f"Starting visualization for n = {n}")

    while current_n != 1:
        binary_str = bin(current_n)[2:] # Remove '0b' prefix
        sequence_binary_lists.append([int(bit) for bit in binary_str])
        max_len = max(max_len, len(binary_str))

        if current_n % 2 == 0:
            current_n = current_n // 2
        else:
            current_n = (3 * current_n) + 1
    
    # Add the final '1'
    binary_str = bin(current_n)[2:]
    sequence_binary_lists.append([int(bit) for bit in binary_str])
    max_len = max(max_len, len(binary_str))

    # Pad shorter binary strings with leading zeros to match max_len
    padded_sequences = []
    for seq_list in sequence_binary_lists:
        padded_sequences.append([0] * (max_len - len(seq_list)) + seq_list)

    # Convert to numpy array for visualization
    matrix = np.array(padded_sequences)

    plt.figure(figsize=(max_len * 0.2, len(padded_sequences) * 0.2)) # Adjust figure size dynamically
    plt.imshow(matrix, cmap='binary', aspect='auto', origin='upper')
    plt.title(f'Collatz Binary Pattern for N={n}')
    plt.xlabel('Bit Position')
    plt.ylabel('Step in Sequence')
    plt.colorbar(label='Bit Value (0 or 1)')
    plt.savefig(filename)
    plt.close()
    print(f"Visualization saved to {filename}")

# Test with n=27, saving the output to a file.
collatz_sequence_binary_visualization(27, 'collatz_binary_pattern_27.png')
collatz_sequence_binary_visualization(97, 'collatz_binary_pattern_97.png') # another test value
collatz_sequence_binary_visualization(101, 'collatz_binary_pattern_101.png') # another test value

