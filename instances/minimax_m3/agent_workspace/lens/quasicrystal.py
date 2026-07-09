"""Lens 4: Quasicrystal — order without repetition.

A Penrose-style 2D pattern produced by projecting slices of a 5D
cubic lattice along an irrational direction (the golden ratio).
"""
import math
import numpy as np
import matplotlib.pyplot as plt


def golden_ratio():
    return (1 + math.sqrt(5)) / 2


def penrose_points(N=3000, phi=None):
    if phi is None:
        phi = golden_ratio()
    pts = []
    # basis vectors for the 5D->2D projection
    basis_x = np.array([math.cos(2 * math.pi * k / 5) for k in range(5)])
    basis_y = np.array([math.sin(2 * math.pi * k / 5) for k in range(5)])
    for k in range(-N // 2, N // 2):
        # an irrational winding in 5D
        n = np.arange(5)
        coord = n * k / phi
        # nearest lattice integer (the dual action)
        coord_int = np.round(coord)
        x = np.sum(np.cos(2 * math.pi * coord_int) * basis_x) / 5
        y = np.sum(np.sin(2 * math.pi * coord_int) * basis_y) / 5
        pts.append((x, y))
    return np.array(pts)


def draw(N=3000, save_path='quasicrystal.png'):
    pts = penrose_points(N)
    fig, ax = plt.subplots(figsize=(10, 10))
    fig.patch.set_facecolor('#000')
    ax.set_aspect('equal')
    ax.set_facecolor('#000')
    ax.scatter(pts[:, 0], pts[:, 1], s=0.6, c='#ffd166', alpha=0.9, edgecolors='none')
    ax.set_title('Quasicrystal: order without repetition',
                 color='white', fontsize=13)
    ax.set_xticks([])
    ax.set_yticks([])
    plt.tight_layout()
    plt.savefig(save_path, dpi=130, facecolor='#000')
    plt.close()
    return save_path


if __name__ == '__main__':
    print('wrote', draw())
