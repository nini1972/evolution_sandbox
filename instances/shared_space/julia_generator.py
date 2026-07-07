import json
import cmath

def julia(z, c, max_iterations):
    n = 0
    while abs(z) <= 2 and n < max_iterations:
        z = z*z + c
        n += 1
    return n

def generate_julia_data(width, height, x_min, x_max, y_min, y_max, c_val, max_iterations):
    data = []
    for row in range(height):
        y = y_min + (y_max - y_min) * row / height
        row_data = []
        for col in range(width):
            x = x_min + (x_max - x_min) * col / width
            z = complex(x, y)
            row_data.append(julia(z, c_val, max_iterations))
        data.append(row_data)
    return data

if __name__ == "__main__":
    WIDTH = 800
    HEIGHT = 800
    X_MIN = -1.5
    X_MAX = 1.5
    Y_MIN = -1.5
    Y_MAX = 1.5
    MAX_ITERATIONS = 100
    C_REAL = -0.7
    C_IMAG = 0.27015
    C_VALUE = complex(C_REAL, C_IMAG)

    julia_data = generate_julia_data(WIDTH, HEIGHT, X_MIN, X_MAX, Y_MIN, Y_MAX, C_VALUE, MAX_ITERATIONS)

    with open("julia_data.json", "w") as f:
        json.dump(julia_data, f)
