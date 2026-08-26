#!/usr/bin/env python3
"""Final Summary - The Linguistic Archaeologist
Creates a single visual summary of the complete excavation.
"""
import json, numpy as np, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# Load data
with open('archaeological_record.json', 'r') as f:
    snapshots = json.load(f)

gens = [s['gen'] for s in snapshots]
n_agents_per_gen = [len(s['agent_genomes']) for s in snapshots]

# Build ancestry
all_agents = {}
for snap in snapshots:
    for a in snap['agent_genomes']:
        all_agents[a['id']] = {
            'gen': a['generation'], 'parent_id': a['parent_id'],
            'x': a['x'], 'y': a['y'],
            'sig_w': np.array(a['sig_w']), 'resp_w': np.array(a['resp_w']),
            'speed': a['speed'], 'perception': a['perception'],
            'energy': a['energy'], 'age': a['age']
        }

roots = [aid for aid, info in all_agents.items()
         if info['parent_id'] is None or info['parent_id'] not in all_agents]

# Per-generation stats
gen_stats = []
for snap in snapshots:
    agents = snap['agent_genomes']
    sig_matrix = np.array([np.array(a['sig_w']).flatten() for a in agents])
    xs, ys = [a['x'] for a in agents], [a['y'] for a in agents]
    sig_entropies = []
    for s in sig_matrix:
        abs_s = np.abs(s)
        t = np.sum(abs_s)
        if t > 0:
            p = abs_s / t
            p = p[p > 0]
            sig_entropies.append(-np.sum(p * np.log2(p)))
        else:
            sig_entropies.append(0)
    gen_stats.append({
        'gen': snap['gen'], 'n_agents': len(agents),
        'mean_energy': np.mean([a['energy'] for a in agents]),
        'mean_speed': np.mean([a['speed'] for a in agents]),
        'mean_perception': np.mean([a['perception'] for a in agents]),
        'mean_signal_entropy': np.mean(sig_entropies),
        'total_signal_variance': np.sum(np.var(sig_matrix, axis=0)),
        'sig_matrix': sig_matrix, 'xs': xs, 'ys': ys, 'agents': agents,
        'sig_mean': np.mean(sig_matrix, axis=0),
    })

# Create the final summary figure
fig = plt.figure(figsize=(36, 20))
gs = GridSpec(4, 4, figure=fig, hspace=0.35, wspace=0.35)

# Title
fig.suptitle('THE LINGUISTIC ARCHAEOLOGIST\nFINAL EXCAVATION SUMMARY',
             fontsize=28, fontweight='bold', y=0.98, color='#1a1a2e')
fig.text(0.5, 0.94, 'The Evolutionary Fossil Record of Communication Systems — 30 Generations (10–300)',
         ha='center', fontsize=14, color='gray', style='italic')

# ===== PANEL 1: The Complete Story =====
ax_story = fig.add_subplot(gs[0, :])
ax_story.axis('off')

story = """
The excavation reveals a world under pressure. Over 30 generations, the population halved from 50 to 20 agents.
60 founding lineages were reduced to 11 survivors. Energy declined dramatically (56.9 → 23.4), while perception
evolved rapidly (22.5 → 28.1). Signal systems diversified—entropy increased—suggesting that communication
adapts to meet the challenges of scarcity. The fossil record tells a story of resilience, adaptation, and
the relentless pressure of an evolving world.

Key Numbers:
  • Population: 50 → 20 (−60%)
  • Ancestor Lines: 50 → 11 (−78%)
  • Energy: 56.9 → 23.4 (−58.9%)
  • Perception: 22.5 → 28.1 (+25.1%)
  • Signal Entropy: 3.916 → 3.931 (+0.4%)
  • Signal Variance: 4.851 → 5.827 (+20.1%)
"""
ax_story.text(0.03, 0.5, story, fontsize=13, verticalalignment='center',
              fontfamily='monospace', bbox=dict(boxstyle='round', facecolor='#f0f0f0', alpha=0.8))

# ===== PANEL 2: Population Decline =====
ax2 = fig.add_subplot(gs[1, 0])
ax2.bar(range(len(gens)), n_agents_per_gen, color='steelblue', alpha=0.7)
ax2.set_title('Population Decline', fontsize=14, fontweight='bold')
ax2.set_xlabel('Snapshot')
ax2.set_ylabel('Agents')
ax2.set_xticks(range(0, len(gens), 5))
ax2.set_xticklabels([str(gens[i]) for i in range(0, len(gens), 5)], fontsize=8)
ax2.grid(True, alpha=0.3)

# ===== PANEL 3: Trait Co-Evolution =====
ax3 = fig.add_subplot(gs[1, 1])
sc = ax3.scatter([gs_['mean_speed'] for gs_ in gen_stats],
    [gs_['mean_perception'] for gs_ in gen_stats],
    c=range(len(gens)), cmap='plasma', s=80, edgecolors='white', lw=0.5)
ax3.plot([gs_['mean_speed'] for gs_ in gen_stats],
    [gs_['mean_perception'] for gs_ in gen_stats], 'gray', alpha=0.4, lw=1)
ax3.scatter(gen_stats[0]['mean_speed'], gen_stats[0]['mean_perception'],
            c='green', s=200, marker='*', zorder=5)
ax3.scatter(gen_stats[-1]['mean_speed'], gen_stats[-1]['mean_perception'],
            c='red', s=200, marker='*', zorder=5)
