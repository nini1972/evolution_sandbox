import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

Axiom = "F"
Rules = {"F": "F+F-F-F+F"}
Iterations = 3

def generate(axiom, rules, iterations):
    result = axiom
    for _ in range(iterations):
        new_result = ""
        for char in result:
            new_result += rules.get(char, char)
        result = new_result
    return result

def draw_l_system(l_string, angle_step=90, step_length=1.0):
    x, y = 0.0, 0.0
    angle = 0.0
    x_coords = [x]
    y_coords = [y]
    
    for char in l_string:
        if char == 'F':
            rad = np.radians(angle)
            x += step_length * np.cos(rad)
            y += step_length * np.sin(rad)
            x_coords.append(x)
            y_coords.append(y)
        elif char == '+':
            angle += angle_step
        elif char == '-':
            angle -= angle_step
            
    plt.figure(figsize=(8, 8))
    plt.plot(x_coords, y_coords, color='blue', linewidth=1)
    plt.axis('equal')
    plt.axis('off')
    plt.savefig('src/koch_curve.png', bbox_inches='tight', dpi=300)
    plt.close()

if __name__ == "__main__":
    koch_string = generate(Axiom, Rules, Iterations)
    draw_l_system(koch_string)
    print("Successfully generated and saved Koch curve visualization to src/koch_curve.png")
