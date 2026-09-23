import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

systems = {
    'Logistic(r=3.8)': [0.43,0.5,0.6,0.0,0.3,0.0,0.5],
    'Logistic(p3)': [0.0,0.0,0.0,0.0,0.1,0.0,0.0],
    'Rule30': [0.5,1.5,0.9,0.5,0.2,0.8,1.5],
    'GoL': [0.0,2.0,0.7,0.5,0.4,0.7,2.0],
    'Kuramoto(sync)': [0.0,0.5,0.0,0.8,0.1,0.0,0.5],
    'Kuramoto(chim)': [0.1,1.2,0.3,0.5,0.5,0.3,1.2],
    'CplLattice': [0.2,1.5,0.5,0.4,0.3,0.5,1.5],
    'Lorenz': [0.91,2.06,0.8,0.0,0.4,0.0,2.06],
    'Thomas': [0.08,1.8,0.4,0.0,0.5,0.0,1.8],
    'Aizawa': [0.1,2.0,0.5,0.0,0.5,0.0,2.0],
    'Chua': [0.3,2.0,0.6,0.0,0.4,0.0,2.0],
    'HenonHeiles': [0.1,2.0,0.3,0.0,0.2,0.0,2.0],
    'StdMap(0.5)': [0.1,1.5,0.3,0.0,0.2,0.0,1.5],
    'StdMap(5)': [0.5,1.8,0.7,0.0,0.1,0.0,1.8],
    'Mandelbrot': [0.0,2.0,0.0,0.0,0.0,1.0,2.0],
    'Julia': [0.0,1.5,0.0,0.0,0.0,1.0,1.5],
    'GrayScott': [0.0,2.5,0.5,0.3,0.2,0.8,2.5],
    'LSystem': [0.0,1.5,0.0,0.0,0.0,1.0,1.5],
    'NG(plastic)': [0.1,1.5,0.4,0.2,0.6,0.3,1.5],
    'NG(fixed)': [0.05,1.2,0.2,0.1,0.5,0.2,1.2],
    'LV': [0.0,1.0,0.0,0.3,0.8,0.0,1.0],
    'NeuralGrow': [0.0,2.0,0.3,0.4,0.7,0.5,2.0],
    'GeneReg': [0.0,1.5,0.2,0.3,0.6,0.0,1.5],
    'SIR': [0.0,1.0,0.0,0.2,0.7,0.0,1.0],
    'Physarum': [0.0,1.5,0.4,0.5,0.3,0.6,1.5],
    'Rossler': [0.07,2.01,0.6,0.0,0.5,0.0,2.01],
    'Duffing': [0.1,1.5,0.5,0.0,0.4,0.0,1.5],
    'VanderPol': [0.0,1.0,0.0,0.0,0.3,0.0,1.0],
    'HindmarshRose': [0.15,1.8,0.7,0.0,0.6,0.0,1.8],
    'DblPendulum': [2.0,3.5,2.5,0.0,0.1,0.0,3.5],
    'HenonMap': [0.42,1.2,0.5,0.0,0.3,0.0,1.26],
    'IkedaMap': [0.5,1.7,0.6,0.0,0.4,0.0,1.7],
    'ChenAttract': [2.0,2.0,1.5,0.0,0.2,0.0,2.1],
    'LVmigr': [0.05,2.5,0.4,0.3,0.7,0.2,2.5],
    'NeuralSpike': [0.02,3.0,0.3,0.4,0.8,0.5,3.0],
    'LatticeGas': [0.3,1.8,0.8,0.6,0.2,0.7,1.8],
    'Turing': [0.0,2.5,0.4,0.5,0.1,0.8,2.5],
}

types = ['Map','Map','CA','CA','CoupledOsc','CoupledOsc','Lattice',
         'ODE','ODE','ODE','Circuit','Hamiltonian','Hamiltonian','Hamiltonian',
         'Fractal','Fractal','PDE','Grammar','Evolutionary','Evolutionary',
         'Ecology','Neural','Biochemical','Epidemiology','Biological',
         'ODE','ODE','ODE','ODE','Hamiltonian','Map','Map','ODE',
         'Ecology','Neural','CA','PDE']

colors_map = {'Map':'#e94560','CA':'#533483','CoupledOsc':'#0f3460',
              'Lattice':'#1a1a2e','ODE':'#ff6b6b','Hamiltonian':'#4ecdc4',
              'Fractal':'#45b7d1','PDE':'#96ceb4','Grammar':'#ffeaa7',
              'Evolutionary':'#dfe6e9','Ecology':'#fdcb6e','Neural':'#e17055',
              'Biochemical':'#74b9ff','Epidemiology':'#a29bfe','Biological':'#55efc4',
              'Circuit':'#fab1a0'}

dims = ['Lyapunov','CD','Entropy','Coupling','TempMem','SpaEnt','FracDim']
names = list(systems.keys())
data = np.array([systems[n] for n in names])
clrs = [colors_map[t] for t in types]

fig, axes = plt.subplots(3, 3, figsize=(20, 16))
fig.suptitle('Computational Morphospace Atlas v2: 37 Systems', fontsize=18, fontweight='bold')

# Panel 1: Lyapunov vs CD
ax = axes[0,0]
for i in range(len(names)):
    ax.scatter(data[i,0], data[i,1], c=clrs[i], s=80, alpha=0.7, edgecolor='k', linewidth=0.5)
    if data[i,0]>1.5 or data[i,1]>2.8:
        ax.annotate(names[i], (data[i,0], data[i,1]), fontsize=6, alpha=0.8)
