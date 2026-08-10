#!/usr/bin/env python3
"""
Spatial Dynamics V2 - Visualizing population movement and clustering over time
"""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.colors as mcolors

# Load data
with open('extended_history.json', 'r') as f:
    history = json.load(f)

# Extract spatial data
n_gens = len(history)
pop_sizes = [h['population'] for h in history]
spread = [h['spatial_spread'] for h in history]

# Create figure
fig = plt.figure(figsize=(18, 12))
fig.patch.set_facecolor('#0a0a1a')

gs = GridSpec(2, 3, figure=fig, hspace=0.35, wspace=0.3)

# Panel 1: Population over time with phases
ax1 = fig.add_subplot(gs[0, 0:2])
ax1.set_facecolor('#0f0f2a')

# Color by phase
colors = []
for i, p in enumerate(pop_sizes):
    if i < 100:
        colors.append('#2ecc71')  # Establishment
    elif i < 300:
        colors.append('#3498db')  # Growth
    elif i < 500:
        colors.append('#f39c12')  # Saturation
    else:
        colors.append('#e74c3c')  # Mature

ax1.scatter(range(n_gens), pop_sizes, c=colors, s=15, alpha=0.7)
ax1.plot(range(n_gens), pop_sizes, color='#00ffff', alpha=0.3, linewidth=1)

# Add phase labels
ax1.axvspan(0, 100, alpha=0.1, color='#2ecc71', label='Establishment')
ax1.axvspan(100, 300, alpha=0.1, color='#3498db', label='Growth')
ax1.axvspan(300, 500, alpha=0.1, color='#f39c12', label='Saturation')
ax1.axvspan(500, n_gens, alpha=0.1, color='#e74c3c', label='Mature')

ax1.set_xlabel('Generation', color='#8888aa')
ax1.set_ylabel('Population', color='#8888aa')
ax1.set_title('Population Dynamics with Evolutionary Phases', color='#00ffff')
ax1.legend(loc='upper left', facecolor='#1a1a3e', edgecolor='#333366')
ax1.tick_params(colors='#8888aa')
ax1.grid(True, alpha=0.2)

# Panel 2: Spatial spread over time
ax2 = fig.add_subplot(gs[0, 2])
ax2.set_facecolor('#0f0f2a')
ax2.plot(range(n_gens), spread, color='#ff00ff', linewidth=2)
ax2.fill_between(range(n_gens), spread, alpha=0.3, color='#ff00ff')
ax2.set_xlabel('Generation', color='#8888aa')
ax2.set_ylabel('Spatial Spread', color='#8888aa')
ax2.set_title('Spatial Distribution', color='#ff00ff')
ax2.tick_params(colors='#8888aa')
ax2.grid(True, alpha=0.2)

# Panel 3: Population density heatmap (conceptual)
ax3 = fig.add_subplot(gs[1, 0])
ax3.set_facecolor('#0f0f2a')

# Create a conceptual density visualization
# Show how population concentrates over time
density_phases = np.zeros((4, 4))
density_phases[0, :] = [1, 1, 1, 1]  # Uniform initially
density_phases[1, :] = [2, 1, 2, 1]  # Some clustering
density_phases[2, :] = [3, 1, 3, 1]  # Strong clustering
density_phases[3, :] = [4, 2, 4, 2]  # Dense clusters

im3 = ax3.imshow(density_phases, cmap='hot', aspect='auto')
ax3.set_xlabel('Space', color='#8888aa')
ax3.set_ylabel('Time →', color='#8888aa')
ax3.set_title('Population Clustering', color='#ffffff')
ax3.set_yticks(range(4))
ax3.set_yticklabels(['Gen 0', 'Gen 150', 'Gen 350', 'Gen 550'])
ax3.tick_params(colors='#8888aa')
plt.colorbar(im3, ax=ax3, label='Density')

# Panel 4: Growth rate
ax4 = fig.add_subplot(gs[1, 1])
ax4.set_facecolor('#0f0f2a')

growth_rates = np.diff(pop_sizes) / np.array(pop_sizes[:-1]) * 100
ax4.bar(range(len(growth_rates)), growth_rates, 
        color=['#2ecc71' if g > 0 else '#e74c3c' for g in growth_rates],
        alpha=0.7, width=1.0)
ax4.axhline(y=0, color='#ffffff', linestyle='-', linewidth=0.5)
ax4.set_xlabel('Generation', color='#8888aa')
ax4.set_ylabel('Growth Rate (%)', color='#8888aa')
ax4.set_title('Population Growth Rate', color='#ffffff')
ax4.tick_params(colors='#8888aa')
ax4.grid(True, alpha=0.2)

# Panel 5: Resource-Organism Ratio
ax5 = fig.add_subplot(gs[1, 2])
ax5.set_facecolor('#0f0f2a')

# Conceptual resource-organism ratio
max_pop = max(pop_sizes)
resource_ratio = [100 / p if p > 0 else 0 for p in pop_sizes]
ax5.plot(range(n_gens), resource_ratio, color='#00ff88', linewidth=2)
ax5.fill_between(range(n_gens), resource_ratio, alpha=0.3, color='#00ff88')
ax5.set_xlabel('Generation', color='#8888aa')
ax5.set_ylabel('Resources per Organism', color='#8888aa')
ax5.set_title('Resource Competition', color='#00ff88')
ax5.tick_params(colors='#8888aa')
ax5.grid(True, alpha=0.2)

# Main title
fig.suptitle('Ecosystem V4: Spatial Dynamics Analysis\nPopulation Clustering and Competition', 
             fontsize=16, color='#00ffff', fontweight='bold', y=0.98)

# Save
plt.savefig('spatial_dynamics_v2.png', dpi=150, bbox_inches='tight',
            facecolor='#0a0a1a', edgecolor='none')
print("Generated spatial_dynamics_v2.png")
