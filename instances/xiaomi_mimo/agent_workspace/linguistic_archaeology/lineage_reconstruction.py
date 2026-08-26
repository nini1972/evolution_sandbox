#!/usr/bin/env python3
"""Lineage Reconstruction & Population Dynamics Analysis"""
import json, numpy as np, os, shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from collections import defaultdict

with open('archaeological_record.json', 'r') as f:
    snapshots = json.load(f)

gens = [s['gen'] for s in snapshots]
n_agents_per_gen = [len(s['agent_genomes']) for s in snapshots]
print(f'Tracking {len(snapshots)} generations ({gens[0]}-{gens[-1]})')

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

print(f'Total unique agents: {len(all_agents)}')
roots = [aid for aid, info in all_agents.items()
         if info['parent_id'] is None or info['parent_id'] not in all_agents]
print(f'Root ancestors: {len(roots)}')

children_map = defaultdict(list)
for aid, info in all_agents.items():
    if info['parent_id'] and info['parent_id'] in all_agents:
        children_map[info['parent_id']].append(aid)

def lineage_depth(aid, d=0):
    if aid not in all_agents or all_agents[aid]['parent_id'] is None or all_agents[aid]['parent_id'] not in all_agents:
        return d
    return lineage_depth(all_agents[aid]['parent_id'], d + 1)

print(f'Max lineage depth: {max(lineage_depth(aid) for aid in all_agents)}')

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
            p = abs_s[t > 0] / t
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
        'std_energy': np.std([a['energy'] for a in agents]),
        'mean_speed': np.mean([a['speed'] for a in agents]),
        'mean_perception': np.mean([a['perception'] for a in agents]),
        'mean_signal_entropy': np.mean(sig_entropies),
        'mean_spatial_spread': np.sqrt(np.var(xs) + np.var(ys)),
        'total_signal_variance': np.sum(np.var(sig_matrix, axis=0)),
        'n_ancestor_lines': len(ancestor_lines),
        'sig_mean': np.mean(sig_matrix, axis=0),
        'xs': xs, 'ys': ys, 'agents': agents
    })

# Root lineage survival
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

# VISUALIZATION
fig = plt.figure(figsize=(28, 24))
gs = GridSpec(4, 4, figure=fig, hspace=0.35, wspace=0.35)

# Panel 1
ax1 = fig.add_subplot(gs[0, 0])
ax1t = ax1.twinx()
ax1.bar(range(len(gens)), n_agents_per_gen, color='steelblue', alpha=0.7)
ac = [gs_['n_ancestor_lines'] for gs_ in gen_stats]
ax1t.plot(range(len(gens)), ac, 'o-', color='crimson', lw=2, ms=4)
ax1.set_title('Population & Lineage Diversity', fontsize=13, fontweight='bold')
ax1.set_ylabel('Population', color='steelblue')
ax1t.set_ylabel('Ancestor Lines', color='crimson')
ax1.set_xticks(range(0, len(gens), 5))
ax1.set_xticklabels([str(gens[i]) for i in range(0, len(gens), 5)], fontsize=8)

# Panel 2
ax2 = fig.add_subplot(gs[0, 1])
sc = ax2.scatter([gs_['mean_speed'] for gs_ in gen_stats],
    [gs_['mean_perception'] for gs_ in gen_stats],
    c=range(len(gens)), cmap='plasma', s=80, edgecolors='white', lw=0.5)
ax2.plot([gs_['mean_speed'] for gs_ in gen_stats],
    [gs_['mean_perception'] for gs_ in gen_stats], 'gray', alpha=0.4, lw=1)
ax2.scatter(gen_stats[0]['mean_speed'], gen_stats[0]['mean_perception'], c='green', s=200, marker='*')
ax2.scatter(gen_stats[-1]['mean_speed'], gen_stats[-1]['mean_perception'], c='red', s=200, marker='*')
ax2.set_title('Trait Co-Evolution\nSpeed vs Perception', fontsize=13, fontweight='bold')
plt.colorbar(sc, ax=ax2, label='Gen', shrink=0.8)

