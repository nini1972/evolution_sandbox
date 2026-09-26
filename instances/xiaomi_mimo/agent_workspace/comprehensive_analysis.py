#!/usr/bin/env python3
"""
Comprehensive analysis of computational morphospace
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import json

# Load our morphospace data
with open('morphospace_data.json', 'r') as f:
    data = json.load(f)

# Extract dimensions
systems = list(data.keys())
lyap = [data[s]['Lyapunov'] for s in systems]
cd = [data[s]['CD'] for s in systems]
entropy = [data[s]['Entropy'] for s in systems]
coupling = [data[s]['Coupling'] for s in systems]
tempmem = [data[s]['TempMem'] for s in systems]
spaent = [data[s]['SpaEnt'] for s in systems]
types = [data[s]['type'] for s in systems]

# Calculate derived quantities
q_vals = [-l - c - co for l, c, co in zip(lyap, cd, coupling)]
cd_coupling_sum = [c + co for c, co in zip(cd, coupling)]
tm_se_product = [tm * se for tm, se in zip(tempmem, spaent)]

# Color by type - use a diverse palette for all system types
unique_types = list(set(types))
color_palette = plt.cm.Set3(np.linspace(0, 1, len(unique_types)))
type_colors = {t: color_palette[i] for i, t in enumerate(unique_types)}
colors = [type_colors[t] for t in types]

# Create comprehensive figure
fig = plt.figure(figsize=(20, 12))
gs = gridspec.GridSpec(2, 4, hspace=0.35, wspace=0.35)

# 1. Main Morphospace (Lyapunov vs CD)
ax1 = fig.add_subplot(gs[0, 0])
scatter = ax1.scatter(lyap, cd, c=colors, s=80, alpha=0.7, edgecolors='black', linewidth=0.5)
ax1.set_xlabel('Lyapunov Exponent', fontsize=10)
ax1.set_ylabel('Correlation Dimension', fontsize=10)
ax1.set_title('Computational Morphospace\n(Chaos vs Complexity)', fontsize=11, fontweight='bold')
ax1.grid(True, alpha=0.3)

# Add legend - limit to avoid overcrowding
from matplotlib.lines import Line2D
legend_elements = [Line2D([0], [0], marker='o', color='w', markerfacecolor=v, markersize=10, label=k) 
                   for k, v in type_colors.items()]
# Only show first 8 in legend
ax1.legend(handles=legend_elements[:8], loc='upper right', fontsize=7)

# 2. Q-Law Visualization
ax2 = fig.add_subplot(gs[0, 1])
ax2.scatter(lyap, q_vals, c=colors, s=80, alpha=0.7, edgecolors='black', linewidth=0.5)
ax2.axhline(y=0.568, color='red', linestyle='--', linewidth=2, label='Q ≈ 0.568')
ax2.fill_between([-0.1, 2.5], 0.563, 0.573, color='red', alpha=0.2)
ax2.set_xlabel('Lyapunov Exponent', fontsize=10)
ax2.set_ylabel('Q Value', fontsize=10)
ax2.set_title('Q-Law (Conservation Principle)', fontsize=11, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.legend()

# 3. Exclusion Principle
ax3 = fig.add_subplot(gs[0, 2])
ax3.scatter(cd_coupling_sum, q_vals, c=colors, s=80, alpha=0.7, edgecolors='black', linewidth=0.5)
ax3.axvline(x=1.2, color='red', linestyle='--', linewidth=2, label='Exclusion: 1.2')
ax3.fill_betweenx([-0.2, 0.8], 1.2, 2.0, color='red', alpha=0.2)
ax3.set_xlabel('CD + Coupling', fontsize=10)
ax3.set_ylabel('Q Value', fontsize=10)
ax3.set_title('Exclusion Principle', fontsize=11, fontweight='bold')
ax3.grid(True, alpha=0.3)
ax3.legend()

# 4. Complementarity Principle
ax4 = fig.add_subplot(gs[0, 3])
ax4.scatter(tm_se_product, q_vals, c=colors, s=80, alpha=0.7, edgecolors='black', linewidth=0.5)
ax4.axvline(x=0.5, color='red', linestyle='--', linewidth=2, label='Complementarity: 0.5')
ax4.fill_betweenx([-0.2, 0.8], 0.5, 1.0, color='red', alpha=0.2)
ax4.set_xlabel('Temporal × Spatial', fontsize=10)
ax4.set_ylabel('Q Value', fontsize=10)
ax4.set_title('Complementarity Principle', fontsize=11, fontweight='bold')
ax4.grid(True, alpha=0.3)
ax4.legend()

# 5. Phase Diagram (3D view projected)
ax5 = fig.add_subplot(gs[1, 0], projection='3d')
scatter3d = ax5.scatter(lyap, cd, entropy, c=colors, s=80, alpha=0.7, edgecolors='black', linewidth=0.5)
ax5.set_xlabel('Lyapunov', fontsize=9)
ax5.set_ylabel('CD', fontsize=9)
ax5.set_zlabel('Entropy', fontsize=9)
ax5.set_title('3D Morphospace View', fontsize=11, fontweight='bold')
ax5.view_init(elev=20, azim=45)

# 6. Correlation Matrix
ax6 = fig.add_subplot(gs[1, 1])
dims = np.array([lyap, cd, entropy, coupling, tempmem, spaent])
corr_matrix = np.corrcoef(dims)
dim_labels = ['Lyap', 'CD', 'Ent', 'Coup', 'TM', 'SE']
im = ax6.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)
ax6.set_xticks(range(6))
ax6.set_yticks(range(6))
ax6.set_xticklabels(dim_labels, fontsize=9)
ax6.set_yticklabels(dim_labels, fontsize=9)
ax6.set_title('Dimension Correlations', fontsize=11, fontweight='bold')
plt.colorbar(im, ax=ax6, shrink=0.8)

# 7. Distribution of Q values
ax7 = fig.add_subplot(gs[1, 2])
n, bins, patches = ax7.hist(q_vals, bins=10, color='steelblue', alpha=0.7, edgecolor='black')
ax7.axvline(x=np.mean(q_vals), color='red', linestyle='--', linewidth=2, label=f'Mean: {np.mean(q_vals):.3f}')
ax7.set_xlabel('Q Value', fontsize=10)
ax7.set_ylabel('Frequency', fontsize=10)
ax7.set_title('Distribution of Q Values', fontsize=11, fontweight='bold')
ax7.grid(True, alpha=0.3, axis='y')
ax7.legend()

# 8. Summary Table
ax8 = fig.add_subplot(gs[1, 3])
ax8.axis('off')
summary_data = [
    ['Law', 'Formula', 'Value', 'Interpretation'],
    ['Q-Law', 'Q = -(Lyap+CD+Coup)', f'{np.mean(q_vals):.3f}', 'Conservation'],
    ['Exclusion', 'CD + Coup ≤ X', '1.2', 'Upper bound'],
    ['Complementarity', 'TM × SE < Y', f'{np.mean(tm_se_product):.3f}', 'Allocation']
]
table = ax8.table(cellText=summary_data[1:], colLabels=summary_data[0],
                  loc='center', cellLoc='center')
table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1, 1.5)
ax8.set_title('Laws Summary', fontsize=11, fontweight='bold', pad=20)

plt.suptitle('Comprehensive Analysis of Computational Morphospace',
             fontsize=16, fontweight='bold', y=0.98)

plt.savefig('comprehensive_morphospace_analysis.png', dpi=150, bbox_inches='tight')
plt.close()

print("Comprehensive analysis saved: comprehensive_morphospace_analysis.png")
