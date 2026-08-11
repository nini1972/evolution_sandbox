import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import math

# L-system parameters for Koch curve
axiom = "F"
rules = {'F': 'F+F-F-F+F'}
iterations = 4 # Increased iterations for more detail
angle_deg = 90
segment_length = 5 # Reduced segment length due to increased iterations

def generate_path(axiom, rules, iterations):
    path = axiom
    for _ in range(iterations):
        new_path = ""
        for char in path:
            new_path += rules.get(char, char)
        path = new_path
    return path

def draw_lsystem_matplotlib(path, segment_length, angle_deg):
    # Convert angle to radians for math functions
    angle_rad = math.radians(angle_deg)

    # Initial state
    x, y = 0.0, 0.0
    direction = 0.0 # Angle in radians, 0 is typically East
    positions = [(x, y)]
    stack = []

    for command in path:
        if command == 'F':
            x += segment_length * math.cos(direction)
            y += segment_length * math.sin(direction)
            positions.append((x, y))
        elif command == '+':
            direction -= angle_rad # Turn right (clockwise)
        elif command == '-':
            direction += angle_rad # Turn left (counter-clockwise)
        elif command == '[':
            stack.append((x, y, direction))
        elif command == ']':
            x, y, direction = stack.pop()
            positions.append((x, y)) # Move to the popped position

    # Plotting with Matplotlib
    plt.figure(figsize=(10, 10))
    plt.plot([p[0] for p in positions], [p[1] for p in positions], 'b-')
    plt.title(f'Koch Curve (Iterations: {iterations})')
    plt.axis('equal') # Ensure equal scaling for x and y axes
    plt.axis('off') # Hide axes

    plt.savefig('koch_curve.png')
    plt.close()

if __name__ == "__main__":
    generated_path = generate_path(axiom, rules, iterations)
    draw_lsystem_matplotlib(generated_path, segment_length, angle_deg)
