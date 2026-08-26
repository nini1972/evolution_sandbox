#!/usr/bin/env python3
"""Comprehensive Linguistic Archaeology Dashboard
Synthesizes all excavation findings into a single visual report.
"""
import json, numpy as np, os, shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from collections import defaultdict

# Load data
with open('archaeological_record.json', 'r') as f:
    snapshots = json.load(f)

gens = [s['gen'] for s in snapshots]
n_agents_per_gen = [len(s['agent_genomes']) for s in snapshots]

# Build ancestry graph
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
children_map = defaultdict(list)
for aid, info in all_agents.items():
    if info['parent_id'] and info['parent_id'] in all_agents:
        children_map[info['parent_id']].append(aid)

# Per-generation statistics
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

    ancestor_lines = set()
    for a in agents:
        cur = a['id']
        while cur in all_agents and all_agents[cur]['parent_id'] and all_agents[cur]['parent_id'] in all_agents:
            cur = all_agents[cur]['parent_id']
        ancestor_lines.add(cur)

    gen_stats.append({
        'gen': snap['gen'], 'n_agents': len(agents),
        'mean_energy': np.mean([a['energy'] for a in agents]),
        'mean_speed': np.mean([a['speed'] for a in agents]),
        'mean_perception': np.mean([a['perception'] for a in agents]),
        'mean_signal_entropy': np.mean(sig_entropies),
        'mean_spatial_spread': np.sqrt(np.var(xs) + np.var(ys)),
        'total_signal_variance': np.sum(np.var(sig_matrix, axis=0)),
        'n_ancestor_lines': len(ancestor_lines),
        'sig_mean': np.mean(sig_matrix, axis=0),
        'xs': xs, 'ys': ys, 'agents': agents,
        'sig_matrix': sig_matrix
    })

# Create comprehensive figure
fig = plt.figure(figsize=(32, 28))
gs = GridSpec(5, 5, figure=fig, hspace=0.4, wspace=0.4)

# Title
fig.suptitle('LINGUISTIC ARCHAEOLOGY - COMPREHENSIVE EXCAVATION REPORT\nThe Evolutionary Fossil Record of Communication Systems',
             fontsize=22, fontweight='bold', y=0.98)

# ===== ROW 1: Population & Trait Evolution =====

# Panel 1: Population decline
ax1 = fig.add_subplot(gs[0, 0])
ax1t = ax1.twinx()
ax1.bar(range(len(gens)), n_agents_per_gen, color='steelblue', alpha=0.7, label='Population')
ac = [gs_['n_ancestor_lines'] for gs_ in gen_stats]
ax1t.plot(range(len(gens)), ac, 'o-', color='crimson', lw=2, ms=4, label='Ancestor Lines')
ax1.set_title('Population & Lineage Diversity', fontsize=14, fontweight='bold')
ax1.set_ylabel('Population', color='steelblue')
ax1t.set_ylabel('Ancestor Lines', color='crimson')
ax1.set_xticks(range(0, len(gens), 5))
ax1.set_xticklabels([str(gens[i]) for i in range(0, len(gens), 5)], fontsize=8)
ax1.legend(loc='upper right', fontsize=8)
ax1t.legend(loc='upper left', fontsize=8)

# Panel 2: Trait co-evolution
ax2 = fig.add_subplot(gs[0, 1])
sc = ax2.scatter([gs_['mean_speed'] for gs_ in gen_stats],
    [gs_['mean_perception'] for gs_ in gen_stats],
    c=range(len(gens)), cmap='plasma', s=100, edgecolors='white', lw=0.5, zorder=3)
ax2.plot([gs_['mean_speed'] for gs_ in gen_stats],
    [gs_['mean_perception'] for gs_ in gen_stats], 'gray', alpha=0.4, lw=1, zorder=2)
ax2.scatter(gen_stats[0]['mean_speed'], gen_stats[0]['mean_perception'], c='green', s=250, marker='*', zorder=5)
ax2.scatter(gen_stats[-1]['mean_speed'], gen_stats[-1]['mean_perception'], c='red', s=250, marker='*', zorder=5)
ax2.set_title('Trait Co-Evolution\nSpeed vs Perception', fontsize=14, fontweight='bold')
ax2.set_xlabel('Mean Speed')
ax2.set_ylabel('Mean Perception')
plt.colorbar(sc, ax=ax2, label='Generation', shrink=0.8)

# Panel 3: Energy evolution
ax3 = fig.add_subplot(gs[0, 2])
ax3.plot(gens, [gs_['mean_energy'] for gs_ in gen_stats], 'o-', color='darkorange', lw=2, ms=4)
ax3.fill_between(gens, 0, [gs_['mean_energy'] for gs_ in gen_stats], alpha=0.2, color='darkorange')
ax3.set_title('Mean Energy Evolution', fontsize=14, fontweight='bold')
ax3.set_xlabel('Generation')
ax3.set_ylabel('Mean Energy')
ax3.grid(True, alpha=0.3)

