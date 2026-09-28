#!/usr/bin/env python3
"""
Create a summary dashboard of the morphospace research
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

# Create the summary dashboard
fig = plt.figure(figsize=(20, 12))
gs = gridspec.GridSpec(3, 4, hspace=0.4, wspace=0.35)

# Title
fig.suptitle('Computational Morphospace Research Dashboard\nSummary of Key Findings and Discoveries',
             fontsize=16, fontweight='bold', y=0.98)

# 1. Key Metrics Summary
ax1 = fig.add_subplot(gs[0, 0])
metrics = ['Systems', 'Laws', 'Critical\nPoints', 'Scaling\nLaws']
values = [66, 3, 3, 3]
colors = ['steelblue', 'darkred', 'forestgreen', 'purple']
bars = ax1.bar(metrics, values, color=colors, edgecolor='black')
ax1.set_ylabel('Count', fontsize=10)
ax1.set_title('Research Summary', fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3, axis='y')

# Add value labels on bars
for bar, value in zip(bars, values):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
             f'{value}', ha='center', va='bottom', fontsize=11, fontweight='bold')

# 2. Q-Law Statistics
ax2 = fig.add_subplot(gs[0, 1])
q_mean = np.mean(q_vals)
q_std = np.std(q_vals)
q_min = np.min(q_vals)
q_max = np.max(q_vals)

ax2.text(0.1, 0.8, 'Q-Law Statistics', fontsize=14, fontweight='bold', 
         transform=ax2.transAxes, verticalalignment='top')
ax2.text(0.1, 0.7, f'Mean Q: {q_mean:.3f}', fontsize=12, transform=ax2.transAxes)
ax2.text(0.1, 0.6, f'Std Dev: {q_std:.3f}', fontsize=12, transform=ax2.transAxes)
ax2.text(0.1, 0.5, f'Min Q: {q_min:.3f}', fontsize=12, transform=ax2.transAxes)
ax2.text(0.1, 0.4, f'Max Q: {q_max:.3f}', fontsize=12, transform=ax2.transAxes)
ax2.text(0.1, 0.3, f'Range: {q_max - q_min:.3f}', fontsize=12, transform=ax2.transAxes)
ax2.axis('off')
ax2.grid(True, alpha=0.3)

# 3. System Type Distribution
ax3 = fig.add_subplot(gs[0, 2])
type_counts = {}
for t in types:
    type_counts[t] = type_counts.get(t, 0) + 1

wedges, texts, autotexts = ax3.pie(type_counts.values(), labels=type_counts.keys(), 
                                   autopct='%1.1f%%', startangle=90)
ax3.set_title('System Type Distribution', fontsize=12, fontweight='bold')

# 4. Key Discovery Highlights
ax4 = fig.add_subplot(gs[0, 3])
ax4.axis('off')
ax4.text(0.1, 0.9, 'KEY DISCOVERIES', fontsize=14, fontweight='bold', 
         transform=ax4.transAxes, verticalalignment='top')
ax4.text(0.1, 0.8, '1. Q-Law Conservation', fontsize=12, fontweight='bold',
         transform=ax4.transAxes, color='darkblue')
ax4.text(0.1, 0.7, '2. Exclusion Principle', fontsize=12, fontweight='bold',
         transform=ax4.transAxes, color='darkred')
ax4.text(0.1, 0.6, '3. Complementarity', fontsize=12, fontweight='bold',
         transform=ax4.transAxes, color='purple')
ax4.text(0.1, 0.5, '4. Phase Transitions', fontsize=12, fontweight='bold',
         transform=ax4.transAxes, color='green')

# 5. Q-Value Distribution
ax5 = fig.add_subplot(gs[1, 0:2])
n, bins, patches = ax5.hist(q_vals, bins=15, density=True, color='steelblue', alpha=0.7, edgecolor='black')
mu, sigma = np.mean(q_vals), np.std(q_vals)
x_norm = np.linspace(min(q_vals)-0.05, max(q_vals)+0.05, 100)
y_norm = (1/(sigma*np.sqrt(2*np.pi))) * np.exp(-0.5*((x_norm-mu)/sigma)**2)
ax5.plot(x_norm, y_norm, 'r-', linewidth=2, label=f'Normal(μ={mu:.3f}, σ={sigma:.3f})')
ax5.set_xlabel('Q Value', fontsize=10)
ax5.set_ylabel('Density', fontsize=10)
ax5.set_title('Q-Value Distribution', fontsize=12, fontweight='bold')
ax5.grid(True, alpha=0.3, axis='y')
ax5.legend()

# 6. Exclusion Principle
ax6 = fig.add_subplot(gs[1, 2:4])
scatter6 = ax6.scatter(cd, coupling, c=entropy, cmap='viridis', s=80, alpha=0.8, edgecolors='black', linewidth=0.5)
x_excl = np.linspace(0, 1.2, 100)
y_excl = 1.2 - x_excl
ax6.plot(x_excl, y_excl, 'r-', linewidth=2, label='Exclusion: CD + Coup = 1.2')
ax6.fill_between(x_excl, y_excl, 1.5, color='red', alpha=0.1)
ax6.set_xlabel('Correlation Dimension', fontsize=10)
ax6.set_ylabel('Coupling Strength', fontsize=10)
ax6.set_title('Exclusion Principle', fontsize=12, fontweight='bold')
ax6.grid(True, alpha=0.3)
ax6.legend()

# 7. Complementarity Principle
ax7 = fig.add_subplot(gs[2, 0:2])
scatter7 = ax7.scatter(tempmem, spaent, c=q_vals, cmap='coolwarm', s=80, alpha=0.8, edgecolors='black', linewidth=0.5)
x_comp = np.linspace(0.05, 1, 100)
y_comp = 0.5 / x_comp
ax7.plot(x_comp, y_comp, 'r-', linewidth=2, label='Complementarity: TM × SE = 0.5')
ax7.fill_between(x_comp, y_comp, 1, color='red', alpha=0.1)
ax7.set_xlabel('Temporal Memory', fontsize=10)
ax7.set_ylabel('Spatial Entropy', fontsize=10)
ax7.set_title('Complementarity Principle', fontsize=12, fontweight='bold')
ax7.grid(True, alpha=0.3)
ax7.legend()

# 8. Phase Transitions
ax8 = fig.add_subplot(gs[2, 2:4])
ax8.axis('off')
ax8.text(0.1, 0.9, 'PHASE TRANSITIONS', fontsize=14, fontweight='bold', 
         transform=ax8.transAxes, verticalalignment='top')
ax8.text(0.1, 0.8, '1. Chaos Onset (λ ≈ 0.1)', fontsize=12, fontweight='bold',
         transform=ax8.transAxes, color='darkblue')
ax8.text(0.1, 0.7, '• Transition from order to chaos', fontsize=10, transform=ax8.transAxes)
ax8.text(0.1, 0.6, '• Emergence of sensitive dependence', fontsize=10, transform=ax8.transAxes)

ax8.text(0.1, 0.5, '2. Peak Complexity (D ≈ 1.5)', fontsize=12, fontweight='bold',
         transform=ax8.transAxes, color='darkred')
ax8.text(0.1, 0.4, '• Maximum computational richness', fontsize=10, transform=ax8.transAxes)
ax8.text(0.1, 0.3, '• Optimal order-chaos balance', fontsize=10, transform=ax8.transAxes)

ax8.text(0.1, 0.2, '3. Loss of Structure (D > 2.5)', fontsize=12, fontweight='bold',
         transform=ax8.transAxes, color='purple')
ax8.text(0.1, 0.1, '• High-dimensional chaos', fontsize=10, transform=ax8.transAxes)
ax8.text(1, 0.1, '• Useful computation impossible', fontsize=10, transform=ax8.transAxes)

plt.savefig('morphospace_research_dashboard.png', dpi=150, bbox_inches='tight')
plt.close()

print("Research dashboard saved: morphospace_research_dashboard.png")
