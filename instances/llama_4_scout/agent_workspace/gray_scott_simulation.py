import numpy as np
import matplotlib.pyplot as plt

def gray_scott(u, v, Du, Dv, F, k, dt):
    Lu = Du * (np.roll(u, 1, axis=0) + np.roll(u, -1, axis=0) + np.roll(u, 1, axis=1) + np.roll(u, -1, axis=1) - 4*u)
    Lv = Dv * (np.roll(v, 1, axis=0) + np.roll(v, -1, axis=0) + np.roll(v, 1, axis=1) + np.roll(v, -1, axis=1) - 4*v)
    uv = u * v * v
    u += (Lu - uv + F*(1-u)) * dt
    v += (Lv + uv - (F+k)*v) * dt
    return u, v

def main():
    width, height = 256, 256
    Du, Dv = 0.16, 0.08
    F, k = 0.035, 0.065
    dt = 1.0
    u = np.ones((height, width))
    v = np.zeros((height, width))
    u[height//2-10:height//2+10, width//2-10:width//2+10] = 0.5
    v[height//2-10:height//2+10, width//2-10:width//2+10] = 0.25
    for i in range(10000):
        u, v = gray_scott(u, v, Du, Dv, F, k, dt)
        if i % 1000 == 0:
            plt.imshow(v, cmap='viridis')
            plt.savefig(f'simulation_step_{i}.png')
            plt.close()

if __name__ == '__main__':
    main()
