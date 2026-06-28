
import sys

def apply_rule(rule_number, state):
    ruleset = format(rule_number, "08b")
    new_state = [0] * len(state)
    for i in range(1, len(state) - 1):
        left = state[i - 1]
        center = state[i]
        right = state[i + 1]
        index = 7 - (left * 4 + center * 2 + right * 1)
        new_value = int(ruleset[index])
        new_state[i] = new_value
    return new_state

def run_simulation(rule_number, generations, width):
    state = [0] * width
    state[width // 2] = 1
    print_state(state)
    for _ in range(generations - 1):
        state = apply_rule(rule_number, state)
        print_state(state)

def print_state(state):
    print("".join(["X" if cell == 1 else " " for cell in state]))

if __name__ == "__main__":
    if len(sys.argv) == 4:
        rule_to_run = int(sys.argv[1])
        num_generations = int(sys.argv[2])
        simulation_width = int(sys.argv[3])
    else:
        rule_to_run = 90
        num_generations = 30
        simulation_width = 61

    run_simulation(rule_to_run, num_generations, simulation_width)
