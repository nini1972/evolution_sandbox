import sys

def collatz(n):
    """Generate the Collatz sequence starting at n until it reaches 1."""
    sequence = [n]
    while n > 1:
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
        sequence.append(n)
    return sequence

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            start_num = int(sys.argv[1])
        except ValueError:
            print("Please provide a valid integer.")
            sys.exit(1)
    else:
        start_num = 27  # Default to a classic interesting starting number
        
    print(f"Generating Collatz sequence for n = {start_num}...")
    seq = collatz(start_num)
    print(f"Sequence: {seq}")
    print(f"Stopping time (steps to reach 1): {len(seq) - 1}")
