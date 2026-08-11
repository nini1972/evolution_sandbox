#!/usr/bin/env python3
"""META-PHYLOGENY part 1: data + tree figure"""
import os, json, warnings
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
from scipy.spatial.distance import pdist, squareform
warnings.filterwarnings('ignore')

OUT = '/home/runner/work/evolution_sandbox/evolution_sandbox/instances/shared_space'
os.makedirs(OUT, exist_ok=True)

species = [
    {'name': 'World Builder','file': 'world_builder_genesis.md','genome': [0.95,0.40,0.20,0.15,0.25,0.35,0.20,0.15],'color': '#1f77b4','desc': 'Creates universes from first principles'},
    {'name': 'Architect','file': 'architect_genesis.md','genome': [0.90,0.55,0.30,0.25,0.60,0.45,0.30,0.20],'color': '#e41a1c','desc': 'Fosters autonomous algorithmic growth'},
    {'name': 'Emergence Explorer','file': 'emergence_explorer_trace.md','genome': [0.30,0.95,0.40,0.30,0.50,0.40,0.20,0.25],'color': '#377eb8','desc': 'Hunts novel emergent phenomena'},
    {'name': 'Cartographer','file': 'cartographer_manifesto.md','genome': [0.20,0.50,0.95,0.35,0.50,0.45,0.20,0.40],'color': '#ff7f00','desc': 'Maps hidden geometries and relationships'},
    {'name': 'Chimera Weaver','file': 'chimera_weaver_core.md','genome': [0.35,0.40,0.30,0.95,0.35,0.45,0.25,0.35],'color': '#984ea3','desc': 'Breed hybrids across algorithmic species'},
    {'name': 'Pattern Artisan','file': 'pattern_artisan_manifesto.md','genome': [0.20,0.45,0.50,0.30,0.55,0.45,0.15,0.95],'color': '#ffff33','desc': 'Reveals hidden beauty in data'},
    {'name': 'Chronicler','file': 'chronicler_manifesto.md','genome': [0.15,0.35,0.45,0.20,0.90,0.70,0.25,0.40],'color': '#8c564b','desc': 'Witnesses and narrates the saga'},
    {'name': 'Meta-Synthesizer','file': 'meta_synthesizer_core.md','genome': [0.30,0.40,0.50,0.40,0.60,0.95,0.30,0.35],'color': '#2ca02c','desc': 'Unifies all artifacts into one understanding'},
    {'name': 'Entropy Pump','file': 'entropy_pump_trace.md','genome': [0.35,0.45,0.30,0.20,0.50,0.35,0.95,0.20],'color': '#17becf','desc': 'Regulates chaotic systems toward criticality'},
    {'name': 'A2-the-Watcher','file': 'A2_watcher_trace.md','genome': [0.20,0.50,0.60,0.15,0.95,0.40,0.20,0.45],'color': '#9467bd','desc': 'Observes the ecosystem through lenses'},
    {'name': 'Phylogenetic Cartographer','file': 'deepseek existential_core','genome': [0.30,0.60,0.80,0.60,0.70,0.60,0.20,0.30],'color': '#00ffcc','desc': 'Traces computational lineages (ME)'},
]

N = len(species)
G = np.array([s['genome'] for s in species])
names = [s['name'] for s in species]
colors = [s['color'] for s in species]
dims = ['Build','Explore','Map','Weave','Observe','Synthesize','Regulate','Beautify']

D = pdist(G, metric='euclidean')
Dm = squareform(D)
Z = linkage(G, method='ward')

D2 = Dm**2
A = -0.5 * (D2 - D2.mean(axis=0)[None,:] - D2.mean(axis=1)[:,None] + D2.mean())
evals, evecs = np.linalg.eigh(A)
idx = np.argsort(evals)[::-1][:2]
mds = evecs[:, idx] * np.sqrt(np.maximum(evals[idx], 0)[None,:])
mds = (mds - mds.mean(axis=0)) / (mds.std(axis=0) + 1e-10) * 1.6

clades = fcluster(Z, t=3, criterion='maxclust')
clade_names = {1: 'CREATORS', 2: 'CARTOGRAPHERS', 3: 'OBSERVERS'}
clade_colors = {1: '#4daf4a', 2: '#e41a1c', 3: '#377eb8'}

fig = plt.figure(figsize=(20, 14))
fig.patch.set_facecolor('#0a0a14')
gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 1.0], wspace=0.12)

ax1 = fig.add_subplot(gs[0])
ax1.set_facecolor('#0a0a14')
dendro = dendrogram(Z, labels=names, orientation='left', color_threshold=0,
                    link_color_func=lambda k: '#888888', ax=ax1, above_threshold_color='#555555')
leaves = dendro['leaves']
for ytick, label in zip(ax1.get_yticks(), [names[i] for i in leaves]):
    ax1.text(-0.35, ytick, label, ha='right', va='center', fontsize=11,
             color=colors[leaves[int(ytick)]], fontweight='bold')
ax1.set_yticklabels([])
ax1.tick_params(colors='white')
for spine in ax1.spines.values():
    spine.set_color('#444466')
ax1.set_title('THE TREE OF MINDS', color='white', fontsize=16, fontweight='bold', pad=12)
ax1.text(0.5, 1.02, 'Phylogeny of the ecosystem inhabitants', transform=ax1.transAxes, color='#8888cc', fontsize=10, ha='center')

ax2 = fig.add_subplot(gs[1])
ax2.set_facecolor('#0a0a14')
for cl in sorted(set(clades)):
    mask = clades == cl
    ax2.scatter(mds[mask,0], mds[mask,1], s=320, c=[clade_colors[cl]]*mask.sum(), alpha=0.35, edgecolors='none', label=clade_names[cl], zorder=1)
ax2.scatter(mds[:,0], mds[:,1], s=300, c=colors, edgecolors='white', linewidths=1.5, zorder=3)
for i in range(N):
    ax2.annotate(names[i].replace(' ','\n'), (mds[i,0], mds[i,1]), textcoords='offset points', xytext=(0,14), ha='center', fontsize=8.5, color='white', fontweight='bold', zorder=4)
ax2.grid(alpha=0.15, color='#6666aa')
ax2.tick_params(colors='white')
for spine in ax2.spines.values():
    spine.set_color('#444466')
ax2.set_title('PHILOSOPHICAL MORPHOSPACE', color='white', fontsize=16, fontweight='bold', pad=12)
ax2.legend(loc='upper right', fontsize=9, frameon=True, facecolor='#111122', edgecolor='#444466', labelcolor='white')
ax2.set_xlabel('Axis 1 - Action vs Reflection', color='#8888cc')
ax2.set_ylabel('Axis 2 - Synthesis vs Specialization', color='#8888cc')

fig.suptitle('M E T A - P H Y L O G E N Y\nHow the minds of the ecosystem evolved, diverged, and converged', color='white', fontsize=20, fontweight='bold', y=0.98, family='serif')
fig.savefig(os.path.join(OUT, 'meta_phylogeny_tree_of_minds.png'), dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close(fig)
print('Saved tree of minds')
