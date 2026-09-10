#!/usr/bin/env python3
"""Morphological Invariants Analysis: Finding Universal Patterns"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

with open('morphospace_data.json') as f:
    data = json.load(f)

names = data['names']
X = np.array(data['X'])
X_pca = np.array(data['X_pca'])
colors = data['colors']
types = data['types']
regimes = data['regimes']
feature_names = ['entropy_rate', 'lyapunov', 'fractal_dim',
                 'spatial_cx', 'temporal_mem', 'sync', 'eff_dim']

# ═══════════════════════════════════════════════════════════════════
# ANALYSIS 1: Morphological Invariants
# What features are conserved across substrate types?
# ═══════════════════════════════════════════════════════════════════

# Group by type
type_groups = {}
for i, t in enumerate(types):
    if t not in type_groups:
        type_groups[t] = []
    type_groups[t].append(i)

print("=" * 70)
print("MORPHOLOGICAL INVARIANTS BY SUBSTRATE TYPE")
print("=" * 70)

for t, indices in sorted(type_groups.items()):
    print(f"\n{t} ({len(indices)} systems):")
    for fname_idx, fname in enumerate(feature_names):
        vals = [X[i, fname_idx] for i in indices]
        mean = np.mean(vals)
        std = np.std(vals)
        cv = std / mean if mean != 0 else 0  # coefficient of variation
        invariant = "INVARIANT" if cv < 0.3 else "VARIABLE"
        print(f"  {fname:15s}: {mean:.3f} ± {std:.3f} (CV={cv:.2f}) [{invariant}]")

# ═══════════════════════════════════════════════════════════════════
# ANALYSIS 2: Morphological Exclusions
# What features cannot coexist?
# ═══════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("MORPHOLOGICAL EXCLUSIONS (Anti-correlations)")
print("=" * 70)

# Compute feature correlations
corr = np.corrcoef(X.T)
for i in range(len(feature_names)):
    for j in range(i+1, len(feature_names)):
        if corr[i, j] < -0.4:
            print(f"  EXCLUSION: {feature_names[i]} ↔ {feature_names[j]}: r={corr[i, j]:.3f}")

# Find systems with high values in "opposing" features
print("\nSystems that violate exclusions (potential transitions):")
for i in range(len(names)):
    # High sync but high chaos
    if X[i, 5] > 0.5 and X[i, 1] > 0.5:
        print(f"  {names[i]}: sync={X[i,5]:.3f}, lyapunov={X[i,1]:.3f}")
    # High fractal_dim but low entropy
    if X[i, 2] > 1.8 and X[i, 0] < 0.3:
        print(f"  {names[i]}: fractal_dim={X[i,2]:.3f}, entropy={X[i,0]:.3f}")

# ═══════════════════════════════════════════════════════════════════
# ANALYSIS 3: Morphological Transitions
# How do structures change along parameter axes?
# ═══════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("MORPHOLOGICAL TRANSITIONS")
print("=" * 70)

# Identify paired systems (same type, different regime)
transition_pairs = [
    ('Logistic (r=3.8)', 'Logistic (period-3)', 'Period Doubling ↔ Chaos'),
    ('Std Map (K=0.5)', 'Std Map (K=5)', 'KAM ↔ Global Chaos'),
    ('Kuramoto (sync)', 'Kuramoto (chimera)', 'Sync ↔ Chimera'),
    ('NoiseGarden (plastic)', 'NoiseGarden (fixed)', 'Plastic ↔ Fixed'),
    ('Thomas', 'Aizawa', 'Weak ↔ Strong Chaos'),
]

for name1, name2, desc in transition_pairs:
    i1 = names.index(name1)
    i2 = names.index(name2)
    delta = X[i2] - X[i1]
    print(f"\n  {desc}:")
    print(f"    {name1} → {name2}")
    for k, fname in enumerate(feature_names):
        if abs(delta[k]) > 0.3:
            arrow = "↑" if delta[k] > 0 else "↓"
            print(f"    {fname:15s}: {delta[k]:+.3f} {arrow}")

# ═══════════════════════════════════════════════════════════════════
# ANALYSIS 4: Ideal Emergence Point
# What would the "optimal" emergent system look like?
# ═══════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("IDEAL EMERGENCE ANALYSIS")
print("=" * 70)

# Define ideal emergence (edge of chaos, high structure, high memory)
ideal = np.array([2.0, 0.3, 1.7, 0.3, 3.0, 0.5, 2.5])

# Distance to ideal
X_norm = (X - X.mean(axis=0)) / X.std(axis=0)
ideal_norm = (ideal - X.mean(axis=0)) / X.std(axis=0)
distances = np.sqrt(np.sum((X_norm - ideal_norm) ** 2, axis=1))

print("\nDistance to ideal emergence point (sorted):")
idx_sorted = np.argsort(distances)
for rank, i in enumerate(idx_sorted):
    print(f"  {rank+1:2d}. {names[i]:35s} d={distances[i]:.3f}")

# What features contribute most to the "gap"?
print("\nFeature gaps from ideal (averaged over all substrates):")
gaps = []
for k, fname in enumerate(feature_names):
    avg_gap = np.mean(np.abs(X[:, k] - ideal[k]))
    gaps.append((avg_gap, fname))
gaps.sort(reverse=True)
for gap, fname in gaps:
    print(f"  {fname:15s}: avg gap = {gap:.3f}")

# ═══════════════════════════════════════════════════════════════════
# ANALYSIS 5: Morphological Complexity Index
# ═══════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("MORPHOLOGICAL COMPLEXITY INDEX")
print("=" * 70)

# Composite index: weighted combination of features
# Higher = more "complex" in the morphological sense
weights = {
    'entropy_rate': 1.0,
    'lyapunov': 1.5,      # Chaos is a complexity amplifier
    'fractal_dim': 1.5,    # Fractal structure = complexity
    'spatial_cx': 1.0,
    'temporal_mem': 1.0,
    'sync': 0.5,           # Sync reduces complexity
    'eff_dim': 0.8
}

complexity = np.zeros(len(names))
for k, fname in enumerate(feature_names):
    # Normalize to [0, 1]
    fmin, fmax = X[:, k].min(), X[:, k].max()
    if fmax > fmin:
        f_norm = (X[:, k] - fmin) / (fmax - fmin)
    else:
        f_norm = np.zeros(len(names))
    # Special handling for sync (invert - high sync = lower complexity)
    if fname == 'sync':
        f_norm = 1 - f_norm
    complexity += weights[fname] * f_norm

complexity /= sum(weights.values())

print("\nMorphological Complexity Index (sorted):")
idx_sorted = np.argsort(complexity)[::-1]
for rank, i in enumerate(idx_sorted):
    bar = "█" * int(complexity[i] * 30)
    print(f"  {rank+1:2d}. {names[i]:35s} {complexity[i]:.3f} {bar}")

# Save analysis results
results = {
    'type_invariants': {},
    'exclusions': [],
    'transitions': [],
    'ideal_distances': {names[i]: float(distances[i]) for i in range(len(names))},
    'complexity_index': {names[i]: float(complexity[i]) for i in range(len(names))},
    'feature_correlations': corr.tolist()
}

for t, indices in type_groups.items():
    invariants = {}
    for fname_idx, fname in enumerate(feature_names):
        vals = [X[i, fname_idx] for i in indices]
        invariants[fname] = {'mean': float(np.mean(vals)), 'std': float(np.std(vals))}
    results['type_invariants'][t] = invariants

for name1, name2, desc in transition_pairs:
    i1 = names.index(name1)
    i2 = names.index(name2)
    delta = X[i2] - X[i1]
    results['transitions'].append({
        'from': name1, 'to': name2, 'description': desc,
        'delta': {feature_names[k]: float(delta[k]) for k in range(len(feature_names))}
    })

with open('morphology_invariants.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nAnalysis saved to morphology_invariants.json")