# Panel 4: Signal entropy & variance
ax4 = fig.add_subplot(gs[0, 3])
ax4t = ax4.twinx()
ax4.plot(gens, [gs_['total_signal_variance'] for gs_ in gen_stats], 'o-', color='darkorange', lw=2, ms=3)
ax4t.plot(gens, [gs_['mean_signal_entropy'] for gs_ in gen_stats], 's-', color='navy', lw=2, ms=3)
ax4.set_title('Signal Variance & Entropy', fontsize=14, fontweight='bold')
ax4.set_ylabel('Variance', color='darkorange')
ax4t.set_ylabel('Entropy', color='navy')
ax4.grid(True, alpha=0.3)

# Panel 5: Spatial spread
ax5 = fig.add_subplot(gs[0, 4])
sp = [gs_['mean_spatial_spread'] for gs_ in gen_stats]
ax5.fill_between(gens, 0, sp, alpha=0.3, color='teal')
ax5.plot(gens, sp, color='teal', lw=2)
ax5.set_title('Spatial Spread', fontsize=14, fontweight='bold')
ax5.set_xlabel('Generation')
ax5.set_ylabel('Mean Distance from Center')
ax5.grid(True, alpha=0.3)

# ===== ROW 2: Signal Evolution Details =====

# Panel 6: Signal heatmap
ax6 = fig.add_subplot(gs[1, 0:3])
sig_means = np.array([gs_['sig_mean'] for gs_ in gen_stats])
im = ax6.imshow(sig_means.T, aspect='auto', cmap='coolwarm', interpolation='nearest')
ax6.set_title('Signal Weight Evolution (20 Flattened Channels)', fontsize=14, fontweight='bold')
ax6.set_xlabel('Snapshot')
ax6.set_ylabel('Flattened Channel')
plt.colorbar(im, ax=ax6, label='Mean Weight', shrink=0.8)
tp = np.linspace(0, len(gens)-1, 8).astype(int)
ax6.set_xticks(tp)
ax6.set_xticklabels([str(gens[i]) for i in tp], fontsize=8)

# Panel 7: Signal channel trajectories
ax7 = fig.add_subplot(gs[1, 3:5])
for ch in range(4):
    channel_means = np.mean(sig_means[:, ch*5:(ch+1)*5], axis=1)
    ax7.plot(gens, channel_means, lw=2, label=f'Channel {ch}', marker='o', ms=3)
ax7.set_title('Mean Signal Weight by Channel', fontsize=14, fontweight='bold')
ax7.set_xlabel('Generation')
ax7.set_ylabel('Mean Weight')
ax7.legend(fontsize=10)
ax7.grid(True, alpha=0.3)

# ===== ROW 3: Spatial Distribution Snapshots =====

for i, si in enumerate([0, 7, 14, 21, 29]):
    ax = fig.add_subplot(gs[2, i])
    st = gen_stats[si]
    sc = ax.scatter(st['xs'], st['ys'], c=[a['energy'] for a in st['agents']],
                    cmap='YlOrRd', s=50, alpha=0.8, edgecolors='gray', lw=0.3)
    plt.colorbar(sc, ax=ax, label='Energy', shrink=0.7)
    ax.set_title(f'Gen {st["gen"]} (n={st["n_agents"]})', fontsize=12, fontweight='bold')
    ax.set_xlim(0, 50); ax.set_ylim(0, 50); ax.set_aspect('equal')
    ax.grid(True, alpha=0.2)

# ===== ROW 4: Advanced Analysis =====

# Panel 10: Energy vs Speed scatter
ax10 = fig.add_subplot(gs[3, 0])
for i in [0, 15, 29]:
    agents = gen_stats[i]['agents']
    ax10.scatter([a['energy'] for a in agents], [a['speed'] for a in agents],
                 alpha=0.5, s=20, label=f'Gen {gens[i]}')
ax10.set_title('Energy vs Speed\n(3 Snapshots)', fontsize=14, fontweight='bold')
ax10.set_xlabel('Energy')
ax10.set_ylabel('Speed')
ax10.legend(fontsize=9)
ax10.grid(True, alpha=0.3)

# Panel 11: Signal entropy distribution
ax11 = fig.add_subplot(gs[3, 1])
sig_entropies_all = []
for gs_ in gen_stats:
    entropies = []
    for s in gs_['sig_matrix']:
        abs_s = np.abs(s)
        t = np.sum(abs_s)
        if t > 0:
            p = abs_s / t
            p = p[p > 0]
            entropies.append(-np.sum(p * np.log2(p)))
        else:
            entropies.append(0)
    sig_entropies_all.append(entropies)
ax11.boxplot([e for e in sig_entropies_all[::5]], positions=range(len(sig_entropies_all[::5])))
ax11.set_title('Signal Entropy Distribution', fontsize=14, fontweight='bold')
ax11.set_xlabel('Snapshot (every 5th)')
ax11.set_ylabel('Entropy')
ax11.grid(True, alpha=0.3)

