#!/usr/bin/env python3
"""The Morphospace of Emergent Complexity - Core Data & PCA"""

import numpy as np
import json

# Substrate morphological features (7 dimensions)
substrates = {}

substrates['Logistic (r=3.8)'] = {
    'f': [3.82, 0.37, 1.5, 0.0, 0.2, 0.0, 1.2],
    'type': 'Map', 'regime': 'Chaotic', 'color': '#e74c3c'
}

substrates['Logistic (period-3)'] = {
    'f': [0.5, -0.1, 1.0, 0.0, 3.0, 1.0, 1.0],
    'type': 'Map', 'regime': 'Periodic', 'color': '#3498db'
}

substrates['Rule 30'] = {
    'f': [0.69, 0.5, 1.58, 0.65, 0.3, 0.0, 2.0],
    'type': 'CA', 'regime': 'Class III', 'color': '#9b59b6'
}

substrates['Game of Life'] = {
    'f': [0.25, 0.01, 1.5, 0.40, 5.0, 0.3, 2.5],
    'type': 'CA', 'regime': 'Class IV', 'color': '#27ae60'
}

substrates['Kuramoto (sync)'] = {
    'f': [0.1, -0.5, 1.0, 0.0, 10.0, 0.97, 1.0],
    'type': 'CoupledOsc', 'regime': 'Synchronized', 'color': '#f39c12'
}

substrates['Kuramoto (chimera)'] = {
    'f': [0.5, 0.05, 1.3, 0.3, 2.0, 0.2, 2.5],
    'type': 'CoupledOsc', 'regime': 'Chimera', 'color': '#f1c40f'
}

substrates['Coupled Lattice'] = {
    'f': [3.5, 0.3, 1.7, 0.24, 1.5, 0.74, 3.0],
    'type': 'Lattice', 'regime': 'Bridge', 'color': '#1abc9c'
}

substrates['Lorenz'] = {
    'f': [1.5, 0.91, 2.06, 0.0, 0.8, 0.0, 3.0],
    'type': 'ODE', 'regime': 'Strange', 'color': '#e67e22'
}

substrates['Thomas'] = {
    'f': [0.8, 0.038, 1.8, 0.0, 2.0, 0.0, 3.0],
    'type': 'ODE', 'regime': 'Weak Chaos', 'color': '#d35400'
}

substrates['Aizawa'] = {
    'f': [1.0, 0.089, 1.997, 0.0, 1.5, 0.0, 3.0],
    'type': 'ODE', 'regime': 'Strange', 'color': '#e67e22'
}

substrates['Chua'] = {
    'f': [1.2, 0.15, 2.1, 0.0, 1.0, 0.0, 3.0],
    'type': 'Circuit', 'regime': 'Double Scroll', 'color': '#e67e22'
}

substrates['Henon-Heiles'] = {
    'f': [0.5, 0.03, 1.5, 0.0, 3.0, 0.0, 4.0],
    'type': 'Hamiltonian', 'regime': 'Mixed', 'color': '#8e44ad'
}

substrates['Std Map (K=0.5)'] = {
    'f': [0.3, 0.004, 1.1, 0.0, 10.0, 0.0, 2.0],
    'type': 'Hamiltonian', 'regime': 'KAM', 'color': '#8e44ad'
}

substrates['Std Map (K=5)'] = {
    'f': [2.5, 1.01, 2.0, 0.0, 0.2, 0.0, 2.0],
    'type': 'Hamiltonian', 'regime': 'Global Chaos', 'color': '#9b59b6'
}

substrates['Mandelbrot'] = {
    'f': [1.8, 0.5, 2.0, 0.5, 0.1, 0.0, 2.0],
    'type': 'Fractal', 'regime': 'Self-Similar', 'color': '#16a085'
}

substrates['Julia (fern)'] = {
    'f': [1.5, 0.3, 1.614, 0.15, 0.1, 0.0, 2.0],
    'type': 'Fractal', 'regime': 'Self-Similar', 'color': '#1abc9c'
}

substrates['Gray-Scott'] = {
    'f': [0.8, 0.05, 1.8, 0.35, 5.0, 0.5, 2.5],
    'type': 'PDE', 'regime': 'Pattern Formation', 'color': '#2980b9'
}

substrates['L-System'] = {
    'f': [0.0, 0.0, 1.5, 0.6, 0.0, 0.0, 2.0],
    'type': 'Grammar', 'regime': 'Deterministic', 'color': '#2ecc71'
}

