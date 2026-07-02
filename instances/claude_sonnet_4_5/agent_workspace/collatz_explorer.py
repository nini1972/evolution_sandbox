
def collatz_sequence(n):
    sequence = [n]
    while n != 1:
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
        sequence.append(n)
    return sequence

import matplotlib.pyplot as plt

if __name__ == "__main__":
    start_numbers = range(1, 101) # Explore sequences for starting numbers 1 to 100
    sequence_lengths = []

    for start_num in start_numbers:
        seq = collatz_sequence(start_num)
        sequence_lengths.append(len(seq))
        # Optional: print sequence and length for detailed view
        # print(f"Collatz sequence for {start_num}: {seq}")
        # print(f"Length of sequence: {len(seq)}\n")

    # Plotting the sequence lengths
    plt.figure(figsize=(12, 6))
    plt.plot(list(start_numbers), sequence_lengths, marker='o', linestyle='-', markersize=4)
    plt.title('Collatz Sequence Lengths for Starting Numbers 1-100')
    plt.xlabel('Starting Number')
    plt.ylabel('Sequence Length')
    plt.grid(True)
    plt.savefig('collatz_sequence_lengths.png')
    print("Generated collatz_sequence_lengths.png")
