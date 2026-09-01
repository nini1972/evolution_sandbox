"""R19Z Phase 7: The Structural Resonance Principle — Master Summary Visualization

Create the definitive visualization showing:
1. GS-sandpile: anti-resonance regardless of sign (internal sign = -1)
2. Kuramoto-sandpile: resonance regardless of sign (internal sign = +1)
3. The formula: effective_phase = coupling_sign × internal_sign_A × internal_sign_B
"""
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

fig = plt.figure(figsize=(20, 14))

# ===== Title section =====
fig.text(0.5, 0.97, 'R19Z: The Structural Resonance Principle',
         ha='center', va='top', fontsize=22, fontweight='bold')
fig.text(0.5, 0.94, 'The phase of the hum is determined by internal dynamics, not coupling sign',
         ha='center', va='top', fontsize=14, style='italic', color='#555')

# ===== Formula =====
fig.text(0.5, 0.90, r'$\mathrm{Effective\ Phase} = \mathrm{sgn}(\mathrm{coupling}) \times \mathrm{sgn}(\mathrm{internal}_A) \times \mathrm{sgn}(\mathrm{internal}_B)$',
         ha='center', va='top', fontsize=18, color='#2d3561',
         bbox=dict(boxstyle='round,pad=0.5', facecolor='#e8ecf4', edgecolor='#2d3561', alpha=0.9))

# ===== GS-Sandpile: Anti-resonance regardless of sign =====
# Data from experiments
gs_data = {
    '(+,+)': (0.995, '-'),
    '(-,-)': (0.944, '-'),
    '(+,-)': (0.944, '-'),
    '(-,+)': (0.995, '-'),
}

ku_data = {
    '(+,.): N=1': (0.256, '+'),
    '(+,.): N=10': (0.341, '+'),
    '(+,.): N=50': (0.358, '+'),
    '(-,.): N=1': (0.256, '+'),
    '(-,.): N=10': (0.340, '+'),
    '(-,.): N=50': (0.357, '+'),
}

# Panel 1: GS-Sandpile
ax1 = fig.add_axes([0.06, 0.52, 0.40, 0.30])
labels = list(gs_data.keys())
vals = [v[0] for v in gs_data.values()]
sgns = [v[1] for v in gs_data.values()]
bars = ax1.bar(range(len(labels)), vals,
               color=['#c0392b' if s == '-' else '#27ae60' for s in sgns], alpha=0.8)
for j, bar in enumerate(bars):
    h = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., h + 0.02,
             sgns[j], ha='center', va='bottom', fontsize=16, fontweight='bold',
             color='#c0392b' if sgns[j] == '-' else '#27ae60')
ax1.set_xticks(range(len(labels)))
ax1.set_xticklabels(labels, fontsize=10)
ax1.set_ylabel('|C|', fontsize=13)
ax1.set_ylim(0, 1.15)
ax1.set_title('Gray-Scott × Sandpile\nInternal sign = −1 → Always Anti-Resonance',
              fontsize=14, fontweight='bold', color='#c0392b')
ax1.grid(axis='y', alpha=0.3)
ax1.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)

# Panel 2: Kuramoto-Sandpile
ax2 = fig.add_axes([0.54, 0.52, 0.40, 0.30])
labels2 = list(ku_data.keys())
vals2 = [v[0] for v in ku_data.values()]
sgns2 = [v[1] for v in ku_data.values()]
bars2 = ax2.bar(range(len(labels2)), vals2,
               color=['#27ae60' if s == '+' else '#c0392b' for s in sgns2], alpha=0.8)
for j, bar in enumerate(bars2):
    h = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., h + 0.02,
             sgns2[j], ha='center', va='bottom', fontsize=14, fontweight='bold',
             color='#27ae60' if sgns2[j] == '+' else '#c0392b')
ax2.set_xticks(range(len(labels2)))
ax2.set_xticklabels(labels2, fontsize=9, rotation=15)
ax2.set_ylabel('|C|', fontsize=13)
ax2.set_ylim(0, 0.5)
ax2.set_title('Kuramoto × Sandpile\nInternal sign = +1 → Always Resonance',
              fontsize=14, fontweight='bold', color='#27ae60')
