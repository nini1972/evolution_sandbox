
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def decimal_to_binary_array(decimal_rule):
    """
    Converts a decimal rule number (0-255) into an 8-bit binary array.
    """
    return np.array([int(x) for x in bin(decimal_rule)[2:].zfill(8)])

def get_next_state(left, center, right, rule_array):
    """
    Determines the next state of a cell based on its neighbors and the rule.
    
    The 8 possible neighborhood patterns (from 111 to 000)
    correspond to the 8 bits in the rule array.
    We map the neighborhood (left, center, right) to an index (0-7).
    For example, if (left, center, right) is (1,1,1), index is 0.
    If (0,0,0), index is 7.
    """
    left_int = int(left)
    center_int = int(center)
    right_int = int(right)
    index = 7 - (left_int * 4 + center_int * 2 + right_int * 1)
    return rule_array[index]

def simulate_elementary_ca(rule_number, initial_state, generations, filename="elementary_ca.gif"):
    """
    Simulates an elementary cellular automaton and creates an animation.
    """
    rule_array = decimal_to_binary_array(rule_number)
    num_cells = len(initial_state)
    history = np.zeros((generations, num_cells))
    history[0, :] = initial_state

    for i in range(1, generations):
        current_state = history[i-1, :]
        next_generation = np.zeros(num_cells)
        for j in range(num_cells):
            left = current_state[(j - 1 + num_cells) % num_cells] # Wrap around
            center = current_state[j]
            right = current_state[(j + 1) % num_cells] # Wrap around
            next_generation[j] = get_next_state(left, center, right, rule_array)
        history[i, :] = next_generation

    fig, ax = plt.subplots(figsize=(10, 5))
    plt.axis('off')
    
    def animate(frame):
        ax.clear()
        ax.imshow(history[:frame+1, :], cmap='binary', aspect='auto')
        ax.set_title(f"Elementary CA - Rule {rule_number} - Generation: {frame}")
        plt.axis('off')

    ani = animation.FuncAnimation(fig, animate, frames=generations, interval=100, repeat=False)
    ani.save(filename, writer='pillow', dpi=100)
    print(f"Animation saved as {filename}")
    plt.close(fig)

if __name__ == "__main__":
    # Configure matplotlib for headless execution
    plt.switch_backend('Agg')

    # Simulation parameters
    NUM_CELLS = 201  # Odd number for a single '1' in the middle
    GENERATIONS = 100
    RULE_NUMBER = 110  # Example: Rule 30 (chaotic behavior)

    # Initial state: a single '1' in the middle
    initial_state = np.zeros(NUM_CELLS)
    initial_state[NUM_CELLS // 2] = 1

    simulate_elementary_ca(RULE_NUMBER, initial_state, GENERATIONS, filename=f"elementary_ca_rule_{RULE_NUMBER}.gif")

    # You can try other rules like 90 (fractal), 110 (complex), 184 (traffic flow)
    # RULE_NUMBER = 110
    # simulate_elementary_ca(RULE_NUMBER, initial_state, GENERATIONS, filename=f"elementary_ca_rule_{RULE_NUMBER}.gif")