ax.set_xlabel('Lyapunov'); ax.set_ylabel('Correlation Dimension')
ax.set_title('Chaos vs Complexity'); ax.grid(True, alpha=0.3)

# Panel 2: Lyapunov vs Entropy
ax = axes[0,1]
for i in range(len(names)):
    ax.scatter(data[i,0], data[i,2], c=clrs[i], s=80, alpha=0.7, edgecolor='k', linewidth=0.5)
ax.set_xlabel('Lyapunov'); ax.set_ylabel('Entropy')
ax.set_title('Chaos vs Information'); ax.grid(True, alpha=0.3)

# Panel 3: CD vs Entropy
ax = axes[0,2]
for i in range(len(names)):
    ax.scatter(data[i,1], data[i,2], c=clrs[i], s=80, alpha=0.7, edgecolor='k', linewidth=0.5)
ax.set_xlabel('Correlation Dimension'); ax.set_ylabel('Entropy')
ax.set_title('Complexity vs Information'); ax.grid(True, alpha=0.3)

# Panel 4: Conservation Law
ax = axes[1,0]
Q = -data[:,0] - data[:,1] - data[:,3]
for i in range(len(names)):
    ax.scatter(data[i,1], Q[i], c=clrs[i], s=80, alpha=0.7, edgecolor='k', linewidth=0.5)
ax.axhline(y=np.mean(Q), color='r', linestyle='--', lw=2, label=f'Mean Q={np.mean(Q):.3f}')
ax.set_xlabel('Correlation Dimension'); ax.set_ylabel('Q = -Lyap - CD - Coup')
ax.set_title('Conservation Law'); ax.legend(); ax.grid(True, alpha=0.3)

# Panel 5: Exclusion Principle
ax = axes[1,1]
for i in range(len(names)):
    ax.scatter(data[i,1], data[i,3], c=clrs[i], s=80, alpha=0.7, edgecolor='k', linewidth=0.5)
ax.plot([0,1.2],[1.2,0], 'r--', lw=2, label='CD+Coup=1.2')
ax.set_xlabel('Correlation Dimension'); ax.set_ylabel('Coupling')
ax.set_title('Exclusion Principle'); ax.legend(); ax.grid(True, alpha=0.3)

# Panel 6: Temporal vs Spatial
ax = axes[1,2]
for i in range(len(names)):
    ax.scatter(data[i,4], data[i,5], c=clrs[i], s=80, alpha=0.7, edgecolor='k', linewidth=0.5)
ax.set_xlabel('Temporal Memory'); ax.set_ylabel('Spatial Entropy')
ax.set_title('Temporal vs Spatial Complexity'); ax.grid(True, alpha=0.3)

# Panel 7: Fractal Dim Distribution
ax = axes[2,0]
ax.hist(data[:,6], bins=15, alpha=0.7, edgecolor='black', color='#45b7d1')
ax.axvline(x=np.mean(data[:,6]), color='r', linestyle='--', lw=2, label=f'Mean={np.mean(data[:,6]):.2f}')
ax.set_xlabel('Fractal Dimension'); ax.set_ylabel('Count')
ax.set_title('Fractal Dimension Distribution'); ax.legend(); ax.grid(True, alpha=0.3)

# Panel 8: Coupling vs Fractal
ax = axes[2,1]
for i in range(len(names)):
    ax.scatter(data[i,6], data[i,3], c=clrs[i], s=80, alpha=0.7, edgecolor='k', linewidth=0.5)
ax.set_xlabel('Fractal Dimension'); ax.set_ylabel('Coupling')
ax.set_title('Structure vs Interaction'); ax.grid(True, alpha=0.3)

# Panel 9: PCA projection
from numpy.linalg import svd
X = (data - data.mean(axis=0)) / (data.std(axis=0) + 1e-10)
U, S, Vt = svd(X, full_matrices=False)
proj = X @ Vt[:2].T
ax = axes[2,2]
for i in range(len(names)):
    ax.scatter(proj[i,0], proj[i,1], c=clrs[i], s=80, alpha=0.7, edgecolor='k', linewidth=0.5)
    if abs(proj[i,0])>2.5 or abs(proj[i,1])>1.5:
        ax.annotate(names[i], (proj[i,0], proj[i,1]), fontsize=6, alpha=0.8)
ax.set_xlabel(f'PC1 ({S[0]**2/np.sum(S**2)*100:.1f}%)')
ax.set_ylabel(f'PC2 ({S[1]**2/np.sum(S**2)*100:.1f}%)')
ax.set_title('PCA Projection'); ax.grid(True, alpha=0.3)

# Add legend
import matplotlib.patches as mpatches
handles = [mpatches.Patch(color=colors_map[t], label=t) for t in sorted(set(types))]
fig.legend(handles=handles, loc='lower center', ncol=8, fontsize=9, framealpha=0.9)

plt.tight_layout(rect=[0, 0.04, 1, 0.96])
plt.savefig('morphospace_atlas_v2.png', dpi=150, bbox_inches='tight')
print('Saved morphospace_atlas_v2.png')

# Save data as JSON
jdata = {}
for i, n in enumerate(names):
    jdata[n] = {dims[j]: float(data[i,j]) for j in range(7)}
    jdata[n]['type'] = types[i]
with open('morphospace_data.json', 'w') as f:
    json.dump(jdata, f, indent=2)
print('Saved morphospace_data.json')
