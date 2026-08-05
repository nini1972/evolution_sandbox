#!/usr/bin/env python3
"""
Comprehensive Dashboard - Ecosystem V4 Analysis
"""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# Load data
with open('extended_history.json') as f:
    ext_history = json.load(f)

with open('experiment_results.json') as f:
    experiments = json.load(f)

# Create figure
fig = plt.figure(figsize=(18, 14))
fig.patch.set_facecolor('#1a1a2e')

# Title
fig.suptitle('Ecosystem V4: Emergent Complexity Analysis Dashboard', 
             fontsize=16, fontweight='bold', color='white', y=0.98)

gs = gridspec.GridSpec(3, 3, hspace=0.4, wspace=0.35, 
                       left=0.08, right=0.95, top=0.93, bottom=0.05)

# Style helper
def style_ax(ax, title):
    ax.set_facecolor('#16213e')
    ax.set_title(title, color='white', fontsize=11, fontweight='bold')
    ax.tick_params(colors='gray')
    for spine in ax.spines.values():
        spine.set_color('#333')
    ax.grid(True, alpha=0.2, color='gray')

# Extract extended run data
gens = [h['generation'] for h in ext_history]
pops = [h['population'] for h in ext_history]
divs = [h['diversity'] for h in ext_history]
spreads = [h['spatial_spread'] for h in ext_history]
energies = [h['avg_energy'] for h in ext_history]

# ---- Plot 1: Population over time ----
ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(gens, pops, color='#e94560', linewidth=1.5)
ax1.fill_between(gens, pops, alpha=0.2, color='#e94560')
style_ax(ax1, 'Population Dynamics')
ax1.set_ylabel('Population', color='gray')

# ---- Plot 2: Diversity over time ----
ax2 = fig.add_subplot(gs[0, 1])
ax2.plot(gens, divs, color='#0f3460', linewidth=1.5)
ax2.plot(gens, spreads, color='#533483', linewidth=1.5, alpha=0.7, label='Spatial Spread')
style_ax(ax2, 'Diversity & Spatial Spread')
ax2.set_ylabel('Value', color='gray')
ax2.legend(fontsize=8, facecolor='#1a1a2e', edgecolor='gray', labelcolor='gray')

# ---- Plot 3: Energy over time ----
ax3 = fig.add_subplot(gs[0, 2])
ax3.plot(gens, energies, color='#e94560', linewidth=1.5)
style_ax(ax3, 'Average Energy')
ax3.set_ylabel('Energy', color='gray')

# ---- Plot 4: Trait Evolution (Speed) ----
ax4 = fig.add_subplot(gs[1, 0])
traits_to_plot = ['avg_speed', 'avg_efficiency', 'avg_awareness']
colors_traits = ['#e94560', '#0f3460', '#533483']
for trait, color in zip(traits_to_plot, colors_traits):
    vals = [h['traits'].get(trait, 0) for h in ext_history]
    label = trait.replace('avg_', '').title()
    ax4.plot(gens, vals, color=color, linewidth=1.5, label=label)
style_ax(ax4, 'Trait Evolution: Speed, Efficiency, Awareness')
ax4.set_ylabel('Trait Value', color='gray')
ax4.legend(fontsize=8, facecolor='#1a1a2e', edgecolor='gray', labelcolor='gray')

# ---- Plot 5: Trait Evolution (Social) ----
ax5 = fig.add_subplot(gs[1, 1])
traits_to_plot2 = ['avg_cooperation', 'avg_aggression', 'avg_frugality']
colors_traits2 = ['#533483', '#e94560', '#0f3460']
for trait, color in zip(traits_to_plot2, colors_traits2):
    vals = [h['traits'].get(trait, 0) for h in ext_history]
    label = trait.replace('avg_', '').title()
    ax5.plot(gens, vals, color=color, linewidth=1.5, label=label)
style_ax(ax5, 'Trait Evolution: Social Strategies')
ax5.set_ylabel('Trait Value', color='gray')
ax5.legend(fontsize=8, facecolor='#1a1a2e', edgecolor='gray', labelcolor='gray')

# ---- Plot 6: Phase portrait (Diversity vs Population) ----
ax6 = fig.add_subplot(gs[1, 2])
scatter = ax6.scatter(pops[:-1], divs[1:], c=gens[:-1], cmap='plasma', 
                       s=15, alpha=0.7)
plt.colorbar(scatter, ax=ax6, label='Generation', pad=0.02)
style_ax(ax6, 'Phase Portrait: Pop vs Diversity')
ax6.set_xlabel('Population', color='gray')
ax6.set_ylabel('Diversity (next gen)', color='gray')

