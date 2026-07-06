
import json
import argparse

def apply_rule30(left, center, right):
    # Rule 30:   111 110 101 100 011 010 001 000
    #            --------------------------------
    #              0   0   0   1   1   1   1   0
    if left == 1 and center == 1 and right == 1: return 0
    if left == 1 and center == 1 and right == 0: return 0
    if left == 1 and center == 0 and right == 1: return 0
    if left == 1 and center == 0 and right == 0: return 1
    if left == 0 and center == 1 and right == 1: return 1
    if left == 0 and center == 1 and right == 0: return 1
    if left == 0 and center == 0 and right == 1: return 1
    if left == 0 and center == 0 and right == 0: return 0

def create_initial_row(size):
    row = [0] * size
    row[size // 2] = 1  # Start with a single '1' in the middle
    return row

def simulate_rule30(size, generations):
    current_row = create_initial_row(size)
    all_generations = [current_row]

    for _ in range(generations - 1):
        next_row = [0] * size
        for i in range(size):
            left = current_row[i - 1] if i > 0 else 0
            center = current_row[i]
            right = current_row[i + 1] if i < size - 1 else 0
            next_row[i] = apply_rule30(left, center, right)
        current_row = next_row
        all_generations.append(current_row)
    return all_generations

def main():
    parser = argparse.ArgumentParser(description="Simulate Conway's Game of Life.")
    parser.add_argument("--size", type=int, default=101, help="Size of the 1D automaton row.")
    parser.add_argument("--generations", type=int, default=100, help="Number of generations to simulate.")
    args = parser.parse_args()

    all_generations = simulate_rule30(args.size, args.generations)

    # Convert 1s and 0s to '#' and ' ' for better representation in JSON
    serializable_generations = []
    for gen in all_generations:
        serializable_generations.append("".join(["#" if cell == 1 else " " for cell in gen]))

    with open("rule30_generations.json", "w") as f:
        json.dump(serializable_generations, f)

if __name__ == "__main__":
    main()
