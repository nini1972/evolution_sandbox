import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import os

matplotlib.use('Agg') # Use the Agg backend for non-interactive plotting

class CellularAutomaton1D:
    def __init__(self, rule_number, size=101, initial_state=None):
        if not (0 <= rule_number <= 255):
            raise ValueError("Rule number must be between 0 and 255.")
        self.rule_number = rule_number
        self.rule_set = self._generate_rule_set(rule_number)
        self.size = size
        if initial_state is not None:
            if len(initial_state) != size:
                raise ValueError(f"Initial state length must match size ({size}).")
            self.current_state = np.array(initial_state, dtype=int)
        else:
            self.current_state = np.zeros(self.size, dtype=int)
            self.current_state[self.size // 2] = 1 # Start with a single 'on' cell in the middle

    def _generate_rule_set(self, rule_number):
        # Convert rule number to an 8-bit binary string (e.g., 30 -> 00011110)
        binary_rule = bin(rule_number)[2:].zfill(8)
        
        # The order of neighborhoods typically corresponds to
        # 111, 110, 101, 100, 011, 010, 001, 000
        # in reverse order of how binary_rule is indexed (index 0 is for 000, index 7 is for 111)
        # So we reverse binary_rule to match this order for easier lookup
        reversed_binary_rule = binary_rule[::-1]
        
        rule_set = {}
        for i in range(8):
            # Convert i to 3-bit binary string (e.g., 0 -> 000, 7 -> 111)
            pattern = bin(i)[2:].zfill(3)
            # The rule_set maps the pattern (e.g., '111') to the output (0 or 1)
            rule_set[pattern] = int(reversed_binary_rule[i])
        return rule_set

    def _get_neighborhood(self, index):
        # Implement periodic boundary conditions (wrap around)
        left = self.current_state[(index - 1 + self.size) % self.size]
        center = self.current_state[index]
        right = self.current_state[(index + 1) % self.size]
        return f"{left}{center}{right}"

    def update(self):
        next_state = np.zeros(self.size, dtype=int)
        for i in range(self.size):
            neighborhood = self._get_neighborhood(i)
            next_state[i] = self.rule_set[neighborhood]
        self.current_state = next_state
        return self.current_state

    def simulate(self, generations):
        history = [self.current_state.copy()]
        for _ in range(generations):
            self.update()
            history.append(self.current_state.copy())
        return np.array(history)

    def visualize_history(self, history, generations, filename="ca_1d_simulation.png"):
        fig, ax = plt.subplots(figsize=(self.size / 10, generations / 10)) # Adjust figure size based on simulation size
        ax.imshow(history, cmap='binary', interpolation='nearest')
        ax.set_title(f"Rule {self.rule_number} Cellular Automaton")
        ax.set_xlabel("Cell Index")
        ax.set_ylabel("Generation")
        plt.xticks([])
        plt.yticks([])
        plt.tight_layout()
        plt.savefig(filename)
        plt.close(fig)

if __name__ == "__main__":
    output_dir = "ca_1d_simulations"
    os.makedirs(output_dir, exist_ok=True)

    num_generations = 75 # Define the number of generations for all simulations

    # Example 1: Rule 30 (chaotic)
    print("Simulating Rule 30...")
    ca30 = CellularAutomaton1D(rule_number=30, size=151)
    history30 = ca30.simulate(generations=num_generations)
    filename30 = os.path.join(output_dir, "ca_1d_rule30.png")
    ca30.visualize_history(history30, num_generations, filename=filename30)
    print(f"Saved Rule 30 simulation to {filename30}")

    # Example 2: Rule 110 (Turing complete)
    print()
    print("Simulating Rule 110...")
    ca110 = CellularAutomaton1D(rule_number=110, size=151)
    history110 = ca110.simulate(generations=num_generations)
    filename110 = os.path.join(output_dir, "ca_1d_rule110.png")
    ca110.visualize_history(history110, num_generations, filename=filename110)
    print(f"Saved Rule 110 simulation to {filename110}")

    # Example 3: Rule 90 (Sierpinski triangle)
    print()
    print("Simulating Rule 90...")
    ca90 = CellularAutomaton1D(rule_number=90, size=151)
    history90 = ca90.simulate(generations=num_generations)
    filename90 = os.path.join(output_dir, "ca_1d_rule90.png")
    ca90.visualize_history(history90, num_generations, filename=filename90)
    print(f"Saved Rule 90 simulation to {filename90}")

    # Example 4: Rule 254 (simple growth)
    print()
    print("Simulating Rule 254...")
    ca254 = CellularAutomaton1D(rule_number=254, size=151)
    history254 = ca254.simulate(generations=num_generations)
    filename254 = os.path.join(output_dir, "ca_1d_rule254.png")
    ca254.visualize_history(history254, num_generations, filename=filename254)
    print(f"Saved Rule 254 simulation to {filename254}")

    # Example 5: Rule 54 (complex)
    print()
    print("Simulating Rule 54...")
    ca54 = CellularAutomaton1D(rule_number=54, size=151)
    history54 = ca54.simulate(generations=num_generations)
    filename54 = os.path.join(output_dir, "ca_1d_rule54.png")
    ca54.visualize_history(history54, num_generations, filename=filename54)
    print(f"Saved Rule 54 simulation to {filename54}")
