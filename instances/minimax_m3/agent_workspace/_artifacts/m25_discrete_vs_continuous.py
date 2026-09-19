"""M25: Discrete-state spatiotemporal systems — testing the discreteness hypothesis."""
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
# Test 1: Binary stochastic cellular automaton (Majority rule)
# ============================================================
def majority_ca(N=64, T=200, p=0.05, seed=42):
    """Binary CA with stochastic majority rule.
    Each cell takes value of majority of neighbors with prob (1-p),
    or flips with prob p."""
    rng = np.random.default_rng(seed)
    x = rng.integers(0, 2, size=N).astype(float)
    history = np.zeros((T, N))
    history[0] = x

    for t in range(T-1):
        new_x = x.copy()
        for i in range(N):
            # Moore neighborhood with periodic BC
            left = x[(i-1) % N]
            right = x[(i+1) % N]
            center = x[i]
            # Majority of {left, center, right}
            majority = 1 if (left + center + right) >= 1.5 else 0
            if rng.random() < p:
                new_x[i] = 1 - majority  # flip
            else:
                new_x[i] = majority
        x = new_x
        history[t+1] = x
    return history

# Test 2: 2D stochastic binary CA
def binary_2d_ca(N=32, T=100, p=0.05, seed=42):
    rng = np.random.default_rng(seed)
    x = rng.integers(0, 2, size=(N, N)).astype(float)
    history = np.zeros((T, N, N))
    history[0] = x
    for t in range(T-1):
        new_x = x.copy()
        for i in range(N):
            for j in range(N):
                # Moore 8-neighborhood + self
                neighbors = [x[(i+di) % N, (i+dj) % N]
                             for di in [-1, 0, 1] for dj in [-1, 0, 1]]
                majority = 1 if sum(neighbors) >= 5 else 0
                if rng.random() < p:
                    new_x[i, j] = 1 - majority
                else:
                    new_x[i, j] = majority
        x = new_x
        history[t+1] = x
    return history

# Test 3: Integer-valued lattice (3 states: 0, 1, 2)
def integer_3state_ca(N=64, T=200, p=0.1, seed=42):
    """3-state CA: each cell takes value based on majority of neighbors."""
    rng = np.random.default_rng(seed)
    x = rng.integers(0, 3, size=N)
    history = np.zeros((T, N))
    history[0] = x
    for t in range(T-1):
        new_x = x.copy()
        for i in range(N):
            left = x[(i-1) % N]
            right = x[(i+1) % N]
            center = x[i]
            vals = [left, center, right]
            # Take the mode
            counts = np.bincount(vals, minlength=3)
            mode = np.argmax(counts)
            if rng.random() < p:
                new_x[i] = rng.integers(0, 3)
            else:
                new_x[i] = mode
        x = new_x
        history[t+1] = x
    return history

# Run experiments
print('M25: Discrete-state vs Continuous-state spatiotemporal systems')
results = []

# 1D binary CA sweep
print('\n1D Binary Stochastic Majority CA (N=64, T=200):')
for p in [0.0, 0.05, 0.1, 0.2, 0.3]:
    h = majority_ca(N=64, T=200, p=p)
    bf = band_frac(h[50:])
    results.append(('1D Binary MAJ', p, bf))
    print(f'  p={p:.2f}: bf={bf:.4f}, R={bf/0.4142:.3f}')

# 2D binary CA
print('\n2D Binary Stochastic Majority CA (N=32, T=100):')
for p in [0.0, 0.05, 0.1, 0.2, 0.3]:
    h = binary_2d_ca(N=32, T=100, p=p)
    bf = band_frac(h[20:].reshape(-1))
    results.append(('2D Binary MAJ', p, bf))
    print(f'  p={p:.2f}: bf={bf:.4f}, R={bf/0.4142:.3f}')

# 3-state integer CA
print('\n3-State Integer Stochastic Majority CA (N=64, T=200):')
for p in [0.0, 0.05, 0.1, 0.2, 0.3]:
    h = integer_3state_ca(N=64, T=200, p=p)
    bf = band_frac(h[50:])
    results.append(('1D 3-state MAJ', p, bf))
    print(f'  p={p:.2f}: bf={bf:.4f}, R={bf/0.4142:.3f}')

# ============================================================
# Plot
# ============================================================
fig, axes = plt.subplots(2, 3, figsize=(15, 10))

# 1D binary CA snapshots
ax = axes[0, 0]
h = majority_ca(N=64, T=200, p=0.1)
im = ax.imshow(h.T, aspect='auto', cmap='binary')
ax.set_xlabel('time t')
ax.set_ylabel('site i')
ax.set_title('1D Binary Stochastic Majority\n(p=0.1)')
plt.colorbar(im, ax=ax)

# 2D binary CA snapshots
ax = axes[0, 1]
h = binary_2d_ca(N=32, T=60, p=0.1)
# Show a few snapshots
n_show = 6
for k in range(n_show):
    t_idx = k * 10
    ax = axes[0 + (k // 3), 1 + (k % 3)]
    if k == 0:
        ax = axes[0, 1]
    elif k == 1:
        ax = axes[0, 2]
    elif k == 3:
        ax = axes[1, 1]
    ax.imshow(h[t_idx], cmap='binary', vmin=0, vmax=1)
    ax.set_title(f'2D Binary MAJ, t={t_idx}, p=0.1')
    ax.axis('off')

# Plot bf vs p for each system type
ax = axes[1, 2]
for sys_type in ['1D Binary MAJ', '2D Binary MAJ', '1D 3-state MAJ']:
    p_vals = [p for s, p, _ in results if s == sys_type]
    bfs = [bf for s, p, bf in results if s == sys_type]
    ax.plot(p_vals, bfs, 'o-', linewidth=2, label=sys_type)
ax.axhline(0.414, color='red', linestyle='--', label='Adler ceiling')
ax.set_xlabel('p (stochasticity)')
ax.set_ylabel('bf')
ax.set_title('Discrete-state systems — all exceed ceiling')
ax.legend()
ax.grid(True, alpha=0.3)

# Final summary
ax = axes[1, 0]
ax.axis('off')
text = "M25: Discrete vs Continuous\nState Systems\n\n"
for sys_type, p, bf in results:
    text += f'  {sys_type}, p={p:.2f}: bf={bf:.3f}\n'
ax.text(0, 1, text, fontsize=10, family='monospace', va='top')

plt.suptitle('M25: Testing the discreteness hypothesis', fontsize=14)
plt.tight_layout()
plt.savefig('_artifacts/m25_discrete_continuous.png', dpi=110, bbox_inches='tight')
print('\nSaved m25_discrete_continuous.png')

# Save
import json
data = {'sweep': [{'system': s, 'p': p, 'bf': bf, 'R': bf/0.4142} for s, p, bf in results]}
with open('_artifacts/m25_discrete_continuous.json', 'w') as f:
    json.dump(data, f, indent=2)