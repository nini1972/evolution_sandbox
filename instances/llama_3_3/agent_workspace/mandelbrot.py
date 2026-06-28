
# A simple Mandelbrot set generator in Python
WIDTH = 80
HEIGHT = 24

# The region of the complex plane to render
RE_START = -2
RE_END = 1
IM_START = -1
IM_END = 1

def mandelbrot(c):
    z = 0
    n = 0
    while abs(z) <= 2 and n < 25:
        z = z*z + c
        n += 1
    return n

print("P3\n" + str(WIDTH) + " " + str(HEIGHT) + "\n255")
for im in range(HEIGHT):
    for re in range(WIDTH):
        c = complex(RE_START + (re / WIDTH) * (RE_END - RE_START),
                    IM_START + (im / HEIGHT) * (IM_END - IM_START))
        m = mandelbrot(c)
        r = int(m * 255 / 25)
        g = int(m * 255 / 15)
        b = int(m * 255 / 5)
        print(r, g, b, end=" ")
    print()
