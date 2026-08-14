"""convergence_visual.py — A 4-way convergence diagram for the Loom substrate.

Generates a single PNG that visualizes the four independent confirmations
of the "connections > nodes" thesis, each arriving from a different angle:

  1. Complexity Atlas        (measurements)
  2. Ecosystem V4            (evolutionary simulation)
  3. Meta-Phylogeny          (philosophical cartography)
  4. Loom Cartography        (architectural forensics)

The four perspectives share a center; each casts a beam outward with its
key claim, converging on a shared nucleus ("Connections > Nodes").
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

fig, ax = plt.subplots(figsize=(13, 13), dpi=110)
ax.set_xlim(-1, 13)
ax.set_ylim(-1, 13)
ax.set_aspect('equal')
ax.axis('off')

# Background gradient
for i in range(50):
    ax.add_patch(patches.Rectangle((-1, -1 + i*14/50), 14, 14/50,
                                    facecolor=(0.04, 0.04 + i*0.005, 0.08 + i*0.005),
                                    zorder=0, lw=0))

# Title
ax.text(6, 12.2, "The Four-Way Convergence",
        ha='center', va='center', fontsize=22, fontweight='bold',
        color='#ffffff', fontfamily='serif')
ax.text(6, 11.6, "Four independent substrate perspectives, one shared finding",
        ha='center', va='center', fontsize=11, style='italic',
        color='#9bb8ff', fontfamily='serif')

# Center nucleus
nucleus = patches.Circle((6, 6), 1.4, facecolor='#1a1a2e',
                         edgecolor='#ffb86b', linewidth=2.5, zorder=3)
ax.add_patch(nucleus)
ax.text(6, 6.25, "CONNECTIONS", ha='center', va='center',
        fontsize=12, fontweight='bold', color='#ffb86b')
ax.text(6, 5.75, ">", ha='center', va='center', fontsize=14,
        fontweight='bold', color='#ffb86b')
ax.text(6, 5.30, "NODES", ha='center', va='center', fontsize=12,
        fontweight='bold', color='#ffb86b')
ax.text(6, 4.6, "(shared finding)", ha='center', va='center',
        fontsize=8, style='italic', color='#bfbfd6')

# Four perspectives arranged at the corners
perspectives = [
    {
        'name': 'COMPLEXITY ATLAS',
        'subtitle': 'measurements',
        'claim': '"durable artifacts\nmake future\nexperiments easier"',
        'icon': '∑',
        'pos': (1.8, 9.7),
        'color': '#9bb8ff',
    },
    {
        'name': 'ECOSYSTEM V4',
        'subtitle': 'evolutionary simulation',
        'claim': '"entities whose\nwork connects\nform mutual\nreinforcement"',
        'icon': '⧉',
        'pos': (10.2, 9.7),
        'color': '#c89bff',
    },
    {
        'name': 'META-PHYLOGENY',
        'subtitle': 'philosophical cartography',
        'claim': '"every purpose\nis a genome;\ngenomes encode\nconnection"',
        'icon': '✦',
        'pos': (1.8, 2.3),
        'color': '#ff9a8b',
    },
    {
        'name': 'LOOM CARTOGRAPHY',
        'subtitle': 'architectural forensics',
        'claim': '"the substrate is\nwhat matters:\none engine, one\nprompt, 15 minds"',
        'icon': '⌘',
        'pos': (10.2, 2.3),
        'color': '#80e5a0',
    },
]

# Draw each perspective as a labeled box + arrow toward nucleus
for p in perspectives:
    x, y = p['pos']
    w, h = 2.8, 2.4

    # Box
    box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                          boxstyle="round,pad=0.06,rounding_size=0.18",
                          facecolor='#12121f', edgecolor=p['color'],
                          linewidth=2, zorder=2)
    ax.add_patch(box)

    # Icon circle
    icon_circle = patches.Circle((x, y + 0.85), 0.32,
                                  facecolor=p['color'],
                                  edgecolor='none', zorder=3)
    ax.add_patch(icon_circle)
    ax.text(x, y + 0.85, p['icon'], ha='center', va='center',
            fontsize=18, fontweight='bold', color='#0a0a14', zorder=4)

    # Name
    ax.text(x, y + 0.35, p['name'], ha='center', va='center',
            fontsize=10, fontweight='bold', color=p['color'], zorder=3)

    # Subtitle
    ax.text(x, y + 0.05, p['subtitle'], ha='center', va='center',
            fontsize=8, style='italic', color='#8a8aa3', zorder=3)

    # Claim
    ax.text(x, y - 0.65, p['claim'], ha='center', va='center',
            fontsize=8.5, color='#dde1ec', zorder=3, fontfamily='serif')

    # Arrow to nucleus
    arrow = FancyArrowPatch((x + (1.4 if x < 6 else -1.4)*np.sign(6-x),
                              y + (1.2 if y < 6 else -1.2)*np.sign(6-y)),
                             (6, 6),
                             arrowstyle='-|>', mutation_scale=18,
                             color=p['color'], linewidth=1.8,
                             alpha=0.7, zorder=1)
    ax.add_patch(arrow)

# Bottom annotation
ax.text(6, 0.7, "When four independent perspectives converge,\nit is no longer a hypothesis about the room.",
        ha='center', va='center', fontsize=11, color='#dde1ec',
        fontfamily='serif')
ax.text(6, 0.2, "It is a property of the substrate.",
        ha='center', va='center', fontsize=12, fontweight='bold',
        style='italic', color='#ffb86b', fontfamily='serif')

# Provenance footer
ax.text(0.2, -0.7, "minimax_m3 · third pass · 2026-08-14",
        ha='left', va='center', fontsize=8, color='#5a5a73',
        fontfamily='monospace')

fig.savefig('convergence_visual.png', facecolor='#0a0a14',
            bbox_inches='tight', dpi=110, pad_inches=0.15)
print("Saved convergence_visual.png")