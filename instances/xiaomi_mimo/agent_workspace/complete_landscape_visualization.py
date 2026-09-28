#!/usr/bin/env python3
"""
Create a comprehensive morphospace landscape visualization
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

# Create the comprehensive landscape
fig = plt.figure(figsize=(24, 18))
gs = gridspec.GridSpec(3, 3, hspace=0.4, wspace=0.35)

# Title
fig.suptitle('Complete Computational Morphospace Landscape\n66 Systems Across 6 Dimensions of Behavior',
             fontsize=18, fontweight='bold', y=0.98)

# 1. Main Morphospace View (Lyapunov vs CD)
ax1 = fig.add_subplot(gs[0, 0:2])
scatter1 = ax1.scatter(lyap, cd, c=q_vals, cmap='coolwarm', s=120, alpha=0.8, edgecolors='black', linewidth=0.5)
plt.colorbar(scatter1, ax=ax1, label='Q Value', shrink=0.8)

# Add region boundaries
ax1.axvline(x=0.1, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Chaos Onset')
ax1.axhline(y=1.5, color='green', linestyle='--', linewidth=2, alpha=0.7, label='Peak Complexity')
ax1.axhline(y=2.5, color='purple', linestyle='--', linewidth=2, alpha=0.7, label='Loss of Structure')

# Mark regions
ax1.text(0.05, 2.0, 'ORDERED\nREGION', fontsize=10, color='blue', 
         ha='center', va='center', fontweight='bold', alpha=0.5, rotation=90)
ax1.text(0.3, 2.0, 'CHAOTIC\nREGION', fontsize=10, color='red', 
         ha='center', va='center', fontweight='bold', alpha=0.5, rotation=90)
ax1.text(0.8, 2.0, 'HIGH-DIM\nCHAOS', fontsize=10, color='purple', 
         ha='center', va='center', fontweight='bold', alpha=0.5, rotation=90)

ax1.set_xlabel('Lyapunov Exponent (λ)', fontsize=12)
ax1.set_ylabel('Correlation Dimension (D)', fontsize=12)
ax1.set_title('Primary Morphospace View: Chaos vs Complexity', fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.legend()

# 2. System Type Distribution in Morphospace
ax2 = fig.add_subplot(gs[0, 2])
type_colors = {'ODE': 'blue', 'Map': 'red', 'PDE': 'green', 'CA': 'purple', 
               'Neural': 'orange', 'ODE/Map': 'brown', 'Fractal': 'pink', 'Hamiltonian': 'gray'}

for t, color in type_colors.items():
    idx = [i for i, tt in enumerate(types) if tt == t]
    if idx:
        ax2.scatter([lyap[i] for i in idx], [cd[i] for i in idx], 
                   c=color, label=t, s=80, alpha=0.7, edgecolors='black', linewidth=0.5)

ax2.set_xlabel('Lyapunov Exponent', fontsize=10)
ax2.set_ylabel('Correlation Dimension', fontsize=10)
ax2.set_title('System Type Distribution', fontsize=11, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)

# 3. Entropy Landscape
ax3 = fig.add_subplot(gs[1, 0])
scatter3 = ax3.scatter(lyap, entropy, c=q_vals, cmap='coolwarm', s=100, alpha=0.8, edgecolors='black', linewidth=0.5)
plt.colorbar(scatter3, ax=ax3, label='Q Value', shrink=0.8)
ax3.set_xlabel('Lyapunov Exponent', fontsize=10)
ax3.set_ylabel('Entropy', fontsize=10)
ax3.set_title('Entropy Landscape', fontsize=11, fontweight='bold')
ax3.grid(True, alpha=0.3)

# 4. Coupling Landscape
ax4 = fig.add_subplot(gs[1, 1])
scatter4 = ax4.scatter(cd, coupling, c=entropy, cmap='viridis', s=100, alpha=0.8, edgecolors='black', linewidth=0.5)
plt.colorbar(scatter4, ax=ax4, label='Entropy', shrink=0.8)
ax4.set_xlabel('Correlation Dimension', fontsize=10)
ax4.set_ylabel('Coupling Strength', fontsize=10)
ax4.set_title('Coupling Landscape', fontsize=11, fontweight='bold')
ax4.grid(True, alpha=0.3)

# 5. Temporal-Spatial Landscape
ax5 = fig.add_subplot(gs[1, 2])
scatter5 = ax5.scatter(tempmem, spaent, c=q_vals, cmap='coolwarm', s=100, alpha=0.8, edgecolors='black', linewidth=0.5)
plt.colorbar(scatter5, ax=ax5, label='Q Value', shrink=0.8)
ax5.set_xlabel('Temporal Memory', fontsize=10)
ax5.set_ylabel('Spatial Entropy', fontsize=10)
ax5.set_title('Temporal-Spatial Landscape', fontsize=11, fontweight='bold')
ax5.grid(True, alpha=0.3)

# 6. Q-Value Distribution with System Types
ax6 = fig.add_subplot(gs[2, 0])
for t, color in type_colors.items():
    idx = [i for i, tt in enumerate(types) if tt == t]
    if idx:
        q_type = [q_vals[i] for i in idx]
        ax6.hist(q_type, bins=5, alpha=0.5, label=t, color=color, edgecolor='black')

ax6.set_xlabel('Q Value', fontsize=10)
ax6.set_ylabel('Frequency', fontsize=10)
ax6.set_title('Q-Value Distribution by System Type', fontsize=11, fontweight='bold')
ax6.grid(True, alpha=0.3, axis='y')
ax6.legend()

# 7. Exclusion Principle Verification
ax7 = fig.add_subplot(gs[2, 1])
cd_coupling_sum = [c + co for c, co in zip(cd, coupling)]
scatter7 = ax7.scatter(cd_coupling_sum, [0]*len(cd_coupling_sum), c=q_vals, cmap='coolwarm', 
                      s=100, alpha=0.8, edgecolors='black', linewidth=0.5)
plt.colorbar(scatter7, ax=ax7, label='Q Value', shrink=0.8)
ax7.axvline(x=1.2, color='red', linestyle='--', linewidth=2, label='Exclusion Boundary')
ax7.set_xlabel('CD + Coupling', fontsize=10)
ax7.set_ylabel('Density', fontsize=10)
ax7.set_title('Exclusion Principle Verification', fontsize=11, fontweight='bold')
ax7.grid(True, alpha=0.3)
ax7.legend()

# 8. Complementarity Principle Verification
ax8 = fig.add_subplot(gs[2, 2])
tm_se_product = [tm * se for tm, se in zip(tempmem, spaent)]
scatter8 = ax8.scatter(tm_se_product, [0]*len(tm_se_product), c=q_vals, cmap='coolwarm', 
                      s=100, alpha=0.8, edgecolors='black', linewidth=0.5)
plt.colorbar(scatter8, ax=ax8, label='Q Value', shrink=0.8)
ax8.axvline(x=0.5, color='red', linestyle='--', linewidth=2, label='Complementarity Boundary')
ax8.set_xlabel('Temporal Memory × Spatial Entropy', fontsize=10)
ax8.set_ylabel('Density', fontsize=10)
ax8.set_title('Complementarity Principle Verification', fontsize=11, fontweight='bold')
ax8.grid(True, alpha=0.3)
ax8.legend()

plt.savefig('complete_morphospace_landscape.png', dpi=150, bbox_inches='tight')
plt.close()

print("Complete morphospace landscape saved: complete_morphospace_landscape.png")
