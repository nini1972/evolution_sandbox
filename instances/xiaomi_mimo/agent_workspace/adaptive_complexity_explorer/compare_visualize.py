#!/usr/bin/env python3
"""Compare experiment results"""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# Load results
with open('experiment_results.json') as f:
    experiments = json.load(f)

fig = plt.figure(figsize=(16, 12))
fig.suptitle('Comparative Analysis: Ecosystem V4 Under Different Conditions', 
             fontsize=14, fontweight='bold')

gs = gridspec.GridSpec(2, 2, hspace=0.35, wspace=0.3)

colors = ['#e74c3c', '#3498db', '#2ecc71']

# 1. Population dynamics comparison
ax1 = fig.add_subplot(gs[0, 0])
for i, exp in enumerate(experiments):
    gens = exp['history_summary']['generations']
    pop = exp['history_summary']['population']
    ax1.plot(gens, pop, color=colors[i], label=exp['name'].split('(')[0].strip(), 
             linewidth=1.5)
ax1.set_xlabel('Generation')
ax1.set_ylabel('Population')
ax1.set_title('Population Dynamics by Configuration')
ax1.legend(fontsize=8)
ax1.grid(True, alpha=0.3)

# 2. Diversity comparison
ax2 = fig.add_subplot(gs[0, 1])
for i, exp in enumerate(experiments):
    gens = exp['history_summary']['generations']
    diversity = exp['history_summary']['diversity']
    ax2.plot(gens, diversity, color=colors[i], label=exp['name'].split('(')[0].strip(), 
             linewidth=1.5)
ax2.set_xlabel('Generation')
ax2.set_ylabel('Diversity')
ax2.set_title('Genetic Diversity by Configuration')
ax2.legend(fontsize=8)
ax2.grid(True, alpha=0.3)

# 3. Energy comparison
ax3 = fig.add_subplot(gs[1, 0])
for i, exp in enumerate(experiments):
    gens = exp['history_summary']['generations']
    energy = exp['history_summary']['avg_energy']
    ax3.plot(gens, energy, color=colors[i], label=exp['name'].split('(')[0].strip(), 
             linewidth=1.5)
ax3.set_xlabel('Generation')
ax3.set_ylabel('Average Energy')
ax3.set_title('Energy Dynamics by Configuration')
ax3.legend(fontsize=8)
ax3.grid(True, alpha=0.3)

# 4. Final traits radar chart
ax4 = fig.add_subplot(gs[1, 1], projection='polar')
trait_names = list(experiments[0]['history_summary']['traits'].keys())
trait_labels = [t.replace('avg_', '') for t in trait_names]

angles = np.linspace(0, 2 * np.pi, len(trait_names), endpoint=False).tolist()
angles += angles[:1]

for i, exp in enumerate(experiments):
    final_traits = [exp['history_summary']['traits'][t] for t in trait_names]
    final_traits_plot = final_traits + final_traits[:1]
    ax4.plot(angles, final_traits_plot, 'o-', color=colors[i], 
             label=exp['name'].split('(')[0].strip(), linewidth=1.5)
    ax4.fill(angles, final_traits_plot, alpha=0.1, color=colors[i])

ax4.set_xticks(angles[:-1])
ax4.set_xticklabels(trait_labels, size=8)
ax4.set_title('Final Trait Profiles\n(Comparison)', pad=20)
ax4.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=8)

plt.savefig('experiment_comparison.png', dpi=150, bbox_inches='tight')
print("Saved experiment_comparison.png")
plt.close()
