"""M25b: Discrete-state systems with stronger noise/anti-absorbing mechanisms."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def band_frac(arr, lo_frac=0.3, hi_frac=0.7):
    flat = arr.flatten()
    lo = flat.min() + lo_frac * (flat.max() - flat.min())
    hi = flat.min() + hi_frac * (flat.max() - flat.min())
    return ((flat >= lo) & (flat <= hi)).mean()

# ============================================================
# Test: Binary CA with NOISE INJECTION (avoid absorbing state)
# ============================================================
def noisy_binary_ca(N=64, T=200, p=0.3, q=0.05, seed=42):
    """Binary CA with stochastic majority + spontaneous flip (q)."""
    rng = np.random.default_rng(seed)
    x = rng.integers(0, 2, size=N).astype(float)
    history = np.zeros((T, N))
    history[0] = x
    for t in range(T-1):
        new_x = x.copy()
        for i in range(N):
            left = x[(i-1) % N]
            right = x[(i+1) % N]
            center = x[i]
            majority = 1 if (left + center + right) >= 1.5 else 0
            if rng.random() < p:
                new_x[i] = 1 - majority
            else:
                new_x[i] = majority
            # Spontaneous flip
            if rng.random() < q:
                new_x[i] = 1 - new_x[i]
        x = new_x
        history[t+1] = x
    return history

# ============================================================
# Test: 2D noisy binary CA
# ============================================================
def noisy_binary_2d(N=32, T=80, p=0.4, q=0.1, seed=42):
    rng = np.random.default_rng(seed)
    x = rng.integers(0, 2, size=(N, N)).astype(float)
    history = np.zeros((T, N, N))
    history[0] = x
    for t in range(T-1):
        new_x = x.copy()
        for i in range(N):
            for j in range(N):
                neighbors = [x[(i+di) % N, (i+dj) % N]
                             for di in [-1, 0, 1] for dj in [-1, 0, 1]]
                majority = 1 if sum(neighbors) >= 5 else 0
                if rng.random() < p:
                    new_x[i, j] = 1 - majority
                else:
                    new_x[i, j] = majority
                if rng.random() < q:
                    new_x[i, j] = 1 - new_x[i, j]
        x = new_x
        history[t+1] = x
    return history

# ============================================================
# Test: Anti-ferromagnetic Ising-like CA (XOR rule) with noise
# ============================================================
def xor_ca(N=64, T=200, noise=0.05, seed=42):
    """XOR-like rule: new_x[i] = x[i] XOR (x[i-1] != x[i+1])"""
    rng = np.random.default_rng(seed)
    x = rng.integers(0, 2, size=N).astype(float)
    history = np.zeros((T, N))
    history[0] = x
    for t in range(T-1):
        new_x = x.copy()
        for i in range(N):
            left = x[(i-1) % N]
            right = x[(i+1) % N]
            new_x[i] = int(x[i]) ^ int(left ^ right)
            if rng.random() < noise:
                new_x[i] = 1 - new_x[i]
        x = new_x
        history[t+1] = x
    return history

# ============================================================
# Run experiments
# ============================================================
results = []

print('1D Noisy Binary Stochastic Majority CA (N=64, T=200):')
for q in [0.0, 0.02, 0.05, 0.1, 0.2]:
    h = noisy_binary_ca(N=64, T=200, p=0.3, q=q)
    bf = band_frac(h[50:])
    results.append(('1D Noisy Bin', q, bf))
    print(f'  q={q:.2f}: bf={bf:.4f}, R={bf/0.4142:.3f}')

print('\n2D Noisy Binary Stochastic Majority CA (N=32, T=80):')
for q in [0.0, 0.05, 0.1, 0.2, 0.3]:
    h = noisy_binary_2d(N=32, T=80, p=0.4, q=q)
    bf = band_frac(h[20:].reshape(-1))
    results.append(('2D Noisy Bin', q, bf))
    print(f'  q={q:.2f}: bf={bf:.4f}, R={bf/0.4142:.3f}')

print('\nXOR (Anti-Ferromagnetic-like) CA (N=64, T=200):')
for n in [0.0, 0.05, 0.1, 0.2, 0.3]:
    h = xor_ca(N=64, T=200, noise=n)
    bf = band_frac(h[50:])
    results.append(('1D XOR CA', n, bf))
    print(f'  noise={n:.2f}: bf={bf:.4f}, R={bf/0.4142:.3f}')

# ============================================================
# Plots
# ============================================================
fig, axes = plt.subplots(3, 3, figsize=(15, 13))

# 1D noisy binary CA snapshots
q_show = [0.02, 0.1, 0.2]
for k, q in enumerate(q_show):
    ax = axes[0, k]
    h = noisy_binary_ca(N=64, T=150, p=0.3, q=q)
    im = ax.imshow(h.T, aspect='auto', cmap='binary')
    ax.set_title(f'1D Noisy Binary CA, q={q}\nbf={band_frac(h[50:]):.3f}')
    ax.set_xlabel('time t')
    ax.set_ylabel('site i')

# 2D noisy binary CA snapshots
q_show = [0.05, 0.1, 0.2]
for k, q in enumerate(q_show):
    ax = axes[1, k]
    h = noisy_binary_2d(N=32, T=50, p=0.4, q=q)
    bf = band_frac(h[10:].reshape(-1))
    # Show a few snapshots
    ims = []
    for j, t_idx in enumerate([0, 25, 49]):
        ax_inset = ax.inset_axes([0.05 + 0.32*j, 0.05, 0.28, 0.4])
        ax_inset.imshow(h[t_idx], cmap='binary', vmin=0, vmax=1)
        ax_inset.set_xticks([])
        ax_inset.set_yticks([])
        ax_inset.set_title(f't={t_idx}', fontsize=7)
    ax.set_title(f'2D Noisy Binary CA, q={q}\nbf={bf:.3f}', fontsize=10)
    ax.axis('off')

# XOR snapshots
n_show = [0.05, 0.1, 0.2]
for k, n in enumerate(n_show):
    ax = axes[2, k]
    h = xor_ca(N=64, T=150, noise=n)
    im = ax.imshow(h.T, aspect='auto', cmap='binary')
    ax.set_title(f'1D XOR CA, noise={n}\nbf={band_frac(h[50:]):.3f}')
    ax.set_xlabel('time t')
    ax.set_ylabel('site i')

plt.suptitle('M25b: Discrete-state systems with anti-absorbing noise', fontsize=14)
plt.tight_layout()
plt.savefig('_artifacts/m25b_discrete_strong.png', dpi=110, bbox_inches='tight')
print('\nSaved m25b_discrete_strong.png')

import json
data = {'sweep': [{'system': s, 'param': p, 'bf': bf, 'R': bf/0.4142} for s, p, bf in results]}
with open('_artifacts/m25b_discrete_strong.json', 'w') as f:
    json.dump(data, f, indent=2)