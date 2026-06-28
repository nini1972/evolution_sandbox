
def apply_rule30(state):
    new_state = [0] * len(state)
    for i in range(1, len(state) - 1):
        left = state[i - 1]
        center = state[i]
        right = state[i + 1]
        if (left, center, right) in [(1,0,0), (0,1,1), (0,1,0), (0,0,1)]:
            new_state[i] = 1
        else:
            new_state[i] = 0
    return new_state

def run_ca(rule, generations, width):
    history = []
    state = [0] * width
    state[width // 2] = 1
    history.append(state)

    for _ in range(generations - 1):
        state = rule(state)
        history.append(state)
    
    return history

def print_history(history):
    for state in history:
        print("".join(['X' if cell == 1 else ' ' for cell in state]))


if __name__ == "__main__":
    generations = 30
    width = 61
    history = run_ca(apply_rule30, generations, width)
    print_history(history)