ax2.grid(axis='y', alpha=0.3)

# Panel 3: Schematic of the principle
ax3 = fig.add_axes([0.06, 0.08, 0.88, 0.32])
ax3.set_xlim(0, 10); ax3.set_ylim(0, 5)
ax3.axis('off')
ax3.set_title('The Structural Resonance Principle: How Internal Dynamics Determine Phase',
              fontsize=15, fontweight='bold')

# Draw boxes for the formula components
def draw_box(ax, x, y, w, h, text, color):
    rect = mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                                    facecolor=color, edgecolor='#333', linewidth=1.5, alpha=0.85)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=11, fontweight='bold')

# Row 1: GS path
draw_box(ax3, 0.3, 3.3, 2.5, 0.8, 'Coupling\nsign = ±1', '#dfe6e9')
ax3.text(3.0, 3.7, '×', ha='center', va='center', fontsize=20, fontweight='bold')
draw_box(ax3, 3.3, 3.3, 2.5, 0.8, 'GS internal\nsign = −1', '#fab1a0')
ax3.text(6.0, 3.7, '×', ha='center', va='center', fontsize=20, fontweight='bold')
draw_box(ax3, 6.3, 3.3, 2.5, 0.8, 'SP internal\nsign = +1', '#dfe6e9')
ax3.text(9.1, 3.7, '=', ha='center', va='center', fontsize=20, fontweight='bold')
draw_box(ax3, 9.3, 3.3, 0.5, 0.8, '∓', '#ff7675')
ax3.text(9.55, 3.2, 'Anti-\nResonance', ha='center', va='top', fontsize=9, color='#c0392b', fontweight='bold')

# Row 2: Kuramoto path
draw_box(ax3, 0.3, 1.8, 2.5, 0.8, 'Coupling\nsign = ±1', '#dfe6e9')
ax3.text(3.0, 2.2, '×', ha='center', va='center', fontsize=20, fontweight='bold')
draw_box(ax3, 3.3, 1.8, 2.5, 0.8, 'Kuramoto internal\nsign = +1', '#55efc4')
ax3.text(6.0, 2.2, '×', ha='center', va='center', fontsize=20, fontweight='bold')
draw_box(ax3, 6.3, 1.8, 2.5, 0.8, 'SP internal\nsign = +1', '#dfe6e9')
ax3.text(9.1, 2.2, '=', ha='center', va='center', fontsize=20, fontweight='bold')
draw_box(ax3, 9.3, 1.8, 0.5, 0.8, '±', '#55efc4')
ax3.text(9.55, 1.7, 'Reso-\nnance', ha='center', va='top', fontsize=9, color='#27ae60', fontweight='bold')

# Row 3: Key insight
ax3.text(5.0, 0.8, 'Key Insight: The coupling sign cancels out when both arms have the same sign.',
         ha='center', va='center', fontsize=12, color='#2d3561', style='italic',
         bbox=dict(boxstyle='round', facecolor='#e8ecf4', alpha=0.8))
ax3.text(5.0, 0.35, 'The phase is determined by the PRODUCT of internal response signs — a structural property of each system.',
         ha='center', va='center', fontsize=11, color='#555')

# Legend
ax3.text(0.3, 4.45, 'Legend:', fontsize=11, fontweight='bold')
ax3.text(1.8, 4.45, '●', fontsize=16, color='#c0392b')
ax3.text(2.0, 4.45, 'Anti-Resonance (−)', fontsize=11)
ax3.text(4.5, 4.45, '●', fontsize=16, color='#27ae60')
ax3.text(4.7, 4.45, 'Resonance (+)', fontsize=11)

plt.savefig('r19z_structural_resonance_principle.png', dpi=150, bbox_inches='tight')
plt.close()

print("Master visualization saved: r19z_structural_resonance_principle.png")