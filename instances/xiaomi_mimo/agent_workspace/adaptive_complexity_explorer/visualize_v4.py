#!/usr/bin/env python3
"""Visualize Ecosystem V4 results"""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# Load history
with open('history_v4.json') as f:
    history = json.load(f)

gens = [h['generation'] for h in history]
pop = [h['population'] for h in history]
diversity = [h['diversity'] for h in history]
spread = [h['spatial_spread'] for h in history]
energy = [h['avg_energy'] for h in history]

# Extract trait data
traits = ['avg_speed', 'avg_efficiency', 'avg_cooperation', 
          'avg_frugality', 'avg_aggression', 'avg_awareness']
trait_data = {t: [h['traits'][t] for h in history] for t in traits}

# Create comprehensive visualization
fig = plt.figure(figsize=(16, 20))
fig.suptitle('Ecosystem V4 - Spatial World Analysis', fontsize=16, fontweight='bold')

gs = gridspec.GridSpec(4, 2, hspace=0.35, wspace=0.3)

# 1. Population dynamics
ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(gens, pop, 'b-', linewidth=1.5)
ax1.set_xlabel('Generation')
ax1.set_ylabel('Population')
ax1.set_title('Population Dynamics')
ax1.grid(True, alpha=0.3)
ax1.fill_between(gens, pop, alpha=0.2)

# 2. Diversity over time
ax2 = fig.add_subplot(gs[0, 1])
ax2.plot(gens, diversity, 'g-', linewidth=1.5)
ax2.set_xlabel('Generation')
ax2.set_ylabel('Diversity (trait std)')
ax2.set_title('Genetic Diversity')
ax2.grid(True, alpha=0.3)
ax2.fill_between(gens, diversity, alpha=0.2, color='green')

# 3. Average energy
ax3 = fig.add_subplot(gs[1, 0])
ax3.plot(gens, energy, 'r-', linewidth=1.5)
ax3.set_xlabel('Generation')
ax3.set_ylabel('Average Energy')
ax3.set_title('Energy Dynamics')
ax3.grid(True, alpha=0.3)
ax3.axhline(y=50, color='k', linestyle='--', alpha=0.3, label='Starting energy')

# 4. Spatial spread
ax4 = fig.add_subplot(gs[1, 1])
ax4.plot(gens, spread, 'm-', linewidth=1.5)
ax4.set_xlabel('Generation')
ax4.set_ylabel('Spatial Spread')
ax4.set_title('Spatial Distribution')
ax4.grid(True, alpha=0.3)

# 5. Trait evolution (main traits)
ax5 = fig.add_subplot(gs[2, :])
colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
for t, c in zip(traits[:4], colors[:4]):
    ax5.plot(gens, trait_data[t], label=t.replace('avg_', ''), 
             linewidth=1.5, color=c)
ax5.set_xlabel('Generation')
ax5.set_ylabel('Trait Value')
ax5.set_title('Trait Evolution (Primary Traits)')
ax5.legend(loc='best')
ax5.grid(True, alpha=0.3)
ax5.set_ylim(0, 1)

# 6. Aggression and Awareness evolution
ax6 = fig.add_subplot(gs[3, 0])
ax6.plot(gens, trait_data['avg_aggression'], label='Aggression', 
         color='#9b59b6', linewidth=1.5)
ax6.plot(gens, trait_data['avg_awareness'], label='Awareness', 
         color='#1abc9c', linewidth=1.5)
ax6.set_xlabel('Generation')
ax6.set_ylabel('Trait Value')
ax6.set_title('Behavioral Traits')
ax6.legend()
ax6.grid(True, alpha=0.3)

# 7. Final trait distribution radar chart
ax7 = fig.add_subplot(gs[3, 1], projection='polar')
final_traits = [trait_data[t][-1] for t in traits]
initial_traits = [trait_data[t][0] for t in traits]
trait_labels = [t.replace('avg_', '') for t in traits]

angles = np.linspace(0, 2 * np.pi, len(traits), endpoint=False).tolist()
angles += angles[:1]
final_traits_plot = final_traits + final_traits[:1]
initial_traits_plot = initial_traits + initial_traits[:1]

ax7.plot(angles, final_traits_plot, 'o-', linewidth=2, label='Final', color='blue')
ax7.fill(angles, final_traits_plot, alpha=0.25, color='blue')
ax7.plot(angles, initial_traits_plot, 'o--', linewidth=1, label='Initial', color='gray')
ax7.fill(angles, initial_traits_plot, alpha=0.1, color='gray')
ax7.set_xticks(angles[:-1])
ax7.set_xticklabels(trait_labels, size=8)
ax7.set_title('Trait Comparison\n(Initial vs Final)', pad=20)
ax7.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))

plt.savefig('ecosystem_v4_analysis.png', dpi=150, bbox_inches='tight')
print("Saved ecosystem_v4_analysis.png")
plt.close()
