def collatz_binary_sequence(n):
    """
    Generates the Collatz sequence for a given number, showing its binary representation at each step.
    """
    print(f"Exploring Collatz sequence for starting number: {n}")
    print(f"Binary: {bin(n)}")
    print("--------------------------------------------------")

    while n != 1:
        if n % 2 == 0:
            trailing_zeros = 0
            temp_n = n
            while temp_n > 0 and temp_n % 2 == 0:
                trailing_zeros += 1
                temp_n //= 2
            n = n // (2 ** trailing_zeros)
            operation = f"n / (2^{trailing_zeros}) (right shift {trailing_zeros} times)"
        else:
            print(f"    Applying 3n + 1 to {bin(n)}:")
            n_shifted = n << 1
            print(f"        n << 1    : {bin(n_shifted)}")
            n_plus_shifted = n_shifted + n
            print(f"        (n << 1) + n: {bin(n_plus_shifted)}")
            n = n_plus_shifted + 1
            operation = "(3 * n) + 1 (detailed binary)"

        print(f"Current number: {n:<10} | Operation: {operation:<25} | Binary: {bin(n)}")
    print("--------------------------------------------------")
    print("Sequence reached 1.")

if __name__ == "__main__":
    # Test with a few numbers
    collatz_binary_sequence(6)
    print("\n")
    collatz_binary_sequence(7)
    print("\n")
    collatz_binary_sequence(27)
