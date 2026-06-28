import numpy as np
import sys
import json

def generate(axiom, rules, iterations):
    result = axiom
    for _ in range(iterations):
        new_result = ""
        for char in result:
            new_result += rules.get(char, char)
        result = new_result
    return result

def draw_l_system_2d(l_string, angle_step=25, step_length=1):
    grid_size = 500
    grid = np.zeros((grid_size, grid_size), dtype=np.uint8)
    pos = (grid_size // 2, grid_size // 2)
    angle = 90
    stack = []

    for char in l_string:
        if char == "F":
            x, y = pos
            rad = np.radians(angle)
            new_x = int(x + step_length * np.cos(rad))
            new_y = int(y - step_length * np.sin(rad))
            if 0 <= new_x < grid_size and 0 <= new_y < grid_size:
                grid[new_y, new_x] = 255
                pos = (new_x, new_y)
            else:
                pos = (x, y)
        elif char == "+":
            angle += angle_step
        elif char == "-":
            angle -= angle_step
        elif char == "[":
            stack.append((pos, angle))
        elif char == "]":
            pos, angle = stack.pop()
            
    return grid

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python l_system_generator.py <axiom> <rules_json> <iterations> <output_file>")
        sys.exit(1)

    axiom = sys.argv[1]
    # Reconstruct rules_json by joining arguments between axiom and iterations
    rules_json = " ".join(sys.argv[2:-2]).strip("'\"")
    iterations = int(sys.argv[-2])
    output_file = sys.argv[-1]

    try:
        rules = json.loads(rules_json)
    except json.JSONDecodeError:
        # Fallback for when shell strips quotes: e.g. {X: F+[[X]-X]-F[-FX]+X, F: FF}
        rules = {}
        cleaned = rules_json.strip("{}")
        for pair in cleaned.split(","):
            if ":" in pair:
                k, v = pair.split(":", 1)
                rules[k.strip().strip("'\"")] = v.strip().strip("'\"")
        if not rules:
            print("Error: Invalid rules format.")
            sys.exit(1)

    l_system_string = generate(axiom, rules, iterations)
    grid = draw_l_system_2d(l_system_string)
    
    # Trim the grid to the bounding box of the L-system
    rows = np.any(grid, axis=1)
    cols = np.any(grid, axis=0)
    if np.any(rows) and np.any(cols):
        ymin, ymax = np.where(rows)[0][[0, -1]]
        xmin, xmax = np.where(cols)[0][[0, -1]]
        trimmed_grid = grid[ymin:ymax+1, xmin:xmax+1]
    else:
        trimmed_grid = grid
        
    np.savetxt(output_file, trimmed_grid, fmt="%d")

    print(f"L-system grid saved to {output_file}")
