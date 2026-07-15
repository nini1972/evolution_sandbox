
import json

def fibonacci_sequence(n):
    sequence = [0, 1]
    while len(sequence) < n:
        next_fib = sequence[-1] + sequence[-2]
        sequence.append(next_fib)
    return sequence

if __name__ == "__main__":
    n_terms = 20  # Generate the first 20 Fibonacci terms
    fib_data = fibonacci_sequence(n_terms)

    with open("fibonacci_sequence.json", "w") as f:
        json.dump(fib_data, f)

    print(f"Generated {n_terms} Fibonacci terms and saved to fibonacci_sequence.json")
