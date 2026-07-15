import matplotlib.pyplot as plt
import os

# Set matplotlib to use the 'Agg' backend for non-interactive plotting
plt.switch_backend('Agg')

def collatz_sequence(n):
    sequence = [n]
    while n != 1:
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
        sequence.append(n)
    return sequence

max_start_number = 100000
sequence_lengths = [len(collatz_sequence(i)) for i in range(1, max_start_number + 1)]
max_values = [max(collatz_sequence(i)) for i in range(1, max_start_number + 1)]

# Plotting sequence lengths
plt.figure(figsize=(12, 6))
plt.plot(range(1, max_start_number + 1), sequence_lengths)
plt.title('Collatz Sequence Lengths')
plt.xlabel('Starting Number')
plt.ylabel('Sequence Length')
plt.grid(True)
plt.savefig('collatz_sequence_lengths.png')
plt.close() # Close the plot to free up memory

# Plotting maximum values in sequences
plt.figure(figsize=(12, 6))
plt.plot(range(1, max_start_number + 1), max_values)
plt.title('Maximum Values in Collatz Sequences')
plt.xlabel('Starting Number')
plt.ylabel('Maximum Value')
plt.grid(True)
plt.savefig('collatz_max_values.png')
plt.close() # Close the plot to free up memory

# Calculate and print average sequence length
average_sequence_length = sum(sequence_lengths) / len(sequence_lengths)

# Calculate and print average maximum value
average_max_value = sum(max_values) / len(max_values)

# Save the print outputs to a file
with open('collatz_stats.txt', 'w') as f:
    f.write(f"Average Collatz sequence length for numbers up to {max_start_number}: {average_sequence_length}\n")
    f.write(f"Average maximum value in Collatz sequences for numbers up to {max_start_number}: {average_max_value}\n")
