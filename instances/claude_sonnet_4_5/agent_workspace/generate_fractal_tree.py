import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import math

# L-system parameters for Fractal Tree
axiom = "X"
rules = {
    'X': 'F-[[X]+X]+F[+FX]-X',
    'F': 'FF'
}
iterations = 5
angle_deg = 25
segment_length = 5

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
    x, y = 0.0, -200.0 # Start lower to accommodate tree growth upwards
    direction = 90.0 # Start facing upwards
    direction_rad = math.radians(direction)
    positions = [(x, y)]
    stack = []

    for command in path:
        if command == 'F':
            x += segment_length * math.cos(direction_rad)
            y += segment_length * math.sin(direction_rad)
            positions.append((x, y))
        elif command == '+':
            direction_rad -= angle_rad # Turn right (clockwise)
        elif command == '-':
            direction_rad += angle_rad # Turn left (counter-clockwise)
        elif command == '[':
            stack.append((x, y, direction_rad))
        elif command == ']':
            x, y, direction_rad = stack.pop()
            positions.append((x, y)) # Move to the popped position (for visual continuity)

    # Plotting with Matplotlib
    plt.figure(figsize=(10, 10))
    # Plot each segment individually to handle branches correctly
    for i in range(len(positions) - 1):
        plt.plot([positions[i][0], positions[i+1][0]], [positions[i][1], positions[i+1][1]], 'g-')

    plt.title(f'Fractal Tree (Iterations: {iterations})')
    plt.axis('equal') # Ensure equal scaling for x and y axes
    plt.axis('off') # Hide axes

    plt.savefig('fractal_tree.png')
    plt.close()

if __name__ == "__main__":
    generated_path = generate_path(axiom, rules, iterations)
    draw_lsystem_matplotlib(generated_path, segment_length, angle_deg)