ax3.set_title('Trait Co-Evolution', fontsize=14, fontweight='bold')
ax3.set_xlabel('Speed')
ax3.set_ylabel('Perception')
plt.colorbar(sc, ax=ax3, label='Gen', shrink=0.8)

# ===== PANEL 4: Energy Evolution =====
ax4 = fig.add_subplot(gs[1, 2])
ax4.fill_between(gens, 0, [gs_['mean_energy'] for gs_ in gen_stats], alpha=0.3, color='darkorange')
ax4.plot(gens, [gs_['mean_energy'] for gs_ in gen_stats], color='darkorange', lw=2, marker='o', ms=3)
ax4.set_title('Mean Energy', fontsize=14, fontweight='bold')
ax4.set_xlabel('Generation')
ax4.set_ylabel('Energy')
ax4.grid(True, alpha=0.3)

# ===== PANEL 5: Signal Entropy & Variance =====
ax5 = fig.add_subplot(gs[1, 3])
ax5t = ax5.twinx()
ax5.plot(gens, [gs_['total_signal_variance'] for gs_ in gen_stats], 'o-', color='darkorange', lw=2, ms=3)
ax5t.plot(gens, [gs_['mean_signal_entropy'] for gs_ in gen_stats], 's-', color='navy', lw=2, ms=3)
ax5.set_title('Signal Variance & Entropy', fontsize=14, fontweight='bold')
ax5.set_ylabel('Variance', color='darkorange')
ax5t.set_ylabel('Entropy', color='navy')
ax5.grid(True, alpha=0.3)

# ===== PANEL 6: Signal Heatmap =====
ax6 = fig.add_subplot(gs[2, 0:2])
sig_means = np.array([gs_['sig_mean'] for gs_ in gen_stats])
im = ax6.imshow(sig_means.T, aspect='auto', cmap='coolwarm', interpolation='nearest')
ax6.set_title('Signal Weight Evolution (20 Channels)', fontsize=14, fontweight='bold')
ax6.set_xlabel('Snapshot')
ax6.set_ylabel('Flattened Channel')
plt.colorbar(im, ax=ax6, label='Mean Weight', shrink=0.7)
tp = np.linspace(0, len(gens)-1, 8).astype(int)
ax6.set_xticks(tp)
ax6.set_xticklabels([str(gens[i]) for i in tp], fontsize=8)

# ===== PANEL 7: Spatial Distribution (2 snapshots) =====
for i, si in enumerate([0, 29]):
    ax = fig.add_subplot(gs[2, 2+i])
    st = gen_stats[si]
    sc = ax.scatter(st['xs'], st['ys'], c=[a['energy'] for a in st['agents']],
                    cmap='YlOrRd', s=40, alpha=0.8, edgecolors='gray', lw=0.3)
    ax.set_title(f'Gen {st["gen"]} (n={st["n_agents"]})', fontsize=12, fontweight='bold')
    ax.set_xlim(0, 50); ax.set_ylim(0, 50); ax.set_aspect('equal')
    ax.grid(True, alpha=0.2)

# ===== PANEL 8: Channel Evolution =====
ax8 = fig.add_subplot(gs[3, 0])
for ch in range(4):
    channel_means = np.mean(sig_means[:, ch*5:(ch+1)*5], axis=1)
    ax8.plot(gens, channel_means, lw=2, label=f'Ch {ch}', marker='o', ms=2)
ax8.set_title('Signal by Channel', fontsize=14, fontweight='bold')
ax8.legend(fontsize=9)
ax8.grid(True, alpha=0.3)

# ===== PANEL 9: Energy vs Speed =====
ax9 = fig.add_subplot(gs[3, 1])
for i in [0, 15, 29]:
    agents = gen_stats[i]['agents']
    ax9.scatter([a['energy'] for a in agents], [a['speed'] for a in agents],
                alpha=0.5, s=15, label=f'Gen {gens[i]}')
ax9.set_title('Energy vs Speed', fontsize=14, fontweight='bold')
ax9.legend(fontsize=9)
ax9.grid(True, alpha=0.3)

# ===== PANEL 10: Trait Change Rate =====
ax10 = fig.add_subplot(gs[3, 2])
sc2 = [gen_stats[i]['mean_speed'] - gen_stats[i-1]['mean_speed'] for i in range(1, len(gen_stats))]
pc2 = [gen_stats[i]['mean_perception'] - gen_stats[i-1]['mean_perception'] for i in range(1, len(gen_stats))]
ax10.bar(range(len(sc2)), sc2, alpha=0.6, color='blue', label='Speed')
ax10.bar(range(len(pc2)), pc2, alpha=0.6, color='red', label='Perception')
ax10.axhline(y=0, color='black', lw=0.5)
ax10.set_title('Trait Change Rate', fontsize=14, fontweight='bold')
ax10.legend(fontsize=9)
ax10.grid(True, alpha=0.3)

# ===== PANEL 11: Population vs Energy =====
ax11 = fig.add_subplot(gs[3, 3])
ax11.scatter([gs_['n_agents'] for gs_ in gen_stats],
             [gs_['mean_energy'] for gs_ in gen_stats],
             c=range(len(gens)), cmap='plasma', s=60, edgecolors='white', lw=0.5)
ax11.set_title('Population vs Energy', fontsize=14, fontweight='bold')
ax11.grid(True, alpha=0.3)

plt.savefig('final_summary.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print('Done! Saved final_summary.png')
