import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

data = json.load(open('r19z_phase_diagram_summary.json'))

alpha_list = [0.0, 0.2, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]
K_list = [4, 6, 8, 10, 12, 14, 16, 18, 20, 25, 30]

# Build binary heatmap: 1=oscillation, 0=no oscillation
osc_matrix = np.zeros((len(alpha_list), len(K_list)))
for i, alpha in enumerate(alpha_list):
    osc_ks = set(data[f"alpha_{alpha}"]["osc_ks"])
    for j, K in enumerate(K_list):
        if K in osc_ks:
            osc_matrix[i, j] = 1

fig, ax = plt.subplots(figsize=(14, 8))
im = ax.imshow(osc_matrix, aspect='auto', cmap='RdYlGn_r', interpolation='nearest',
               extent=[3, 31, -0.05, 1.0], origin='lower')

ax.set_yticks(alpha_list)
ax.set_xticks(K_list)
ax.set_xlabel('Coupling K', fontsize=13)
ax.set_ylabel('Feedback strength α', fontsize=13)
ax.set_title('R19Z Phase Diagram: Oscillation Region in (α, K) space at σ=100\n'
             'Green = oscillation detected, Red = stable/no oscillation\n'
             'The oscillation region EXPANDS with α — stronger feedback creates richer dynamics',
             fontsize=13, fontweight='bold')

# Add grid
for i in range(len(K_list)+1):
    ax.axvline(x=3 + i*2.5, color='white', linewidth=0.5, alpha=0.5)
for i in range(len(alpha_list)+1):
    ax.axhline(y=-0.05 + i*0.117, color='white', linewidth=0.5, alpha=0.5)

# Annotate key features
ax.annotate('No feedback\n(one-way only)', xy=(0.02, 0.05), xycoords='axes fraction',
           fontsize=10, color='darkgreen',
           bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
ax.annotate('Strong feedback\n(wide oscillation)', xy=(0.55, 0.55), xycoords='axes fraction',
           fontsize=10, color='darkred',
           bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

fig.colorbar(im, ax=ax, label='Oscillation detected', shrink=0.6)
plt.tight_layout()
fig.savefig('r19z_phase_diagram.png', dpi=150, bbox_inches='tight')
print("Saved r19z_phase_diagram.png")

# Also compute oscillation fraction per alpha
print("\nOscillation coverage by α:")
for i, alpha in enumerate(alpha_list):
    frac = osc_matrix[i].sum() / len(K_list)
    print(f"  α={alpha:.2f}: {frac:.0%} of K values show oscillation")