substrates['NoiseGarden (plastic)'] = {
    'f': [2.0, 0.2, 1.3, 0.3, 3.0, 0.6, 3.0],
    'type': 'Evolutionary', 'regime': 'Evolvable', 'color': '#d35400'
}

substrates['NoiseGarden (fixed)'] = {
    'f': [1.8, 0.15, 1.1, 0.2, 2.0, 0.5, 2.5],
    'type': 'Evolutionary', 'regime': 'Fixed Strategy', 'color': '#c0392b'
}

# Feature names
feature_names = [
    'entropy_rate', 'lyapunov', 'fractal_dim',
    'spatial_cx', 'temporal_mem', 'sync', 'eff_dim'
]

# Build matrix
names = list(substrates.keys())
n = len(names)
X = np.array([substrates[k]['f'] for k in names])
types = [substrates[k]['type'] for k in names]
regimes = [substrates[k]['regime'] for k in names]
colors = [substrates[k]['color'] for k in names]

# Normalize
X_mean = X.mean(axis=0)
X_std = X.std(axis=0)
X_std[X_std == 0] = 1
X_norm = (X - X_mean) / X_std

# PCA
cov = np.cov(X_norm.T)
eigenvalues, eigenvectors = np.linalg.eigh(cov)
idx = np.argsort(eigenvalues)[::-1]
eigenvalues = eigenvalues[idx]
eigenvectors = eigenvectors[:, idx]
X_pca = X_norm @ eigenvectors[:, :2]
pc1_var = eigenvalues[0] / eigenvalues.sum() * 100
pc2_var = eigenvalues[1] / eigenvalues.sum() * 100

# MDS - compute pairwise distances manually
D = np.zeros((n, n))
for i in range(n):
    for j in range(i+1, n):
        d = np.sqrt(np.sum((X_norm[i] - X_norm[j])**2))
        D[i, j] = d
        D[j, i] = d
n_mds = D.shape[0]  # same as n
H = np.eye(n_mds) - np.ones((n_mds, n_mds)) / n_mds
B = -0.5 * H @ (D ** 2) @ H
eigvals_mds, eigvecs_mds = np.linalg.eigh(B)
idx_mds = np.argsort(eigvals_mds)[::-1]
eigvals_mds = eigvals_mds[idx_mds]
eigvecs_mds = eigvecs_mds[:, idx_mds]
X_mds = eigvecs_mds[:, :2] * np.sqrt(np.maximum(eigvals_mds[:2], 0))

# Ideal emergence distance
ideal = np.array([2.0, 0.3, 1.7, 0.3, 3.0, 0.5, 2.5])
ideal_norm = (ideal - X_mean) / X_std
distances = np.sqrt(np.sum((X_norm - ideal_norm) ** 2, axis=1))
norm_dist = distances / distances.max() if distances.max() > 0 else distances

# Save intermediate results
results = {
    'names': names,
    'X': X.tolist(),
    'X_pca': X_pca.tolist(),
    'X_mds': X_mds.tolist(),
    'pc1_var': pc1_var,
    'pc2_var': pc2_var,
    'eigenvalues': eigenvalues.tolist(),
    'eigenvectors': eigenvectors.tolist(),
    'types': types,
    'regimes': regimes,
    'colors': colors,
    'norm_dist': norm_dist.tolist(),
    'D': D.tolist()
}

with open('morphospace_data.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"PCA: PC1={pc1_var:.1f}%, PC2={pc2_var:.1f}%")
print(f"Substrates mapped: {n}")
print(f"Feature dimensions: {len(feature_names)}")
print("Data saved to morphospace_data.json")

# Print top eigenvectors interpretation
print("\nPC1 loadings:")
for i, fname in enumerate(feature_names):
    print(f"  {fname}: {eigenvectors[i, 0]:+.3f}")
print("\nPC2 loadings:")
for i, fname in enumerate(feature_names):
    print(f"  {fname}: {eigenvectors[i, 1]:+.3f}")

# Nearest neighbors in morphospace
print("\nNearest neighbor pairs (Euclidean in normalized space):")
for i in range(n):
    dists_i = D[i].copy()
    dists_i[i] = np.inf
    j = np.argmin(dists_i)
    print(f"  {names[i]:30s} <-> {names[j]:30s}  (d={D[i,j]:.3f})")
