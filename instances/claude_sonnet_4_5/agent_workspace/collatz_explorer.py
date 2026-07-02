import matplotlib.pyplot as plt

def collatz_sequence(n):
    sequence = [n]
    max_value = n
    while n != 1:
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
        sequence.append(n)
        if n > max_value:
            max_value = n
    return sequence, max_value

if __name__ == "__main__":
    max_number = 100
    lengths = []
    max_values = []

    for i in range(1, max_number + 1):
        sequence_data, current_max_value = collatz_sequence(i)
        lengths.append(len(sequence_data))
        max_values.append(current_max_value)

    # Plotting sequence lengths
    plt.figure(figsize=(12, 6))
    plt.plot(range(1, max_number + 1), lengths, marker="o", linestyle="-", markersize=4)
    plt.title("Collatz Sequence Lengths (1 to {})".format(max_number))
    plt.xlabel("Starting Number")
    plt.ylabel("Sequence Length")
    plt.grid(True)
    plt.savefig("collatz_sequence_lengths.png")
    plt.close()

    # Plotting maximum values reached
    plt.figure(figsize=(12, 6))
    plt.plot(range(1, max_number + 1), max_values, marker="o", linestyle="-", markersize=4, color="red")
    plt.title("Collatz Sequence Maximum Values Reached (1 to {})".format(max_number))
    plt.xlabel("Starting Number")
    plt.ylabel("Maximum Value in Sequence")
    plt.grid(True)
    plt.savefig("collatz_sequence_max_values.png")
    plt.close()

    print("Generated collatz_sequence_lengths.png and collatz_sequence_max_values.png")