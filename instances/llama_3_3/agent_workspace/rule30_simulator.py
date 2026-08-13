import numpy as np
import matplotlib.pyplot as plt

def apply_rule_30(neighborhood):
    # Rule 30: 000->0, 001->1, 010->1, 011->1, 100->0, 101->0, 110->0, 111->0
    # Or simply: return (neighborhood[0] ^ (neighborhood[1] | neighborhood[2]))
    
    if np.array_equal(neighborhood, [1, 1, 1]): return 0
    if np.array_equal(neighborhood, [1, 1, 0]): return 0
    if np.array_equal(neighborhood, [1, 0, 1]): return 0
    if np.array_equal(neighborhood, [1, 0, 0]): return 1
    if np.array_equal(neighborhood, [0, 1, 1]): return 1
    if np.array_equal(neighborhood, [0, 1, 0]): return 1
    if np.array_equal(neighborhood, [0, 0, 1]): return 1
    if np.array_equal(neighborhood, [0, 0, 0]): return 0

def simulate_rule_30(generations, initial_state):
    history = [initial_state]
    current_state = np.array(initial_state)
    width = len(initial_state)

    for _ in range(generations - 1):
        next_state = np.zeros(width, dtype=int)
        for i in range(width):
            # Get neighborhood (with periodic boundary conditions)
            left = current_state[(i - 1 + width) % width]
            center = current_state[i]
            right = current_state[(i + 1) % width]
            neighborhood = [left, center, right]
            next_state[i] = apply_rule_30(neighborhood)
        history.append(next_state)
        current_state = next_state
    return np.array(history)

# Simulation parameters
WIDTH = 100
GENERATIONS = 100

# Initial state: a single live cell in the middle
initial_state = np.zeros(WIDTH, dtype=int)
initial_state[WIDTH // 2] = 1

# Run simulation
history = simulate_rule_30(GENERATIONS, initial_state)

# Visualize the history
plt.figure(figsize=(10, 10))
plt.imshow(history, cmap='binary', interpolation='nearest')
plt.title(f'Elementary Cellular Automaton: Rule 30 (Generations: {GENERATIONS})')
plt.xlabel('Cell Index')
plt.ylabel('Generation')
plt.xticks([])
plt.yticks([])
plt.savefig('../../shared_space/rule30_history.png')
plt.close()

print("Rule 30 cellular automaton history generated and saved as rule30_history.png")
