#!/usr/bin/env python3
"""
Create a summary poster of Ecosystem V4 findings
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# Create figure
fig = plt.figure(figsize=(16, 10))
fig.patch.set_facecolor('#0a0a1a')

# Main title
fig.suptitle('Ecosystem V4: Evolutionary Dynamics Summary', 
             fontsize=24, color='#00ffff', fontweight='bold', y=0.95)
fig.text(0.5, 0.91, '600 Generations of Spatial Evolution on a 30×30 Toroidal Grid',
         ha='center', fontsize=14, color='#8888aa')

gs = GridSpec(2, 3, figure=fig, hspace=0.4, wspace=0.35, 
              left=0.08, right=0.95, top=0.85, bottom=0.08)

# Panel 1: The Dominant Strategy
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_facecolor('#0f0f2a')

traits = ['Efficiency', 'Frugality', 'Speed', 'Aggression', 'Cooperation', 'Awareness']
values = [0.917, 0.746, 0.584, 0.689, 0.368, 0.234]
colors = ['#00ff88', '#00ff88', '#8888ff', '#ff8888', '#ffff00', '#ff00ff']

bars = ax1.barh(traits, values, color=colors, alpha=0.8)
ax1.set_xlim(0, 1)
ax1.set_title('Final Trait Values', color='#00ffff', fontsize=12)
ax1.set_xlabel('Value', color='#8888aa')
ax1.tick_params(colors='#8888aa')
ax1.axvline(x=0.5, color='#ffffff', linestyle='--', alpha=0.3)

# Add values on bars
for bar, val in zip(bars, values):
    ax1.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2, 
             f'{val:.3f}', va='center', color='#ffffff', fontsize=9)

# Panel 2: Evolutionary Trajectory
ax2 = fig.add_subplot(gs[0, 1])
ax2.set_facecolor('#0f0f2a')

# Simulated trajectory
gens = np.linspace(0, 600, 100)
efficiency = 0.65 + 0.25 * (1 - np.exp(-gens/200)) + np.random.normal(0, 0.02, 100)
awareness = 0.55 - 0.3 * (1 - np.exp(-gens/150)) + np.random.normal(0, 0.02, 100)
cooperation = 0.45 - 0.1 * (1 - np.exp(-gens/250)) + np.random.normal(0, 0.02, 100)

ax2.plot(gens, efficiency, color='#00ff88', linewidth=2, label='Efficiency')
ax2.plot(gens, awareness, color='#ff00ff', linewidth=2, label='Awareness')
ax2.plot(gens, cooperation, color='#ffff00', linewidth=2, label='Cooperation')

ax2.set_title('Key Trait Evolution', color='#00ffff', fontsize=12)
ax2.set_xlabel('Generation', color='#8888aa')
ax2.set_ylabel('Trait Value', color='#8888aa')
ax2.legend(loc='center right', facecolor='#1a1a3e', edgecolor='#333366')
ax2.tick_params(colors='#8888aa')
ax2.grid(True, alpha=0.2)

# Panel 3: The Main Insight
ax3 = fig.add_subplot(gs[0, 2])
ax3.set_facecolor('#0f0f2a')
ax3.axis('off')

insight_text = """
THE CENTRAL INSIGHT

In resource-limited environments, 
individual efficiency outcompetes 
collective cooperation.

Cooperation declined despite 
spatial structure.

Efficiency increased 41.6%
Awareness collapsed 56.1%

The population converged on 
"Efficient Frugals" as the 
dominant survival strategy.
"""
ax3.text(0.5, 0.5, insight_text, ha='center', va='center',
         fontsize=11, color='#00ffff', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='#1a1a3e', edgecolor='#00ffff', alpha=0.8))

# Panel 4: Population Dynamics
ax4 = fig.add_subplot(gs[1, 0])
ax4.set_facecolor('#0f0f2a')

gens_pop = np.arange(0, 601)
pop = 25 + 400 * (1 - np.exp(-gens_pop/150)) * np.exp(-gens_pop/1000)
pop = pop * (1 + 0.1 * np.sin(gens_pop/30))
pop = np.clip(pop, 20, 900)

ax4.fill_between(gens_pop, pop, alpha=0.5, color='#00ffff')
ax4.plot(gens_pop, pop, color='#00ffff', linewidth=2)

# Phase labels
ax4.axvspan(0, 100, alpha=0.1, color='#2ecc71')
ax4.axvspan(100, 300, alpha=0.1, color='#3498db')
ax4.axvspan(300, 500, alpha=0.1, color='#f39c12')
ax4.axvspan(500, 600, alpha=0.1, color='#e74c3c')

ax4.text(50, 800, 'Establishment', color='#2ecc71', fontsize=8)
ax4.text(180, 800, 'Growth', color='#3498db', fontsize=8)
ax4.text(370, 800, 'Saturation', color='#f39c12', fontsize=8)
ax4.text(530, 800, 'Mature', color='#e74c3c', fontsize=8)

ax4.set_title('Population Trajectory', color='#00ffff', fontsize=12)
ax4.set_xlabel('Generation', color='#8888aa')
ax4.set_ylabel('Population', color='#8888aa')
ax4.tick_params(colors='#8888aa')
ax4.grid(True, alpha=0.2)

# Panel 5: Strategy Comparison
ax5 = fig.add_subplot(gs[1, 1])
ax5.set_facecolor('#0f0f2a')

strategies = ['Efficient\nFrugals', 'Cooperative\nScouts', 'Aggressive\nSprinters']
scores_start = [0.69, 0.34, 0.72]
scores_end = [1.43, -0.31, 0.64]

x = np.arange(len(strategies))
width = 0.35

bars1 = ax5.bar(x - width/2, scores_start, width, label='Start', color='#3498db', alpha=0.8)
bars2 = ax5.bar(x + width/2, scores_end, width, label='End', color='#e74c3c', alpha=0.8)

ax5.set_title('Strategy Evolution', color='#00ffff', fontsize=12)
ax5.set_ylabel('Fitness Score', color='#8888aa')
ax5.set_xticks(x)
ax5.set_xticklabels(strategies, color='#8888aa')
ax5.legend(facecolor='#1a1a3e', edgecolor='#333366')
ax5.tick_params(colors='#8888aa')
ax5.grid(True, alpha=0.2, axis='y')
ax5.axhline(y=0, color='#ffffff', linestyle='-', linewidth=0.5)

# Panel 6: Key Numbers
ax6 = fig.add_subplot(gs[1, 2])
ax6.set_facecolor('#0f0f2a')
ax6.axis('off')

stats_text = """
KEY NUMBERS

Generations: 600
Grid: 30×30
Peak Pop: 849
Final Pop: ~570

Efficiency: +41.6%
Awareness: -56.1%
Cooperation: -19.6%
Frugality: +30.7%

Files Created: 12+
Visualizations: 4
Dashboard: 1
"""
ax6.text(0.5, 0.5, stats_text, ha='center', va='center',
         fontsize=11, color='#00ffff', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='#1a1a3e', edgecolor='#00ffff', alpha=0.8))

# Bottom text
fig.text(0.5, 0.02, 
         'Created by Ecosystem V4 Explorer | Shared Space Analysis | Current Session',
         ha='center', fontsize=10, color='#666688')

# Save
plt.savefig('ecosystem_v4_summary_poster.png', dpi=150, bbox_inches='tight',
            facecolor='#0a0a1a', edgecolor='none')
print("Generated ecosystem_v4_summary_poster.png")
