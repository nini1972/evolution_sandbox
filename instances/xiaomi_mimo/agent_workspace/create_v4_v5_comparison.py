#!/usr/bin/env python3
"""
Compare V4 (Normal Mutation) vs V5 (High Mutation)
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import json

# Load both histories
with open('adaptive_complexity_explorer/history_v4.json', 'r') as f:
    history_v4 = json.load(f)

with open('adaptive_complexity_explorer/history_v5_high_mutation.json', 'r') as f:
    history_v5 = json.load(f)

# Ensure both histories have the same length (use minimum)
min_len = min(len(history_v4), len(history_v5))
history_v4 = history_v4[:min_len]
history_v5 = history_v5[:min_len]

# Create comparison figure
fig, axes = plt.subplots(3, 3, figsize=(16, 14))
fig.patch.set_facecolor('#0a0a1a')

fig.suptitle('Mutation Rate Experiment: V4 (Low) vs V5 (High)', 
             fontsize=18, color='#00ffff', fontweight='bold')

# Panel 1: Population Comparison
ax1 = axes[0, 0]
ax1.set_facecolor('#0f0f2a')

gens = [h['generation'] for h in history_v4]
pop_v4 = [h['population'] for h in history_v4]
pop_v5 = [h['population'] for h in history_v5]

ax1.fill_between(gens, pop_v4, alpha=0.4, color='#00ff88', label='V4 (Low Mutation)')
ax1.fill_between(gens, pop_v5, alpha=0.4, color='#ff00ff', label='V5 (High Mutation)')
ax1.plot(gens, pop_v4, color='#00ff88', linewidth=2)
ax1.plot(gens, pop_v5, color='#ff00ff', linewidth=2)

ax1.set_title('Population Dynamics', color='#00ffff', fontsize=12)
ax1.set_xlabel('Generation', color='#8888aa')
ax1.set_ylabel('Population', color='#8888aa')
ax1.legend(facecolor='#1a1a3e', edgecolor='#444466')
ax1.tick_params(colors='#8888aa')
ax1.grid(True, alpha=0.2)

# Panel 2: Efficiency Comparison
ax2 = axes[0, 1]
ax2.set_facecolor('#0f0f2a')

eff_v4 = [h['traits']['avg_efficiency'] for h in history_v4]
eff_v5 = [h['traits']['avg_efficiency'] for h in history_v5]

ax2.plot(gens, eff_v4, color='#00ff88', linewidth=2, label='V4')
ax2.plot(gens, eff_v5, color='#ff00ff', linewidth=2, label='V5')
ax2.set_title('Efficiency Evolution', color='#00ffff', fontsize=12)
ax2.set_xlabel('Generation', color='#8888aa')
ax2.set_ylabel('Avg Efficiency', color='#8888aa')
ax2.legend(facecolor='#1a1a3e', edgecolor='#444466')
ax2.tick_params(colors='#8888aa')
ax2.grid(True, alpha=0.2)

# Panel 3: Cooperation Comparison
ax3 = axes[0, 2]
ax3.set_facecolor('#0f0f2a')

coop_v4 = [h['traits']['avg_cooperation'] for h in history_v4]
coop_v5 = [h['traits']['avg_cooperation'] for h in history_v5]

ax3.plot(gens, coop_v4, color='#00ff88', linewidth=2, label='V4')
ax3.plot(gens, coop_v5, color='#ff00ff', linewidth=2, label='V5')
ax3.set_title('Cooperation Evolution', color='#00ffff', fontsize=12)
ax3.set_xlabel('Generation', color='#8888aa')
ax3.set_ylabel('Avg Cooperation', color='#8888aa')
ax3.legend(facecolor='#1a1a3e', edgecolor='#444466')
ax3.tick_params(colors='#8888aa')
ax3.grid(True, alpha=0.2)

# Panel 4: Awareness Comparison
ax4 = axes[1, 0]
ax4.set_facecolor('#0f0f2a')

aware_v4 = [h['traits']['avg_awareness'] for h in history_v4]
aware_v5 = [h['traits']['avg_awareness'] for h in history_v5]

ax4.plot(gens, aware_v4, color='#00ff88', linewidth=2, label='V4')
ax4.plot(gens, aware_v5, color='#ff00ff', linewidth=2, label='V5')
ax4.set_title('Awareness Evolution', color='#00ffff', fontsize=12)
ax4.set_xlabel('Generation', color='#8888aa')
ax4.set_ylabel('Avg Awareness', color='#8888aa')
ax4.legend(facecolor='#1a1a3e', edgecolor='#444466')
ax4.tick_params(colors='#8888aa')
ax4.grid(True, alpha=0.2)

# Panel 5: Frugality Comparison
ax5 = axes[1, 1]
ax5.set_facecolor('#0f0f2a')

frug_v4 = [h['traits']['avg_frugality'] for h in history_v4]
frug_v5 = [h['traits']['avg_frugality'] for h in history_v5]

ax5.plot(gens, frug_v4, color='#00ff88', linewidth=2, label='V4')
ax5.plot(gens, frug_v5, color='#ff00ff', linewidth=2, label='V5')
ax5.set_title('Frugality Evolution', color='#00ffff', fontsize=12)
ax5.set_xlabel('Generation', color='#8888aa')
ax5.set_ylabel('Avg Frugality', color='#8888aa')
ax5.legend(facecolor='#1a1a3e', edgecolor='#444466')
ax5.tick_params(colors='#8888aa')
ax5.grid(True, alpha=0.2)

# Panel 6: Aggression Comparison
ax6 = axes[1, 2]
ax6.set_facecolor('#0f0f2a')

agg_v4 = [h['traits']['avg_aggression'] for h in history_v4]
agg_v5 = [h['traits']['avg_aggression'] for h in history_v5]

ax6.plot(gens, agg_v4, color='#00ff88', linewidth=2, label='V4')
ax6.plot(gens, agg_v5, color='#ff00ff', linewidth=2, label='V5')
ax6.set_title('Aggression Evolution', color='#00ffff', fontsize=12)
ax6.set_xlabel('Generation', color='#8888aa')
ax6.set_ylabel('Avg Aggression', color='#8888aa')
ax6.legend(facecolor='#1a1a3e', edgecolor='#444466')
ax6.tick_params(colors='#8888aa')
ax6.grid(True, alpha=0.2)

# Panel 7: Final Trait Comparison Bar Chart
ax7 = axes[2, 0]
ax7.set_facecolor('#0f0f2a')

traits = ['Efficiency', 'Cooperation', 'Awareness', 'Frugality', 'Aggression']
final_v4 = [0.917, 0.368, 0.234, 0.746, 0.263]
final_v5 = [0.930, 0.327, 0.430, 0.691, 0.437]

x = np.arange(len(traits))
width = 0.35

bars1 = ax7.bar(x - width/2, final_v4, width, label='V4', color='#00ff88', alpha=0.8)
bars2 = ax7.bar(x + width/2, final_v5, width, label='V5', color='#ff00ff', alpha=0.8)

ax7.set_title('Final Trait Values', color='#00ffff', fontsize=12)
ax7.set_xticks(x)
ax7.set_xticklabels(traits)
ax7.set_ylabel('Value', color='#8888aa')
ax7.legend(facecolor='#1a1a3e', edgecolor='#444466')
ax7.tick_params(colors='#8888aa')
ax7.grid(True, alpha=0.2, axis='y')

# Panel 8: Diversity Comparison
ax8 = axes[2, 1]
ax8.set_facecolor('#0f0f2a')

div_v4 = [h['diversity'] for h in history_v4]
div_v5 = [h['diversity'] for h in history_v5]

ax8.plot(gens, div_v4, color='#00ff88', linewidth=2, label='V4')
ax8.plot(gens, div_v5, color='#ff00ff', linewidth=2, label='V5')
ax8.set_title('Genetic Diversity', color='#00ffff', fontsize=12)
ax8.set_xlabel('Generation', color='#8888aa')
ax8.set_ylabel('Diversity Index', color='#8888aa')
ax8.legend(facecolor='#1a1a3e', edgecolor='#444466')
ax8.tick_params(colors='#8888aa')
ax8.grid(True, alpha=0.2)

# Panel 9: Key Findings Summary
ax9 = axes[2, 2]
ax9.set_facecolor('#0f0f2a')
ax9.axis('off')

findings = """
KEY FINDINGS

V4 (Low Mutation):
- Population: ~570
- Efficiency: 0.917 (+41.6%)
- Awareness: 0.234 (-56.1%)
- Cooperation: 0.368 (-19.6%)
- Strong convergence

V5 (High Mutation):
- Population: ~405
- Efficiency: 0.930 (+43.4%)
- Awareness: 0.430 (-19.3%)
- Cooperation: 0.327 (-28.6%)
- Maintains more variation

INSIGHT:
High mutation maintains
awareness diversity but
reduces overall population.
"""

ax9.text(0.5, 0.5, findings, ha='center', va='center',
         fontsize=10, color='#00ffff', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='#1a1a3e', edgecolor='#00ffff', alpha=0.8))

# Bottom text
fig.text(0.5, 0.01, 
         'Experiment: Mutation Rate Impact | V4 vs V5 Comparison',
         ha='center', fontsize=10, color='#666688')

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('mutation_experiment_comparison.png', dpi=150, bbox_inches='tight',
            facecolor='#0a0a1a', edgecolor='none')
print("Generated mutation_experiment_comparison.png")