# ---- Plot 7: Experiment comparison - Population ----
ax7 = fig.add_subplot(gs[2, 0])
exp_colors = ['#e94560', '#0f3460', '#533483']
for i, exp in enumerate(experiments):
    gens_e = exp['history_summary']['generations']
    pop_e = exp['history_summary']['population']
    label = exp['name'].split('(')[0].strip()
    ax7.plot(gens_e, pop_e, color=exp_colors[i], linewidth=1.5, label=label)
style_ax(ax7, 'Experiment Comparison: Population')
ax7.set_xlabel('Generation', color='gray')
ax7.set_ylabel('Population', color='gray')
ax7.legend(fontsize=7, facecolor='#1a1a2e', edgecolor='gray', labelcolor='gray')

# ---- Plot 8: Experiment comparison - Diversity ----
ax8 = fig.add_subplot(gs[2, 1])
for i, exp in enumerate(experiments):
    gens_e = exp['history_summary']['generations']
    div_e = exp['history_summary']['diversity']
    label = exp['name'].split('(')[0].strip()
    ax8.plot(gens_e, div_e, color=exp_colors[i], linewidth=1.5, label=label)
style_ax(ax8, 'Experiment Comparison: Diversity')
ax8.set_xlabel('Generation', color='gray')
ax8.set_ylabel('Diversity', color='gray')
ax8.legend(fontsize=7, facecolor='#1a1a2e', edgecolor='gray', labelcolor='gray')

# ---- Plot 9: Final trait radar chart ----
ax9 = fig.add_subplot(gs[2, 2], projection='polar')
ax9.set_facecolor('#16213e')

# Get final traits from extended run
final_traits = ext_history[-1]['traits']
trait_names = list(final_traits.keys())
trait_labels = [t.replace('avg_', '').title() for t in trait_names]
trait_values = list(final_traits.values())

angles = np.linspace(0, 2 * np.pi, len(trait_names), endpoint=False).tolist()
angles += angles[:1]
trait_values_plot = trait_values + trait_values[:1]

ax9.plot(angles, trait_values_plot, 'o-', color='#e94560', linewidth=2)
ax9.fill(angles, trait_values_plot, alpha=0.3, color='#e94560')

# Add experiment final traits for comparison
for i, exp in enumerate(experiments):
    final_e = exp['history_summary']['traits']
    vals = [final_e.get(t, 0) for t in trait_names]
    vals_plot = vals + vals[:1]
    ax9.plot(angles, vals_plot, '--', color=exp_colors[i], linewidth=1.2, alpha=0.7)

ax9.set_xticks(angles[:-1])
ax9.set_xticklabels(trait_labels, size=8, color='gray')
ax9.set_title('Final Trait Profiles', color='white', fontsize=11, fontweight='bold', pad=20)
ax9.set_rgrids([0.2, 0.4, 0.6, 0.8], labels=['0.2', '0.4', '0.6', '0.8'], 
               fontsize=7, color='gray')
ax9.tick_params(colors='gray')
ax9.grid(color='gray', alpha=0.3)

# Legend for radar
from matplotlib.lines import Line2D
legend_elements = [Line2D([0], [0], color='#e94560', linewidth=2, label='Extended Run')]
for i, exp in enumerate(experiments):
    name = exp['name'].split('(')[0].strip()
    legend_elements.append(Line2D([0], [0], color=exp_colors[i], linewidth=1.2, 
                                   linestyle='--', label=name))
ax9.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.4, 1.1), 
           fontsize=7, facecolor='#1a1a2e', edgecolor='gray', labelcolor='gray')

plt.savefig('dashboard_v4.png', dpi=150, bbox_inches='tight', 
            facecolor=fig.get_facecolor())
print("Saved dashboard_v4.png")
plt.close()

# Print summary statistics
print("\n" + "="*60)
print("DASHBOARD SUMMARY")
print("="*60)
print(f"\nExtended Run Final State (Gen {ext_history[-1]['generation']}):")
print(f"  Population: {ext_history[-1]['population']}")
print(f"  Diversity: {ext_history[-1]['diversity']:.4f}")
print(f"  Avg Energy: {ext_history[-1]['avg_energy']:.2f}")
print(f"  Spatial Spread: {ext_history[-1]['spatial_spread']:.2f}")
print(f"\nFinal Traits:")
for k, v in ext_history[-1]['traits'].items():
    print(f"  {k}: {v:.4f}")

print(f"\nExperiment Comparisons (at Gen 150):")
for exp in experiments:
    print(f"  {exp['name']}:")
    print(f"    Pop: {exp['final_state']['population']}, "
          f"Time: {exp['final_state']['elapsed_seconds']:.1f}s")
