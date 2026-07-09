"""Lens 6: Lorenz attractor — deterministic chaos wearing a shape.

Three coupled nonlinear ODEs (Lorenz, 1963) produce a strange
attractor: a fractal of dimension ~2.06 inside 3-space. The system
is fully deterministic and yet unpredictable in detail.
"""
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  (registers projection)


def lorenz(N=20000, dt=0.005, sigma=10.0, rho=28.0, beta=8.0 / 3.0,
           x0=(0.1, 0.0, 0.0)):
    x, y, z = x0
    xs = np.empty(N)
    ys = np.empty(N)
    zs = np.empty(N)
    for i in range(N):
        xs[i] = x
        ys[i] = y
        zs[i] = z
        dx = sigma * (y - x)
        dy = x * (rho - z) - y
        dz = x * y - beta * z
        x += dx * dt
        y += dy * dt
        z += dz * dt
    return xs, ys, zs


def draw(save_path='lorenz.png'):
    xs, ys, zs = lorenz()
    # skip transient
    xs, ys, zs = xs[1000:], ys[1000:], zs[1000:]

    fig = plt.figure(figsize=(12, 10))
    fig.patch.set_facecolor('#000')
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('#000')
    ax.plot(xs, ys, zs, lw=0.35, color='#ef476f', alpha=0.9)
    ax.set_title('Lorenz: a deterministic shape that is forever surprising',
                 color='white', fontsize=13)
    ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.pane.set_facecolor('#000')
        axis.pane.set_edgecolor('#222')
    plt.tight_layout()
    plt.savefig(save_path, dpi=130, facecolor='#000')
    plt.close()
    return save_path


if __name__ == '__main__':
    print('wrote', draw())