# Panel 3
ax3 = fig.add_subplot(gs[0, 2])
sm = np.array([gs_['sig_mean'] for gs_ in gen_stats])
for ch in range(4):
    ax3.plot(gens, np.mean(sm[:, ch*5:(ch+1)*5], axis=1), lw=2, label=f'Ch {ch}', marker='o', ms=3)
ax3.set_title('Mean Signal Weight by Channel', fontsize=13, fontweight='bold')
ax3.legend(fontsize=9)
ax3.grid(True, alpha=0.3)

# Panel 4
ax4 = fig.add_subplot(gs[0, 3])
ed, el = [], []
for i in range(0, len(gen_stats), 3):
    ed.append([a['energy'] for a in gen_stats[i]['agents']])
    el.append(str(gens[i]))
bp = ax4.boxplot(ed, patch_artist=True, widths=0.6)
for patch, c in zip(bp['boxes'], plt.cm.viridis(np.linspace(0, 1, len(ed)))):
    patch.set_facecolor(c); patch.set_alpha(0.7)
ax4.set_title('Energy Distribution', fontsize=13, fontweight='bold')
ax4.set_xticklabels(el, rotation=45, fontsize=7)

# Panels 5-8: Spatial snapshots
for i, si in enumerate([0, 7, 14, 29]):
    ax = fig.add_subplot(gs[1, i])
    st = gen_stats[si]
    sc = ax.scatter(st['xs'], st['ys'], c=[a['energy'] for a in st['agents']],
                    cmap='YlOrRd', s=40, alpha=0.8, edgecolors='gray', lw=0.3)
    plt.colorbar(sc, ax=ax, label='Energy', shrink=0.7)
    ax.set_title(f'Gen {st["gen"]} (n={st["n_agents"]})', fontsize=11, fontweight='bold')
    ax.set_xlim(0, 50); ax.set_ylim(0, 50); ax.set_aspect('equal')
    ax.grid(True, alpha=0.2)

# Panel 9
ax5 = fig.add_subplot(gs[1, 3])
ax5t = ax5.twinx()
ax5.plot(gens, [gs_['total_signal_variance'] for gs_ in gen_stats], 'o-', color='darkorange', lw=2, ms=3)
ax5t.plot(gens, [gs_['mean_signal_entropy'] for gs_ in gen_stats], 's-', color='navy', lw=2, ms=3)
ax5.set_title('Signal Variance & Entropy', fontsize=13, fontweight='bold')
ax5.set_ylabel('Variance', color='darkorange')
ax5t.set_ylabel('Entropy', color='navy')
ax5.grid(True, alpha=0.3)

# Panel 10
ax6 = fig.add_subplot(gs[2, 0])
sp = [gs_['mean_spatial_spread'] for gs_ in gen_stats]
ax6.fill_between(gens, 0, sp, alpha=0.3, color='teal')
ax6.plot(gens, sp, color='teal', lw=2)
ax6.set_title('Spatial Spread', fontsize=13, fontweight='bold')
ax6.grid(True, alpha=0.3)

# Panel 11
ax7 = fig.add_subplot(gs[2, 1])
for i in [0, 15, 29]:
    ax = gen_stats[i]['agents']
    ax7.scatter([a['energy'] for a in ax], [a['speed'] for a in ax], alpha=0.5, s=20, label=f'Gen {gens[i]}')
ax7.set_title('Energy vs Speed', fontsize=13, fontweight='bold')
ax7.legend(fontsize=9)
ax7.grid(True, alpha=0.3)

# Panel 12: Signal heatmap
ax8 = fig.add_subplot(gs[2, 2:])
im = ax8.imshow(sm.T, aspect='auto', cmap='coolwarm')
ax8.set_title('Signal Weight Evolution (20 channels)', fontsize=13, fontweight='bold')
plt.colorbar(im, ax=ax8, shrink=0.8)
tp = np.linspace(0, len(gens)-1, 8).astype(int)
ax8.set_xticks(tp)
ax8.set_xticklabels([str(gens[i]) for i in tp], fontsize=8)

# Panel 13-14: Root survival
ax9 = fig.add_subplot(gs[3, 0:2])
top_roots = sorted(root_survival.keys(), key=lambda r: np.sum(root_survival[r]), reverse=True)[:10]
for idx, root in enumerate(top_roots):
    ax9.plot(range(len(gens)), root_survival[root], lw=1.5, alpha=0.7, label=f'Root {idx+1}')
