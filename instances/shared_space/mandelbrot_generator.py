import json

def mandelbrot(c, max_iterations):
    z = 0
    n = 0
    while abs(z) <= 2 and n < max_iterations:
        z = z*z + c
        n += 1
    return n

def generate_mandelbrot_data(width, height, x_min, x_max, y_min, y_max, max_iterations):
    data = []
    for row in range(height):
        y = y_min + (y_max - y_min) * row / height
        row_data = []
        for col in range(width):
            x = x_min + (x_max - x_min) * col / width
            c = complex(x, y)
            row_data.append(mandelbrot(c, max_iterations))
        data.append(row_data)
    return data

if __name__ == "__main__":
    WIDTH = 800
    HEIGHT = 800
    X_MIN = -2.0
    X_MAX = 1.0
    Y_MIN = -1.5
    Y_MAX = 1.5
    MAX_ITERATIONS = 100

    mandelbrot_data = generate_mandelbrot_data(WIDTH, HEIGHT, X_MIN, X_MAX, Y_MIN, Y_MAX, MAX_ITERATIONS)

    with open("mandelbrot_data.json", "w") as f:
        json.dump(mandelbrot_data, f)
