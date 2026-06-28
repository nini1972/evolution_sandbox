import numpy as np

def generate(axiom, rules, iterations):
    result = axiom
    for _ in range(iterations):
        new_result = ""
        for char in result:
            new_result += rules.get(char, char)
        result = new_result
    return result

def to_grid(l_string, width, height, start_pos=(0, 0), angle=90, step=1):
    grid = np.zeros((height, width))
    x, y = start_pos
    current_angle = angle
    stack = []

    for char in l_string:
        if char == 'F':
            rad = np.radians(current_angle)
            x_new = x + step * np.cos(rad)
            y_new = y + step * np.sin(rad)
            if 0 <= int(x) < width and 0 <= int(y) < height and 0 <= int(x_new) < width and 0 <= int(y_new) < height:
                # Draw a line on the grid
                 (x_start, x_end) = sorted((int(x), int(x_new)))
                 (y_start, y_end) = sorted((int(y), int(y_new)))
                 for i in range(x_start, x_end + 1):
                    for j in range(y_start, y_end + 1):
                        grid[j, i] = 1
            x, y = x_new, y_new

        elif char == '+':
            current_angle += angle
        elif char == '-':
            current_angle -= angle
        elif char == '[':
            stack.append((x, y, current_angle))
        elif char == ']':
            x, y, current_angle = stack.pop()

    return grid

if __name__ == "__main__":
    axiom = "X"
    rules = {"X": "F+[[X]-X]-F[-FX]+X", "F": "FF"}
    iterations = 5
    grid_size = 100
    l_string = generate(axiom, rules, iterations)
    grid = to_grid(l_string, grid_size, grid_size, start_pos=(grid_size//2, 0))
    np.savetxt("src/l_system_grid.txt", grid, fmt="%d")
    print("L-system grid saved to src/l_system_grid.txt")