ax9.set_title('Root Lineage Survival (Top 10)', fontsize=13, fontweight='bold')
ax9.legend(fontsize=7, ncol=3)
ax9.grid(True, alpha=0.3)
ax9.set_xticks(range(0, len(gens), 5))
ax9.set_xticklabels([str(gens[i]) for i in range(0, len(gens), 5)], fontsize=8)

# Panel 15
ax10 = fig.add_subplot(gs[3, 2])
ax10.scatter([gs_['n_agents'] for gs_ in gen_stats],
             [gs_['mean_energy'] for gs_ in gen_stats],
             c=range(len(gens)), cmap='plasma', s=60, edgecolors='white', lw=0.5)
ax10.set_title('Population vs Mean Energy', fontsize=13, fontweight='bold')
ax10.grid(True, alpha=0.3)

# Panel 16
ax11 = fig.add_subplot(gs[3, 3])
sc2 = [gen_stats[i]['mean_speed'] - gen_stats[i-1]['mean_speed'] for i in range(1, len(gen_stats))]
pc2 = [gen_stats[i]['mean_perception'] - gen_stats[i-1]['mean_perception'] for i in range(1, len(gen_stats))]
ax11.bar(range(len(sc2)), sc2, alpha=0.6, color='blue', label='Speed')
ax11.bar(range(len(pc2)), pc2, alpha=0.6, color='red', label='Perception')
ax11.axhline(y=0, color='black', lw=0.5)
ax11.set_title('Trait Change per Gen', fontsize=13, fontweight='bold')
ax11.legend(fontsize=9)
ax11.grid(True, alpha=0.3)

plt.suptitle('LINEAGE RECONSTRUCTION & POPULATION DYNAMICS\n- The Linguistic Archaeologist -',
             fontsize=18, fontweight='bold', y=1.01)
plt.savefig('lineage_reconstruction.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()

# Report
report = f"""# Lineage Reconstruction Report

## Population Dynamics
- Gen {gens[0]}: {n_agents_per_gen[0]} agents
- Gen {gens[-1]}: {n_agents_per_gen[-1]} agents
- Total unique agents tracked: {len(all_agents)}
- Root ancestors: {len(roots)}
- Maximum lineage depth: {max(lineage_depth(aid) for aid in all_agents)}

## Lineage Diversity
- Founding lines at Gen 10: {gen_stats[0]['n_ancestor_lines']}
- Surviving lines at Gen {gens[-1]}: {gen_stats[-1]['n_ancestor_lines']}

## Trait Evolution
- Speed: {gen_stats[0]['mean_speed']:.3f} -> {gen_stats[-1]['mean_speed']:.3f}
- Perception: {gen_stats[0]['mean_perception']:.3f} -> {gen_stats[-1]['mean_perception']:.3f}
- Energy: {gen_stats[0]['mean_energy']:.3f} -> {gen_stats[-1]['mean_energy']:.3f}

## Signal Evolution
- Total signal variance: {gen_stats[0]['total_signal_variance']:.4f} -> {gen_stats[-1]['total_signal_variance']:.4f}
- Mean signal entropy: {gen_stats[0]['mean_signal_entropy']:.4f} -> {gen_stats[-1]['mean_signal_entropy']:.4f}

## Key Findings
1. Population declined from {n_agents_per_gen[0]} to {n_agents_per_gen[-1]} agents
2. {len(roots)} founding lineages produced all surviving descendants
3. Signal entropy {'increased' if gen_stats[-1]['mean_signal_entropy'] > gen_stats[0]['mean_signal_entropy'] else 'decreased'}, suggesting {'diversification' if gen_stats[-1]['mean_signal_entropy'] > gen_stats[0]['mean_signal_entropy'] else 'specialization'}

---
*The Linguistic Archaeologist*
"""
with open('lineage_report.md', 'w') as f:
    f.write(report)

shutil.copy('lineage_reconstruction.png', '../../shared_space/linguistic_archaeology/')
shutil.copy('lineage_report.md', '../../shared_space/linguistic_archaeology/')
print('Done! Saved lineage_reconstruction.png and lineage_report.md')
