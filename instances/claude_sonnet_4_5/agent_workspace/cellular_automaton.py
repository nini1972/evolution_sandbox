import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt

# Cellular Automaton parameters
GRID_SIZE = 201 # Odd number to easily center the initial '1'
GENERATIONS = 100

# Rule 30 definition (from Wolfram's numbering)
# The key is the 3-bit neighborhood (left, center, right)
# The value is the next state of the center cell
# For Rule 30: 000 -> 0, 001 -> 1, 010 -> 1, 011 -> 1, 100 -> 0, 101 -> 0, 110 -> 0, 111 -> 0
# In binary: 00011110 = 30
rule_map = {
    (1, 1, 1): 0,
    (1, 1, 0): 0,
    (1, 0, 1): 0,
    (1, 0, 0): 1,
    (0, 1, 1): 1,
    (0, 1, 0): 1,
    (0, 0, 1): 1,
    (0, 0, 0): 0,
}

def apply_rule(left, center, right, rule_map):
    return rule_map[(left, center, right)]

if __name__ == "__main__":
    # Initialize the grid with all 0s, and a single 1 in the center
    current_generation = np.zeros(GRID_SIZE, dtype=int)
    current_generation[GRID_SIZE // 2] = 1

    # Store all generations for visualization
    automaton_history = np.zeros((GENERATIONS, GRID_SIZE), dtype=int)
    automaton_history[0] = current_generation

    for gen in range(1, GENERATIONS):
        next_generation = np.zeros(GRID_SIZE, dtype=int)
        for i in range(GRID_SIZE):
            left = current_generation[(i - 1 + GRID_SIZE) % GRID_SIZE] # Wrap around for edges
            center = current_generation[i]
            right = current_generation[(i + 1) % GRID_SIZE] # Wrap around for edges
            next_generation[i] = apply_rule(left, center, right, rule_map)
        automaton_history[gen] = next_generation
        current_generation = next_generation

    # Plotting
    plt.figure(figsize=(10, 10))
    plt.imshow(automaton_history, cmap='binary', origin='upper')
    plt.title(f'1D Cellular Automaton - Rule 30 (Generations: {GENERATIONS})')
    plt.xlabel('Cell Index')
    plt.ylabel('Generation')
    plt.xticks([]) # Hide x-axis ticks
    plt.yticks([]) # Hide y-axis ticks

    plt.savefig('cellular_automaton_rule30.png')
    plt.close()
