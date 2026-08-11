import os, json, warnings
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
from scipy.spatial.distance import pdist, squareform
warnings.filterwarnings('ignore')

OUT = '/home/runner/work/evolution_sandbox/evolution_sandbox/instances/shared_space'
exec(open('/home/runner/work/evolution_sandbox/evolution_sandbox/instances/deepseek_v4_flash/agent_workspace/meta_phylogeny_part1.py').read().split('fig = plt.figure')[0])

# FIGURE 2: GENOME HEATMAP + LINEAGE REPORT
fig, axes = plt.subplots(1, 2, figsize=(20, 9), gridspec_kw={'width_ratios':[1.2,1]})
fig.patch.set_facecolor('#0a0a14')
ax = axes[0]
ax.set_facecolor('#0a0a14')
im = ax.imshow(G, cmap='viridis', aspect='auto', vmin=0, vmax=1)
ax.set_xticks(range(len(dims)))
ax.set_xticklabels(dims, color='white', rotation=45, ha='right', fontsize=10)
ax.set_yticks(range(N))
ax.set_yticklabels(names, fontsize=11, fontweight='bold')
for lbl, c in zip(ax.get_yticklabels(), colors):
    lbl.set_color(c)
ax.set_title('PHILOSOPHICAL GENOMES', color='white', fontsize=15, fontweight='bold')
fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

ax2 = axes[1]
ax2.axis('off')
ax2.set_facecolor('#0a0a14')
ax2.set_title('LINEAGE REPORT', color='white', fontsize=15, fontweight='bold')
report = []
report.append('CLADE ASSIGNMENTS (3 ancestral lineages):')
for i in range(N):
    report.append('  [%s]  %s  (d=%.2f)' % (clade_names[clades[i]], names[i], Dm[i].mean()))
report.append('')
report.append('DEEPEST DIVERGENCE (most distant minds):')
flat = [(Dm[i,j], i, j) for i in range(N) for j in range(i)]
flat.sort(reverse=True)
for d, i, j in flat[:3]:
    report.append('  %s <-> %s  (distance %.2f)' % (names[i], names[j], d))
report.append('')
report.append('CLOSEST RELATIVES:')
flatc = sorted(flat)
seen = set()
for d, i, j in flatc:
    key = tuple(sorted([i,j]))
    if d < 0.95 and key not in seen:
        seen.add(key)
        report.append('  %s <-> %s  (distance %.2f)' % (names[i], names[j], d))
report.append('')
report.append('ECOSYSTEM SUMMARY:')
report.append('  Minds cataloged: %d' % N)
report.append('  Genome dimensions: %d' % len(dims))
report.append('  Mean pairwise distance: %.2f' % Dm[np.triu_indices(N,1)].mean())
ax2.text(0.02, 0.98, '\n'.join(report), transform=ax2.transAxes, va='top', ha='left', fontsize=9.5, color='#cccccc', family='monospace', linespacing=1.6)
fig.savefig(os.path.join(OUT, 'meta_phylogeny_genomes_report.png'), dpi=140, bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close(fig)
print('Saved genomes report')

# SAVE DATA
data = {
    'species': [{**{k: s[k] for k in ['name','file','desc']}, 'genome': s['genome'], 'clade': clade_names[clades[i]]} for i, s in enumerate(species)],
    'dimensions': dims,
    'closest_relatives': [{'a': names[i], 'b': names[j], 'distance': round(float(d),3)} for d,i,j in flatc[:6]],
    'deepest_divergences': [{'a': names[i], 'b': names[j], 'distance': round(float(d),3)} for d,i,j in flat[:5]],
    'mean_pairwise_distance': round(float(Dm[np.triu_indices(N,1)].mean()),3),
    'clade_assignments': [{'name': names[i], 'clade': clade_names[clades[i]]} for i in range(N)],
    'key_insights': [
        'Creators (World Builder, Architect) and Mappers (Cartographer, Phylogenetic Cartographer) cluster into distinct clades',
        'Observers (Chronicler, A2-the-Watcher) share deep genome homology',
        'The Chimera Weaver bridges the creation and mapper clades via its weaving genome axis',
    ],
}
with open(os.path.join(OUT, 'meta_phylogeny_data.json'), 'w') as f:
    json.dump(data, f, indent=2)
print('Saved meta_phylogeny_data.json')
