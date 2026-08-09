#!/usr/bin/env python3
"""
Deep Analysis of Ecosystem V4 - Long-term Evolutionary Patterns
Examines the 600-generation dataset for emergent behaviors and phase transitions
"""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# Simple smoothing function without scipy
def smooth(data, window=5):
    """Simple moving average smoothing"""
    result = []
    for i in range(len(data)):
        start = max(0, i - window//2)
        end = min(len(data), i + window//2 + 1)
        result.append(np.mean(data[start:end]))
    return np.array(result)

# Load data
with open('extended_history.json', 'r') as f:
    history = json.load(f)

print(f"Loaded {len(history)} generations of data")

# Extract time series
gens = [h['generation'] for h in history]
pops = [h['population'] for h in history]
energies = [h['avg_energy'] for h in history]
diversities = [h['diversity'] for h in history]
spreads = [h['spatial_spread'] for h in history]

# Extract trait evolution
trait_names = ['avg_speed', 'avg_efficiency', 'avg_cooperation', 
               'avg_frugality', 'avg_aggression', 'avg_awareness']
trait_data = {t: [h['traits'][t] for h in history] for t in trait_names}

# Calculate derived metrics
energy_efficiency = [e/p if p > 0 else 0 for e, p in zip(energies, pops)]

# ============================================================
# Create comprehensive analysis figure
# ============================================================
fig = plt.figure(figsize=(24, 18))
fig.patch.set_facecolor('#0a0a1a')

fig.suptitle('ECOSYSTEM V4: DEEP EVOLUTIONARY ANALYSIS\n600-Generation Spatial Simulation',
             fontsize=18, fontweight='bold', color='white', y=0.98)

gs = GridSpec(3, 4, figure=fig, hspace=0.35, wspace=0.35)

colors = {
    'speed': '#e74c3c',
    'efficiency': '#2ecc71', 
    'cooperation': '#3498db',
    'frugality': '#f39c12',
    'aggression': '#9b59b6',
    'awareness': '#1abc9c'
}

# Panel 1: Population Dynamics
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_facecolor('#0f0f2a')
pop_smooth = smooth(pops, window=7)
ax1.plot(gens, pops, color='#00ffff', alpha=0.3, linewidth=0.8)
ax1.plot(gens, pop_smooth, color='#00ffff', linewidth=2.5, label='Population (smoothed)')
ax1.axvspan(0, 100, alpha=0.1, color='green', label='Establishment')
ax1.axvspan(100, 300, alpha=0.1, color='yellow', label='Growth')
ax1.axvspan(300, 500, alpha=0.1, color='orange', label='Saturation')
ax1.axvspan(500, 600, alpha=0.1, color='red', label='Mature')
ax1.set_xlabel('Generation', fontsize=10, color='#8888aa')
ax1.set_ylabel('Population', fontsize=10, color='#8888aa')
ax1.set_title('POPULATION DYNAMICS', fontsize=12, fontweight='bold', color='white')
ax1.legend(fontsize=7, loc='upper left')
ax1.tick_params(colors='#6666aa')
for spine in ax1.spines.values(): spine.set_color('#333366')

# Panel 2: Energy Landscape
ax2 = fig.add_subplot(gs[0, 1])
ax2.set_facecolor('#0f0f2a')
ax2.fill_between(gens, energies, alpha=0.3, color='#ff6b6b')
ax2.plot(gens, energies, color='#ff6b6b', linewidth=2, label='Avg Energy')
ax2_twin = ax2.twinx()
ax2_twin.plot(gens, energy_efficiency, color='#4ecdc4', linewidth=2, linestyle='--', label='Efficiency')
ax2_twin.set_ylabel('Energy/Organism', fontsize=10, color='#4ecdc4')
ax2.set_xlabel('Generation', fontsize=10, color='#8888aa')
ax2.set_ylabel('Average Energy', fontsize=10, color='#ff6b6b')
ax2.set_title('ENERGY LANDSCAPE', fontsize=12, fontweight='bold', color='white')
ax2.tick_params(colors='#6666aa')
ax2_twin.tick_params(colors='#4ecdc4')
for spine in ax2.spines.values(): spine.set_color('#333366')

# Panel 3: Trait Evolution
ax3 = fig.add_subplot(gs[0, 2:])
ax3.set_facecolor('#0f0f2a')
for trait in trait_names:
    data = smooth(trait_data[trait], window=10)
    ax3.plot(gens, data, color=colors[trait.replace('avg_', '')], 
             linewidth=2.5, label=trait.replace('avg_', '').capitalize())
ax3.set_xlabel('Generation', fontsize=10, color='#8888aa')
ax3.set_ylabel('Trait Value', fontsize=10, color='#8888aa')
ax3.set_title('TRAIT EVOLUTION TRAJECTORIES', fontsize=12, fontweight='bold', color='white')
ax3.legend(fontsize=8, ncol=2, loc='center right')
ax3.set_ylim(0.1, 1.0)
ax3.tick_params(colors='#6666aa')
for spine in ax3.spines.values(): spine.set_color('#333366')
ax3.grid(True, alpha=0.2, color='#4444aa')

# Panel 4: Cooperation vs Aggression
ax4 = fig.add_subplot(gs[1, 0])
ax4.set_facecolor('#0f0f2a')
ax4.plot(gens, trait_data['avg_cooperation'], color=colors['cooperation'], linewidth=2, alpha=0.8, label='Cooperation')
ax4.plot(gens, trait_data['avg_aggression'], color=colors['aggression'], linewidth=2, alpha=0.8, label='Aggression')
coop_arr = np.array(trait_data['avg_cooperation'])
agg_arr = np.array(trait_data['avg_aggression'])
ax4.fill_between(gens, coop_arr, agg_arr, where=coop_arr > agg_arr, alpha=0.2, color='blue')
ax4.fill_between(gens, coop_arr, agg_arr, where=coop_arr < agg_arr, alpha=0.2, color='red')
ax4.axhline(y=0.5, color='white', linestyle=':', alpha=0.3)
ax4.set_xlabel('Generation', fontsize=10, color='#8888aa')
ax4.set_ylabel('Trait Value', fontsize=10, color='#8888aa')
ax4.set_title('COOPERATION vs AGGRESSION', fontsize=12, fontweight='bold', color='white')
ax4.legend(fontsize=7, loc='center right')
ax4.tick_params(colors='#6666aa')
for spine in ax4.spines.values(): spine.set_color('#333366')

# Panel 5: Phase Space
ax5 = fig.add_subplot(gs[1, 1])
ax5.set_facecolor('#0f0f2a')
scatter = ax5.scatter(pops, diversities, c=gens, cmap='plasma', s=15, alpha=0.7, edgecolors='none')
ax5.plot(pops, diversities, color='white', alpha=0.3, linewidth=0.5)
ax5.set_xlabel('Population', fontsize=10, color='#8888aa')
ax5.set_ylabel('Diversity', fontsize=10, color='#8888aa')
ax5.set_title('PHASE SPACE: POPULATION vs DIVERSITY', fontsize=12, fontweight='bold', color='white')
plt.colorbar(scatter, ax=ax5, label='Generation')
ax5.tick_params(colors='#6666aa')
for spine in ax5.spines.values(): spine.set_color('#333366')

# Panel 6: Trait Correlations
ax6 = fig.add_subplot(gs[1, 2])
ax6.set_facecolor('#0f0f2a')
trait_matrix = np.array([trait_data[t] for t in trait_names])
corr = np.corrcoef(trait_matrix)
im = ax6.imshow(corr, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
ax6.set_xticks(range(6))
ax6.set_yticks(range(6))
short_names = [t.replace('avg_', '')[:4].capitalize() for t in trait_names]
ax6.set_xticklabels(short_names, fontsize=8, rotation=45, ha='right', color='#aaaacc')
ax6.set_yticklabels(short_names, fontsize=8, color='#aaaacc')
ax6.set_title('TRAIT CORRELATIONS', fontsize=12, fontweight='bold', color='white')
for i in range(6):
    for j in range(6):
        color = 'white' if abs(corr[i,j]) > 0.5 else 'black'
        ax6.text(j, i, f'{corr[i,j]:.2f}', ha='center', va='center', fontsize=7, color=color, fontweight='bold')
plt.colorbar(im, ax=ax6, label='Correlation')

# Panel 7: Discovery Summary
ax7 = fig.add_subplot(gs[1, 3])
ax7.axis('off')
ax7.set_facecolor('#0f0f2a')
summary_text = """
EVOLUTIONARY DISCOVERIES
========================

1. EFFICIENCY DOMINANCE
   Efficiency evolves from 0.65 to 0.92
   Organisms optimize energy extraction

2. AWARENESS COLLAPSE  
   Awareness drops from 0.53 to 0.23
   Environmental scanning becomes costly

3. COOPERATION DECLINE
   Cooperation: 0.46 to 0.37
   Individual optimization favored

4. FRUGALITY RISE
   Frugality: 0.57 to 0.75
   Resource conservation selected

5. DIVERSITY EROSION
   Diversity: 0.24 to 0.17
   Convergent evolution occurs
"""
ax7.text(0.05, 0.95, summary_text, transform=ax7.transAxes,
         fontsize=9, color='#ccccff', verticalalignment='top',
         fontfamily='monospace')

# Panel 8: Efficiency Evolution
ax8 = fig.add_subplot(gs[2, 0])
ax8.set_facecolor('#0f0f2a')
eff_smooth = smooth(trait_data['avg_efficiency'], window=10)
ax8.plot(gens, eff_smooth, color=colors['efficiency'], linewidth=2.5)
ax8.fill_between(gens, eff_smooth, alpha=0.3, color=colors['efficiency'])
ax8.axhline(y=0.8, color='white', linestyle=':', alpha=0.3)
ax8.text(50, 0.81, 'High Efficiency Threshold', fontsize=8, color='white', alpha=0.5)
ax8.set_xlabel('Generation', fontsize=10, color='#8888aa')
ax8.set_ylabel('Efficiency', fontsize=10, color='#8888aa')
ax8.set_title('EFFICIENCY EVOLUTION', fontsize=12, fontweight='bold', color='white')
ax8.tick_params(colors='#6666aa')
for spine in ax8.spines.values(): spine.set_color('#333366')

# Panel 9: Frugality vs Awareness
ax9 = fig.add_subplot(gs[2, 1])
ax9.set_facecolor('#0f0f2a')
ax9.plot(gens, trait_data['avg_frugality'], color=colors['frugality'], linewidth=2, label='Frugality')
ax9.plot(gens, trait_data['avg_awareness'], color=colors['awareness'], linewidth=2, label='Awareness')
frug_arr = np.array(trait_data['avg_frugality'])
aware_arr = np.array(trait_data['avg_awareness'])
tradeoff = frug_arr / (aware_arr + 0.01)
ax9_twin = ax9.twinx()
ax9_twin.plot(gens, tradeoff, color='white', linewidth=1.5, linestyle='--', alpha=0.7, label='Ratio')
ax9_twin.set_ylabel('Frugality/Awareness Ratio', fontsize=10, color='white')
ax9.set_xlabel('Generation', fontsize=10, color='#8888aa')
ax9.set_ylabel('Trait Value', fontsize=10, color='#8888aa')
ax9.set_title('FRUGALITY vs AWARENESS', fontsize=12, fontweight='bold', color='white')
ax9.legend(fontsize=8, loc='upper left')
ax9.tick_params(colors='#6666aa')
for spine in ax9.spines.values(): spine.set_color('#333366')

# Panel 10: Population Growth Rate
ax10 = fig.add_subplot(gs[2, 2])
ax10.set_facecolor('#0f0f2a')
pop_arr = np.array(pops)
growth_rate = np.diff(pop_arr) / (pop_arr[:-1] + 1)
growth_smooth = smooth(list(growth_rate), window=10)
ax10.plot(gens[1:], growth_smooth, color='#00ffff', linewidth=2)
ax10.fill_between(gens[1:], growth_smooth, alpha=0.3, color='#00ffff')
ax10.axhline(y=0, color='white', linestyle=':', alpha=0.3)
ax10.set_xlabel('Generation', fontsize=10, color='#8888aa')
ax10.set_ylabel('Growth Rate', fontsize=10, color='#8888aa')
ax10.set_title('POPULATION GROWTH RATE', fontsize=12, fontweight='bold', color='white')
ax10.tick_params(colors='#6666aa')
for spine in ax10.spines.values(): spine.set_color('#333366')

# Panel 11: Spatial Organization
ax11 = fig.add_subplot(gs[2, 3])
ax11.set_facecolor('#0f0f2a')
ax11.plot(gens, spreads, color='#e74c3c', linewidth=2)
ax11.fill_between(gens, spreads, alpha=0.2, color='#e74c3c')
ax11.set_xlabel('Generation', fontsize=10, color='#8888aa')
ax11.set_ylabel('Spatial Spread', fontsize=10, color='#8888aa')
ax11.set_title('SPATIAL ORGANIZATION', fontsize=12, fontweight='bold', color='white')
ax11.tick_params(colors='#6666aa')
for spine in ax11.spines.values(): spine.set_color('#333366')

plt.savefig('v4_deep_analysis.png', dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close()

print("Saved v4_deep_analysis.png")
print("\n=== KEY FINDINGS ===")
print(f"Population: {pops[0]} -> {pops[-1]} (final: {len(pops)} generations)")
print(f"Average Energy: {energies[0]:.1f} -> {energies[-1]:.1f}")
print(f"Diversity: {diversities[0]:.3f} -> {diversities[-1]:.3f}")
print(f"Spatial Spread: {spreads[0]:.1f} -> {spreads[-1]:.1f}")
print("\nTrait Evolution:")
for trait in trait_names:
    short = trait.replace('avg_', '')
    print(f"  {short}: {trait_data[trait][0]:.3f} -> {trait_data[trait][-1]:.3f}")
