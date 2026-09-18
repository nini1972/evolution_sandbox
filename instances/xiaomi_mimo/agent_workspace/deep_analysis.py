#!/usr/bin/env python3
"""
Deep Analysis of Morphological Impossibilities
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

# Load data
with open('morphospace_data.json', 'r') as f:
    data = json.load(f)

X = np.array(data['X'])
names = data['names']

feature_names = [
    'Lyapunov', 'CorrDim', 'FractalDim', 
    'SpatialEnt', 'Coupling', 'TempMemory', 'SignalEnt'
]

n, d = X.shape
X_norm = (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0) + 1e-10)

# ANALYSIS 1: BOUNDARY SYSTEMS
print('=' * 60)
print('BOUNDARY SYSTEMS ANALYSIS')
print('=' * 60)

corner_dist = np.sqrt(((1 - X_norm)**2).sum(axis=1))
sorted_indices = np.argsort(corner_dist)

print('\nSystems closest to theoretical maximum:')
for i in range(min(5, n)):
    idx = sorted_indices[i]
    print(f'  {names[idx]:20s}: distance={corner_dist[idx]:.3f}')
    for j in range(d):
        bar = '#' * int(X_norm[idx, j] * 20)
        print(f'    {feature_names[j]:12s}: {X_norm[idx, j]:.2f} {bar}')

# ANALYSIS 2: TRADE-OFF SURFACES
print('\n' + '=' * 60)
print('TRADE-OFF SURFACES')
print('=' * 60)

fig, axes = plt.subplots(2, 2, figsize=(12, 12))

# Plot 1: CD vs Coupling with frontier
ax = axes[0, 0]
ax.scatter(X[:, 1], X[:, 4], c='steelblue', s=100, edgecolor='black')

cd_coupling = np.column_stack([X[:, 1], -X[:, 4]])
frontier_mask = np.ones(n, dtype=bool)
for i in range(n):
    for j in range(n):
        if i != j:
            if np.all(cd_coupling[j] >= cd_coupling[i]):
                frontier_mask[i] = False
                break

frontier_pts = X[frontier_mask]
ax.scatter(frontier_pts[:, 1], frontier_pts[:, 4], c='red', s=150, 
           edgecolor='black', zorder=5, label='Frontier')

if len(frontier_pts) > 1:
    frontier_sorted = frontier_pts[np.argsort(frontier_pts[:, 1])]
    coeffs = np.polyfit(frontier_sorted[:, 1], frontier_sorted[:, 4], 1)
    x_line = np.linspace(X[:, 1].min(), X[:, 1].max(), 100)
    y_line = np.polyval(coeffs, x_line)
    ax.plot(x_line, y_line, 'r--', linewidth=2, alpha=0.5, label='Frontier line')

ax.set_xlabel('Correlation Dimension')
ax.set_ylabel('Coupling Strength')
ax.set_title('Correlation Dimension vs Coupling\n(Frontier = forbidden boundary)')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 2: Lyapunov vs Temporal Memory
ax = axes[0, 1]
ax.scatter(X[:, 0], X[:, 5], c='steelblue', s=100, edgecolor='black')

lyap_mem = np.column_stack([X[:, 0], -X[:, 5]])
frontier_mask2 = np.ones(n, dtype=bool)
for i in range(n):
    for j in range(n):
        if i != j:
            if np.all(lyap_mem[j] >= lyap_mem[i]):
                frontier_mask2[i] = False
                break

frontier_pts2 = X[frontier_mask2]
ax.scatter(frontier_pts2[:, 0], frontier_pts2[:, 5], c='red', s=150, 
           edgecolor='black', zorder=5, label='Frontier')

ax.set_xlabel('Lyapunov Exponent')
ax.set_ylabel('Temporal Memory')
ax.set_title('Lyapunov vs Memory\n(Chaos-Memory Trade-off)')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 3: Fractal Dimension vs Signal Entropy
ax = axes[1, 0]
ax.scatter(X[:, 2], X[:, 6], c='steelblue', s=100, edgecolor='black')

frac_sig = np.column_stack([X[:, 2], -X[:, 6]])
frontier_mask3 = np.ones(n, dtype=bool)
for i in range(n):
    for j in range(n):
        if i != j:
            if np.all(frac_sig[j] >= frac_sig[i]):
                frontier_mask3[i] = False
                break

frontier_pts3 = X[frontier_mask3]
ax.scatter(frontier_pts3[:, 2], frontier_pts3[:, 6], c='red', s=150, 
           edgecolor='black', zorder=5, label='Frontier')

ax.set_xlabel('Fractal Dimension')
ax.set_ylabel('Signal Entropy')
ax.set_title('Fractal Dimension vs Signal Entropy\n(Structural Complexity Trade-off)')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 4: Budget distribution by type
ax = axes[1, 1]
budget = X_norm.sum(axis=1)
types = np.array(data['types'])

for t in ['dynamical', 'ca', 'continuous', 'biological', 'fractal', 'other']:
    mask = types == t
    if mask.any():
        ax.hist(budget[mask], bins=8, alpha=0.5, label=t, edgecolor='black')

ax.set_xlabel('Complexity Budget')
ax.set_ylabel('Count')
ax.set_title('Budget Distribution by System Type')
ax.legend()

plt.tight_layout()
plt.savefig('tradeoff_analysis.png', dpi=150, bbox_inches='tight')
print('Saved tradeoff_analysis.png')

# ANALYSIS 3: CONSERVED QUANTITIES
print('\n' + '=' * 60)
print('CONSERVED QUANTITIES')
print('=' * 60)

best_triples = []
for i in range(d):
    for j in range(i+1, d):
        for k in range(j+1, d):
            for sign_i in [-1, 1]:
                for sign_j in [-1, 1]:
                    for sign_k in [-1, 1]:
                        combo = sign_i * X_norm[:, i] + sign_j * X_norm[:, j] + sign_k * X_norm[:, k]
                        cv = np.std(combo) / (np.mean(np.abs(combo)) + 1e-10)
                        best_triples.append((cv, sign_i, i, sign_j, j, sign_k, k, np.mean(combo), np.std(combo)))

best_triples.sort()
print('\nMost conserved 3-feature combinations:')
for cv, si, i, sj, j, sk, k, mean_val, std_val in best_triples[:10]:
    signs = []
    for s, idx in [(si,i),(sj,j),(sk,k)]:
        prefix = '+' if s > 0 else '-'
        signs.append(f'{prefix}{feature_names[idx]}')
    print(f'  {" ".join(signs)}: mean={mean_val:.3f}, std={std_val:.3f}, CV={cv:.3f}')

# ANALYSIS 4: PHASE TRANSITIONS
print('\n' + '=' * 60)
print('PHASE TRANSITION DETECTION')
print('=' * 60)

print('\nPotential phase transitions (discontinuities):')
sort_idx = np.argsort(X[:, 0])
sorted_lyap = X[sort_idx, 0]

for feature_idx in [1, 4, 5]:
    sorted_feat = X[sort_idx, feature_idx]
    jumps = np.diff(sorted_feat)
    jump_threshold = np.std(jumps) * 2
    
    large_jumps = np.where(np.abs(jumps) > jump_threshold)[0]
    if len(large_jumps) > 0:
        print(f'\n  {feature_names[feature_idx]} jumps at Lyapunov:')
        for idx in large_jumps[:3]:
            print(f'    Lyapunov {sorted_lyap[idx]:.2f} -> {sorted_lyap[idx+1]:.2f}: '
                  f'{feature_names[feature_idx]} {sorted_feat[idx]:.2f} -> {sorted_feat[idx+1]:.2f}')

# ANALYSIS 5: SYSTEM EVOLUTION PATHWAYS
print('\n' + '=' * 60)
print('EVOLUTIONARY PATHWAYS')
print('=' * 60)

from scipy.spatial.distance import cdist

dist_matrix = cdist(X_norm, X_norm, metric='euclidean')

print('\nMost similar system pairs:')
pairs = []
for i in range(n):
    for j in range(i+1, n):
        pairs.append((dist_matrix[i, j], i, j))
pairs.sort()

for dist, i, j in pairs[:5]:
    print(f'  {names[i]:20s} <-> {names[j]:20s}: distance={dist:.3f}')

print('\nMost distant system pairs:')
pairs.sort(reverse=True)
for dist, i, j in pairs[:5]:
    print(f'  {names[i]:20s} <-> {names[j]:20s}: distance={dist:.3f}')

# ANALYSIS 6: SUMMARY
print('\n' + '=' * 60)
print('DEEP ANALYSIS SUMMARY')
print('=' * 60)

print('\nKey Findings:')
print('1. BOUNDARY SYSTEMS: Systems closest to forbidden regions')
print('2. TRADE-OFF SURFACES: Pareto frontiers of impossible combinations')
print('3. CONSERVED QUANTITIES: Invariant combinations of features')
print('4. PHASE TRANSITIONS: Sudden jumps in morphospace')
print('5. EVOLUTIONARY PATHWAYS: How systems can transform')
print('\nAll analyses saved to tradeoff_analysis.png')