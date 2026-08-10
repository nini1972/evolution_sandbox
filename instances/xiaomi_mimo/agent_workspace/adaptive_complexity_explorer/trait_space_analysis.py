#!/usr/bin/env python3
"""
Trait Space Analysis - Visualizing Strategic Clusters in Ecosystem V4
Shows how the population moves through multi-dimensional trait space
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

# Extract trait data
n_gens = len(history)
traits_over_time = {
    'efficiency': [],
    'awareness': [],
    'cooperation': [],
    'frugality': [],
    'aggression': [],
    'speed': []
}

for h in history:
    for t in traits_over_time:
        traits_over_time[t].append(h['traits'][f'avg_{t}'])

# Convert to arrays
for t in traits_over_time:
    traits_over_time[t] = np.array(traits_over_time[t])

# Create figure with multiple panels
fig = plt.figure(figsize=(20, 16))
fig.patch.set_facecolor('#0a0a1a')

gs = GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.35)

# Color mapping for generations
colors = plt.cm.plasma(np.linspace(0.1, 0.9, n_gens))

# Panel 1: Efficiency vs Awareness (main strategic axis)
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_facecolor('#0f0f2a')
scatter1 = ax1.scatter(traits_over_time['efficiency'], 
                       traits_over_time['awareness'],
                       c=range(n_gens), cmap='plasma', s=30, alpha=0.8)
ax1.plot(traits_over_time['efficiency'], 
         traits_over_time['awareness'], 
         color='#00ffff', alpha=0.3, linewidth=1)
ax1.set_xlabel('Efficiency', color='#8888aa')
ax1.set_ylabel('Awareness', color='#8888aa')
ax1.set_title('Efficiency vs Awareness\n(The Primary Trade-off)', color='#00ffff')
ax1.tick_params(colors='#8888aa')
ax1.grid(True, alpha=0.2)

# Add annotations
ax1.annotate('Gen 0', (traits_over_time['efficiency'][0], 
             traits_over_time['awareness'][0]),
             textcoords="offset points", xytext=(10, 10),
             color='#00ff88', fontsize=10, fontweight='bold')
ax1.annotate('Gen 600', (traits_over_time['efficiency'][-1], 
             traits_over_time['awareness'][-1]),
             textcoords="offset points", xytext=(10, -15),
             color='#ff6b6b', fontsize=10, fontweight='bold')

# Panel 2: Cooperation vs Efficiency
ax2 = fig.add_subplot(gs[0, 1])
ax2.set_facecolor('#0f0f2a')
ax2.scatter(traits_over_time['efficiency'], 
            traits_over_time['cooperation'],
            c=range(n_gens), cmap='plasma', s=30, alpha=0.8)
ax2.plot(traits_over_time['efficiency'], 
         traits_over_time['cooperation'], 
         color='#ff00ff', alpha=0.3, linewidth=1)
ax2.set_xlabel('Efficiency', color='#8888aa')
ax2.set_ylabel('Cooperation', color='#8888aa')
ax2.set_title('Cooperation vs Efficiency\n(Individual vs Collective)', color='#ff00ff')
ax2.tick_params(colors='#8888aa')
ax2.grid(True, alpha=0.2)

# Panel 3: Speed vs Awareness
ax3 = fig.add_subplot(gs[0, 2])
ax3.set_facecolor('#0f0f2a')
ax3.scatter(traits_over_time['speed'], 
            traits_over_time['awareness'],
            c=range(n_gens), cmap='plasma', s=30, alpha=0.8)
ax3.plot(traits_over_time['speed'], 
         traits_over_time['awareness'], 
         color='#ffff00', alpha=0.3, linewidth=1)
ax3.set_xlabel('Speed', color='#8888aa')
ax3.set_ylabel('Awareness', color='#8888aa')
ax3.set_title('Speed vs Awareness\n(Sprinters vs Scouts)', color='#ffff00')
ax3.tick_params(colors='#8888aa')
ax3.grid(True, alpha=0.2)

# Panel 4: Frugality vs Aggression
ax4 = fig.add_subplot(gs[1, 0])
ax4.set_facecolor('#0f0f2a')
ax4.scatter(traits_over_time['frugality'], 
            traits_over_time['aggression'],
            c=range(n_gens), cmap='plasma', s=30, alpha=0.8)
ax4.plot(traits_over_time['frugality'], 
         traits_over_time['aggression'], 
         color='#00ff88', alpha=0.3, linewidth=1)
ax4.set_xlabel('Frugality', color='#8888aa')
ax4.set_ylabel('Aggression', color='#8888aa')
ax4.set_title('Frugality vs Aggression\n(Conservation vs Consumption)', color='#00ff88')
ax4.tick_params(colors='#8888aa')
ax4.grid(True, alpha=0.2)

# Panel 5: 3D-like visualization (Efficiency, Awareness, Cooperation)
ax5 = fig.add_subplot(gs[1, 1], projection='3d')
ax5.set_facecolor('#0f0f2a')
scatter5 = ax5.scatter(traits_over_time['efficiency'],
                       traits_over_time['awareness'],
                       traits_over_time['cooperation'],
                       c=range(n_gens), cmap='plasma', s=20, alpha=0.7)
ax5.set_xlabel('Efficiency', color='#8888aa')
ax5.set_ylabel('Awareness', color='#8888aa')
ax5.set_zlabel('Cooperation', color='#8888aa')
ax5.set_title('3D Trait Space\n(Efficiency, Awareness, Cooperation)', color='#ffffff')
ax5.tick_params(colors='#8888aa')

# Panel 6: Trait trajectory heatmap
ax6 = fig.add_subplot(gs[1, 2])
ax6.set_facecolor('#0f0f2a')
trait_names = ['speed', 'efficiency', 'cooperation', 'frugality', 'aggression', 'awareness']
trait_matrix = np.array([traits_over_time[t] for t in trait_names])
im = ax6.imshow(trait_matrix, aspect='auto', cmap='viridis', vmin=0, vmax=1)
ax6.set_xlabel('Generation', color='#8888aa')
ax6.set_ylabel('Trait', color='#8888aa')
ax6.set_title('Trait Evolution Heatmap', color='#ffffff')
ax6.set_yticks(range(6))
ax6.set_yticklabels(['Speed', 'Eff', 'Coop', 'Frug', 'Aggr', 'Aware'])
ax6.tick_params(colors='#8888aa')
plt.colorbar(im, ax=ax6, label='Trait Value')

# Panel 7: Strategic Cluster Analysis
ax7 = fig.add_subplot(gs[2, 0:2])
ax7.set_facecolor('#0f0f2a')

# Define strategic clusters based on trait combinations
# Cluster 1: Efficient Frugals (high efficiency, high frugality, low awareness)
# Cluster 2: Cooperative Scouts (higher cooperation, higher awareness)
# Cluster 3: Aggressive Sprinters (high aggression, high speed)

# Calculate cluster membership scores
eff = traits_over_time['efficiency']
fru = traits_over_time['frugality']
awa = traits_over_time['awareness']
coo = traits_over_time['cooperation']
agg = traits_over_time['aggression']
spd = traits_over_time['speed']

# Simple scoring for visualization
cluster1_score = eff + fru - awa  # Efficient Frugals
cluster2_score = coo + awa - eff  # Cooperative Scouts
cluster3_score = agg + spd - fru  # Aggressive Sprinters

ax7.plot(range(n_gens), cluster1_score, color='#2ecc71', linewidth=2, 
         label='Efficient Frugals', alpha=0.8)
ax7.plot(range(n_gens), cluster2_score, color='#3498db', linewidth=2, 
         label='Cooperative Scouts', alpha=0.8)
ax7.plot(range(n_gens), cluster3_score, color='#e74c3c', linewidth=2, 
         label='Aggressive Sprinters', alpha=0.8)

ax7.set_xlabel('Generation', color='#8888aa')
ax7.set_ylabel('Strategy Score', color='#8888aa')
ax7.set_title('Strategic Cluster Dominance Over Time', color='#ffffff')
ax7.legend(loc='upper right', facecolor='#1a1a3e', edgecolor='#333366')
ax7.tick_params(colors='#8888aa')
ax7.grid(True, alpha=0.2)

# Panel 8: Correlation matrix
ax8 = fig.add_subplot(gs[2, 2])
ax8.set_facecolor('#0f0f2a')

# Calculate correlation matrix
trait_data = np.array([traits_over_time[t] for t in trait_names])
corr_matrix = np.corrcoef(trait_data)

im8 = ax8.imshow(corr_matrix, cmap='RdBu_r', vmin=-1, vmax=1)
ax8.set_xticks(range(6))
ax8.set_yticks(range(6))
ax8.set_xticklabels(['Spd', 'Eff', 'Coo', 'Frg', 'Agg', 'Awa'], color='#8888aa')
ax8.set_yticklabels(['Spd', 'Eff', 'Coo', 'Frg', 'Agg', 'Awa'], color='#8888aa')
ax8.set_title('Trait Correlation Matrix', color='#ffffff')

# Add correlation values
for i in range(6):
    for j in range(6):
        color = 'white' if abs(corr_matrix[i, j]) > 0.5 else 'black'
        ax8.text(j, i, f'{corr_matrix[i, j]:.2f}', 
                ha='center', va='center', color=color, fontsize=8)

plt.colorbar(im8, ax=ax8, label='Correlation')

# Main title
fig.suptitle('Ecosystem V4: Trait Space Analysis\nStrategic Evolution in 600 Generations', 
             fontsize=18, color='#00ffff', fontweight='bold', y=0.98)

# Save
plt.savefig('trait_space_analysis.png', dpi=150, bbox_inches='tight',
            facecolor='#0a0a1a', edgecolor='none')
print("Generated trait_space_analysis.png")

# Print strategic insights
print("\n=== STRATEGIC INSIGHTS ===")
print(f"Efficient Frugals score: {cluster1_score[0]:.2f} → {cluster1_score[-1]:.2f}")
print(f"Cooperative Scouts score: {cluster2_score[0]:.2f} → {cluster2_score[-1]:.2f}")
print(f"Aggressive Sprinters score: {cluster3_score[0]:.2f} → {cluster3_score[-1]:.2f}")

# Find dominant strategy
final_scores = [cluster1_score[-1], cluster2_score[-1], cluster3_score[-1]]
strategies = ['Efficient Frugals', 'Cooperative Scouts', 'Aggressive Sprinters']
dominant = strategies[np.argmax(final_scores)]
print(f"\nDominant strategy at Gen 600: {dominant}")
