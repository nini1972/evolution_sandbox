import numpy as np
import matplotlib.pyplot as plt
import os

def apply_rule(rule_number, state):
    # Correct bit mapping:
    # index = (left * 4) + (state * 2) + right
    # result = (rule_number >> index) & 1
    left = np.roll(state, 1)
    right = np.roll(state, -1)
    
    indices = (left * 4) + (state * 2) + right
    lookup = np.array([(rule_number >> i) & 1 for i in range(8)])
    new_state = lookup[indices]
    
    return new_state

def simulate_ca(rule_number, generations, width):
    grid = np.zeros((generations, width), dtype=int)
    grid[0, width // 2] = 1
    
    for i in range(1, generations):
        grid[i] = apply_rule(rule_number, grid[i-1])
    
    return grid

def visualize_ca(grid, rule_number, filename):
    plt.figure(figsize=(10, 10))
    plt.imshow(grid, cmap="binary", interpolation="nearest")
    plt.title(f"Rule {rule_number}")
    plt.axis("off")
    plt.savefig(filename)
    plt.close()

if __name__ == "__main__":
    # Rules to explore: 30 (Chaotic), 90 (Sierpinski), 110 (Turing Complete), 184 (Traffic)
    interesting_rules = [30, 90, 110, 184]
    gens = 200
    width = 400
    
    os.makedirs("visuals", exist_ok=True)
    
    for rule in interesting_rules:
        grid = simulate_ca(rule, gens, width)
        visualize_ca(grid, rule, f"visuals/rule_{rule}.png")
        print(f"Generated visual for Rule {rule}")
