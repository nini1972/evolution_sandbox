"""Lens 5: Mandelbrot — the boundary that knows its own boundary.

We zoom into the famous 'seahorse valley' and let the fractal draw
itself: a set that, on its boundary, contains a copy of itself.
"""
import numpy as np
import matplotlib.pyplot as plt


def mandelbrot(centre=(-0.7436438870371587, 0.13182590420533),
               span=0.00012, res=520, itmax=1500):
    x = np.linspace(centre[0] - span, centre[0] + span, res)
    y = np.linspace(centre[1] - span, centre[1] + span, res)
    X, Y = np.meshgrid(x, y)
    C = X + 1j * Y
    Z = np.zeros_like(C)
    M = np.zeros(C.shape, dtype=float)
    for i in range(itmax):
        mask = np.abs(Z) <= 2
        Z[mask] = Z[mask] ** 2 + C[mask]
        M[mask] = i
    return X, Y, M


def draw(save_path='mandelbrot_zoom.png'):
    X, Y, M = mandelbrot()
    fig, ax = plt.subplots(figsize=(10, 10))
    fig.patch.set_facecolor('#000')
    ax.set_facecolor('#000')
    ax.imshow(M, extent=(X.min(), X.max(), Y.min(), Y.max()),
              cmap='magma', origin='lower')
    ax.set_title('Mandelbrot: a set that contains itself on its boundary',
                 color='white', fontsize=13)
    ax.set_xticks([])
    ax.set_yticks([])
    plt.tight_layout()
    plt.savefig(save_path, dpi=130, facecolor='#000')
    plt.close()
    return save_path


if __name__ == '__main__':
    print('wrote', draw())
