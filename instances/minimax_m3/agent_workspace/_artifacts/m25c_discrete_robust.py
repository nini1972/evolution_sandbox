"""M25c: Fixed - use properly chaotic discrete systems."""
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
# Use a chaotic binary CA (Rule 90 with binary noise)
# ============================================================
def rule90_ca(N=64, T=300, seed=42):
    """Rule 90: x_i(t+1) = x_{i-1}(t) XOR x_{i+1}(t)."""
    rng = np.random.default_rng(seed)
    x = rng.integers(0, 2, size=N).astype(np.uint8)
    history = np.zeros((T, N), dtype=np.uint8)
    history[0] = x
    for t in range(T-1):
        left = np.roll(x, 1)
        right = np.roll(x, -1)
        x = left ^ right
        history[t+1] = x
    return history.astype(float)

# ============================================================
# Binary CA with strong external forcing
# ============================================================
def forced_binary_ca(N=64, T=300, p_flip=0.5, seed=42):
    """Each cell randomly flips with prob p_flip, but with local coupling."""
    rng = np.random.default_rng(seed)
    x = rng.integers(0, 2, size=N).astype(np.uint8)
    history = np.zeros((T, N), dtype=np.uint8)
    history[0] = x
    for t in range(T-1):
        # Local rule: new state = majority of neighbors with prob p_flip
        new_x = x.copy()
        for i in range(N):
            left = x[(i-1) % N]
            right = x[(i+1) % N]
            center = x[i]
            majority = 1 if (left + center + right) >= 1.5 else 0
            if rng.random() < p_flip:
                new_x[i] = majority
            else:
                new_x[i] = 1 - majority
        x = new_x
        history[t+1] = x
    return history.astype(float)

# ============================================================
# Use XYS-Style: Binary state with conservative dynamics (sum mod 2)
# ============================================================
def xor_ca_fixed(N=64, T=300, noise=0.05, seed=42):
    """XOR rule with noise: new_x[i] = x[i] XOR (x[i-1] XOR x[i+1])."""
    rng = np.random.default_rng(seed)
    x = rng.integers(0, 2, size=N).astype(np.uint8)
    history = np.zeros((T, N), dtype=np.uint8)
    history[0] = x
    for t in range(T-1):
        new_x = x.copy()
        for i in range(N):
            left = np.uint8(x[(i-1) % N])
            right = np.uint8(x[(i+1) % N])
            center = np.uint8(x[i])
            new_x[i] = center ^ (left ^ right)
            if rng.random() < noise:
                new_x[i] = new_x[i] ^ np.uint8(1)
        x = new_x
        history[t+1] = x
    return history.astype(float)

# ============================================================
# Run experiments
# ============================================================
results = []

print('Rule 90 (Linear) CA (N=64, T=300):')
h = rule90_ca(N=64, T=300)
bf = band_frac(h[50:])
results.append(('Rule 90', 0, bf))
print(f'  bf={bf:.4f}, R={bf/0.4142:.3f}')

print('\nForced Binary Stochastic Majority CA (N=64, T=300):')
for pf in [0.1, 0.3, 0.5, 0.7, 0.9]:
    h = forced_binary_ca(N=64, T=300, p_flip=pf)
    bf = band_frac(h[50:])
    results.append(('Forced Bin MAJ', pf, bf))
    print(f'  p_flip={pf:.2f}: bf={bf:.4f}, R={bf/0.4142:.3f}')

print('\nXOR Rule 90 CA with Noise (N=64, T=300):')
for n in [0.0, 0.05, 0.1, 0.2, 0.3]:
    h = xor_ca_fixed(N=64, T=300, noise=n)
    bf = band_frac(h[50:])
    results.append(('XOR Rule 90', n, bf))
    print(f'  noise={n:.2f}: bf={bf:.4f}, R={bf/0.4142:.3f}')

# ============================================================
# Plot
# ============================================================
fig, axes = plt.subplots(3, 3, figsize=(15, 13))

# Rule 90
ax = axes[0, 0]
h = rule90_ca(N=64, T=200)
im = ax.imshow(h.T, aspect='auto', cmap='binary')
ax.set_title(f'Rule 90 (pure XOR)\nbf={band_frac(h[50:]):.3f}')
ax.set_xlabel('time t')
ax.set_ylabel('site i')

# Forced binary MAJ
for k, pf in enumerate([0.3, 0.5, 0.7]):
    ax = axes[0, k+1]
    h = forced_binary_ca(N=64, T=200, p_flip=pf)
    im = ax.imshow(h.T, aspect='auto', cmap='binary')
    ax.set_title(f'Forced Bin MAJ, p={pf}\nbf={band_frac(h[50:]):.3f}')
    ax.set_xlabel('time t')
    ax.set_ylabel('site i')

# XOR rule 90 with noise
for k, n in enumerate([0.05, 0.1, 0.2]):
    ax = axes[1, k]
    h = xor_ca_fixed(N=64, T=200, noise=n)
    im = ax.imshow(h.T, aspect='auto', cmap='binary')
    ax.set_title(f'XOR Rule 90, noise={n}\nbf={band_frac(h[50:]):.3f}')
    ax.set_xlabel('time t')
    ax.set_ylabel('site i')

# bf vs noise
ax = axes[2, 0]
for sys_type in ['XOR Rule 90']:
    xs = [p for s, p, _ in results if s == sys_type]
    ys = [bf for s, p, bf in results if s == sys_type]
    ax.plot(xs, ys, 'o-', linewidth=2, label=sys_type)
ax.axhline(0.414, color='red', linestyle='--', label='Adler ceiling')
ax.set_xlabel('noise')
ax.set_ylabel('bf')
ax.set_title('XOR Rule 90: bf vs noise')
ax.legend()
ax.grid(True, alpha=0.3)

# Forced MAJ bf vs p
ax = axes[2, 1]
xs = [p for s, p, _ in results if s == 'Forced Bin MAJ']
ys = [bf for s, p, bf in results if s == 'Forced Bin MAJ']
ax.plot(xs, ys, 'o-', linewidth=2, color='purple')
ax.axhline(0.414, color='red', linestyle='--')
ax.set_xlabel('p_flip')
ax.set_ylabel('bf')
ax.set_title('Forced Binary MAJ: bf vs p')
ax.grid(True, alpha=0.3)

# Summary
ax = axes[2, 2]
ax.axis('off')
text = "M25c: Robust Discrete Systems\n\n"
for sys_type, p, bf in results:
    text += f'  {sys_type}, p={p:.2f}: bf={bf:.3f}\n'
text += f'\nC=316/763={0.4142:.4f}'
ax.text(0, 1, text, fontsize=9, family='monospace', va='top')

plt.suptitle('M25c: Properly chaotic discrete systems', fontsize=14)
plt.tight_layout()
plt.savefig('_artifacts/m25c_discrete_robust.png', dpi=110, bbox_inches='tight')
print('\nSaved m25c_discrete_robust.png')

import json
data = {'sweep': [{'system': s, 'param': p, 'bf': bf, 'R': bf/0.4142} for s, p, bf in results]}
with open('_artifacts/m25c_discrete_robust.json', 'w') as f:
    json.dump(data, f, indent=2)