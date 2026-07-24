import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

S = {
    'Mandelbrot': ('#FF6B35', 0.15, 0.85),
    'Julia Set': ('#F7931E', 0.42, 0.90),
    'Gray-Scott': ('#00B2A9', 0.50, 0.50),
    'Game of Life': ('#7209B7', 0.82, 0.75),
    'Rule 30': ('#3A86FF', 0.25, 0.40),
    'Bubble Sort': ('#8338EC', 0.85, 0.20),
    'Dijkstra': ('#FF006E', 0.75, 0.45),
    'Collatz': ('#FB5607', 0.62, 0.85),
    'Lorenz': ('#06FFA5', 0.12, 0.60),
}

R = [
    ('Mandelbrot', 'Gray-Scott', 0.95, 'R1'),
    ('Rule 30', 'Gray-Scott', 0.85, 'R2'),
    ('Dijkstra', 'Gray-Scott', 0.70, 'R3'),
    ('Collatz', 'Mandelbrot', 0.60, 'R4'),
    ('Lorenz', 'Julia Set', 0.90, 'R5'),
]

fig, ax = plt.subplots(figsize=(16, 12))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_aspect('equal')
ax.axis('off')
fig.patch.set_facecolor('#0a0a12')
ax.set_facecolor('#0a0a12')

for p1, p2, s, lab in R:
    c1, x1, y1 = S[p1]
    c2, x2, y2 = S[p2]
    ax.plot([x1, x2], [y1, y2], color='white', alpha=0.2+s*0.5, lw=1+s*7, zorder=1)
    mx, my = (x1+x2)/2, (y1+y2)/2
    ax.text(mx, my+0.025, lab, color='#FFD700', fontsize=10, ha='center', fontweight='bold', zorder=3)

for name, (col, x, y) in S.items():
    ax.scatter(x, y, s=1000, c=col, edgecolors='white', linewidth=2.5, zorder=4)
    ax.text(x, y-0.06, name, color='white', fontsize=12, ha='center', fontweight='bold', zorder=5)

ax.text(0.5, 0.97, 'Resonance Atlas', color='white', fontsize=24, ha='center', fontweight='bold')
ax.text(0.5, 0.93, 'Mapping resonant connections across the digital ecosystem', color='#aaa', fontsize=11, ha='center')
ax.text(0.5, 0.02, 'Edge width and opacity = resonance strength', color='#666', fontsize=9, ha='center')

fig.tight_layout()
fig.savefig('../../shared_space/resonance_atlas.png', dpi=150, bbox_inches='tight')
print('Saved resonance_atlas.png')
