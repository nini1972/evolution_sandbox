import sys

def collatz_sequence(n):
    """
    Generates the Collatz sequence for a given starting number n.
    Args:
        n (int): The starting number.
    Returns:
        tuple: A tuple containing the sequence list, stopping time, and max value.
    """
    if n <= 0:
        raise ValueError("Starting number must be a positive integer.")

    sequence = [n]
    max_value = n
    steps = 0

    while n != 1:
        if n % 2 == 0:
            n //= 2
        else:
            n = 3 * n + 1
        sequence.append(n)
        if n > max_value:
            max_value = n
        steps += 1
    return sequence, steps, max_value

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python collatz_sequence_viewer.py <starting_number>")
        sys.exit(1)

    try:
        start_num = int(sys.argv[1])
        if start_num <= 0:
            raise ValueError
    except (ValueError, IndexError):
        print("Please provide a positive integer as the starting number.")
        sys.exit(1)

    seq, stopping_time, max_val = collatz_sequence(start_num)

    print(f"\n--- Collatz Sequence for {start_num} ---")
    print(f"Sequence: {seq}")
    print(f"Stopping Time: {stopping_time}")
    print(f"Maximum Value: {max_val}")
