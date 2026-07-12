"""Render a quick preview thumbnail of lens_dashboard.html by tiling the 6 PNGs."""
import os
import matplotlib.pyplot as plt
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
names = [
    'godelian_lens_revelation.png',
    'strange_loop.png',
    'hofstadter_q.png',
    'quasicrystal.png',
    'mandelbrot_zoom.png',
    'lorenz.png',
]
fig, axes = plt.subplots(2, 3, figsize=(13, 8.6), facecolor='#000')
for ax, n in zip(axes.ravel(), names):
    img = Image.open(os.path.join(HERE, n))
    ax.set_facecolor('#000')
    ax.imshow(img)
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_color('#222')
fig.suptitle('Six Lenses of Self-Reference  -  preview of lens_dashboard.html',
             color='white', fontsize=14, y=0.99)
fig.tight_layout()
out = os.path.join(HERE, 'dashboard_preview.png')
fig.savefig(out, dpi=110, facecolor='#000')
print(out)
