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
    max_number = 1000
    all_sequences = {}
    lengths = []
    max_values = []

    for i in range(1, max_number + 1):
        sequence_data, current_max_value = collatz_sequence(i)
        all_sequences[i] = sequence_data # Store the full sequence
        lengths.append(len(sequence_data))
        max_values.append(current_max_value)

    with open("collatz_data.txt", "w") as f:
        f.write(f"Collatz Conjecture Data for numbers up to {max_number}\n")
        f.write("--------------------------------------------------\n")
        for i in range(1, max_number + 1):
            f.write(f"Starting Number: {i}\n")
            f.write(f"  Sequence Length: {lengths[i-1]}\n")
            f.write(f"  Maximum Value: {max_values[i-1]}\n")
            f.write(f"  Sequence: {all_sequences[i]}\n")
            f.write("\n")
    print("Generated collatz_data.txt")