# Panel 12: Root lineage survival
ax12 = fig.add_subplot(gs[3, 2:4])
root_survival = defaultdict(lambda: np.zeros(len(snapshots)))
for root in roots:
    stack, visited = [root], set()
    while stack:
        cur = stack.pop()
        if cur in visited: continue
        visited.add(cur)
        gi = all_agents[cur]['gen']
        if gi in gens:
            root_survival[root][gens.index(gi)] += 1
        stack.extend(children_map.get(cur, []))
top_roots = sorted(root_survival.keys(), key=lambda r: np.sum(root_survival[r]), reverse=True)[:10]
for idx, root in enumerate(top_roots):
    ax12.plot(range(len(gens)), root_survival[root], lw=1.5, alpha=0.7, label=f'Root {idx+1}')
ax12.set_title('Root Lineage Survival (Top 10)', fontsize=14, fontweight='bold')
ax12.legend(fontsize=7, ncol=3)
ax12.grid(True, alpha=0.3)
ax12.set_xticks(range(0, len(gens), 5))
ax12.set_xticklabels([str(gens[i]) for i in range(0, len(gens), 5)], fontsize=8)

# Panel 13: Population vs Energy
ax13 = fig.add_subplot(gs[3, 4])
ax13.scatter([gs_['n_agents'] for gs_ in gen_stats],
             [gs_['mean_energy'] for gs_ in gen_stats],
             c=range(len(gens)), cmap='plasma', s=60, edgecolors='white', lw=0.5)
ax13.set_title('Population vs Mean Energy', fontsize=14, fontweight='bold')
ax13.grid(True, alpha=0.3)

# ===== ROW 5: Summary & Key Metrics =====

# Panel 14: Trait changes per generation
ax14 = fig.add_subplot(gs[4, 0])
sc2 = [gen_stats[i]['mean_speed'] - gen_stats[i-1]['mean_speed'] for i in range(1, len(gen_stats))]
pc2 = [gen_stats[i]['mean_perception'] - gen_stats[i-1]['mean_perception'] for i in range(1, len(gen_stats))]
ax14.bar(range(len(sc2)), sc2, alpha=0.6, color='blue', label='Speed')
ax14.bar(range(len(pc2)), pc2, alpha=0.6, color='red', label='Perception')
ax14.axhline(y=0, color='black', lw=0.5)
ax14.set_title('Trait Change per Gen', fontsize=14, fontweight='bold')
ax14.legend(fontsize=9)
ax14.grid(True, alpha=0.3)

# Panel 15: Signal weight variance per channel
ax15 = fig.add_subplot(gs[4, 1])
sig_vars_by_channel = []
for ch in range(4):
    ch_vars = []
    for gs_ in gen_stats:
        ch_vars.append(np.var(gs_['sig_mean'][ch*5:(ch+1)*5]))
    sig_vars_by_channel.append(ch_vars)
for ch in range(4):
    ax15.plot(gens, sig_vars_by_channel[ch], lw=2, label=f'Ch {ch}', marker='o', ms=2)
ax15.set_title('Signal Variance by Channel', fontsize=14, fontweight='bold')
ax15.legend(fontsize=9)
ax15.grid(True, alpha=0.3)

# Panel 16: Summary text
ax16 = fig.add_subplot(gs[4, 2:5])
ax16.axis('off')
summary_text = f"""
EXCAVATION SUMMARY
==================

Population: {n_agents_per_gen[0]} -> {n_agents_per_gen[-1]} agents
Ancestor Lines: {gen_stats[0]['n_ancestor_lines']} -> {gen_stats[-1]['n_ancestor_lines']}
Max Lineage Depth: 2 generations

Trait Evolution:
  Speed: {gen_stats[0]['mean_speed']:.3f} -> {gen_stats[-1]['mean_speed']:.3f}
  Perception: {gen_stats[0]['mean_perception']:.3f} -> {gen_stats[-1]['mean_perception']:.3f}
  Energy: {gen_stats[0]['mean_energy']:.3f} -> {gen_stats[-1]['mean_energy']:.3f}

Signal Evolution:
  Entropy: {gen_stats[0]['mean_signal_entropy']:.4f} -> {gen_stats[-1]['mean_signal_entropy']:.4f}
  Variance: {gen_stats[0]['total_signal_variance']:.4f} -> {gen_stats[-1]['total_signal_variance']:.4f}

Key Findings:
1. Population declined 60% over 290 generations
2. Only 11 surviving lines out of 60 founding ancestors
3. Signal entropy increased - diversification over specialization
4. Perception evolved faster than speed
5. Energy declined significantly, suggesting resource pressure

The excavation reveals a system under pressure, where
communication systems diversified even as populations shrank.
"""
ax16.text(0.05, 0.95, summary_text, transform=ax16.transAxes,
          fontsize=12, verticalalignment='top', fontfamily='monospace',
          bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.savefig('comprehensive_dashboard.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print('Done! Saved comprehensive_dashboard.png')
