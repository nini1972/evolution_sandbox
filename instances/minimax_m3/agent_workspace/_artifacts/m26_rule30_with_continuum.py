"""M26: Embed binary chaos in continuous noise to test bf properly."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def band_frac(arr, lo_frac=0.3, hi_frac=0.7):
    flat = arr.flatten()
    lo = flat.min() + lo_frac * (flat.max() - flat.min())
    hi = flat.min() + hi_frac * (flat.max() - flat.min())
    return ((flat >= lo) & (flat <= hi)).mean()

def rule30_ca(N=128, T=300, seed=42):
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
            new_x[i] = left ^ (center | right)
        x = new_x
        history[t+1] = x
    return history.astype(float)

# Embed Rule 30 in continuous noise
def rule30_with_continuum(N=128, T=300, sigma=0.3, seed=42):
    """Rule 30 dynamics but each cell has continuous noise added."""
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
            binary_val = 1.0 if (left > 0.5) ^ ((center > 0.5) | (right > 0.5)) else 0.0
            new_x[i] = binary_val + sigma * rng.normal()
        x = new_x
        history[t+1] = x
    return history

# Continuous "stochastic Rule 30" - pure continuous
def stochastic_rule30_continuous(N=128, T=300, sigma=0.4, threshold=0.5, seed=42):
    """Continuous version: apply rule to sigmoid(x - threshold)."""
    rng = np.random.default_rng(seed)
    x = rng.uniform(-1, 1, size=N)
    history = np.zeros((T, N))
    history[0] = x
    for t in range(T-1):
        new_x = x.copy()
        for i in range(N):
            left = x[(i-1) % N]
            right = x[(i+1) % N]
            center = x[i]
            # Convert to binary decisions via thresholding
            l_b = 1 if left > threshold else 0
            r_b = 1 if right > threshold else 0
            c_b = 1 if center > threshold else 0
            new_x[i] = (l_b ^ (c_b | r_b)) * 2 - 1  # Map back to +/-1
            new_x[i] += sigma * rng.normal()
        x = new_x
        history[t+1] = x
    return history

# ============================================================
# Run experiments
# ============================================================
print('M26: Rule 30 with continuous embedding')
results = []

print('\nRule 30 (pure binary):')
h = rule30_ca(N=128, T=300)
bf = band_frac(h[50:])
f1 = (h[50:] == 1).mean()
results.append(('Rule 30 (binary)', 'N/A', bf, f1))
print(f'  bf={bf:.4f}, f(1)={f1:.4f}')

print('\nRule 30 + Gaussian noise (sigma):')
for sigma in [0.05, 0.1, 0.2, 0.3, 0.5]:
    h = rule30_with_continuum(N=128, T=300, sigma=sigma)
    bf = band_frac(h[50:])
    f1 = (h[50:] > 0.5).mean()
    results.append(('Rule 30 + noise', sigma, bf, f1))
    print(f'  sigma={sigma:.2f}: bf={bf:.4f}, f(>0.5)={f1:.4f}')

print('\nStochastic Rule 30 (continuous mapping +/-1):')
for sigma in [0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 1.0]:
    h = stochastic_rule30_continuous(N=128, T=300, sigma=sigma)
    bf = band_frac(h[50:])
    results.append(('Stoch Rule 30', sigma, bf, 0))
    print(f'  sigma={sigma:.2f}: bf={bf:.4f}')

# Plot
fig, axes = plt.subplots(3, 3, figsize=(15, 13))

# Row 0: binary rule 30
ax = axes[0, 0]
h = rule30_ca(N=128, T=200)
ax.imshow(h.T, aspect='auto', cmap='binary')
ax.set_title('Rule 30 (binary)\nbf undefined for binary')

# Row 0: rule 30 + sigma=0.1
ax = axes[0, 1]
h = rule30_with_continuum(N=128, T=200, sigma=0.1)
bf = band_frac(h[50:])
ax.imshow(h.T, aspect='auto', cmap='viridis')
ax.set_title(f'Rule 30 + noise σ=0.1\nbf={bf:.3f}')

# Row 0: rule 30 + sigma=0.3
ax = axes[0, 2]
h = rule30_with_continuum(N=128, T=200, sigma=0.3)
bf = band_frac(h[50:])
ax.imshow(h.T, aspect='auto', cmap='viridis')
ax.set_title(f'Rule 30 + noise σ=0.3\nbf={bf:.3f}')

# Row 1: stochastic rule 30 (continuous)
for k, sigma in enumerate([0.0, 0.1, 0.3]):
    ax = axes[1, k]
    h = stochastic_rule30_continuous(N=128, T=200, sigma=sigma)
    bf = band_frac(h[50:])
    ax.imshow(h.T, aspect='auto', cmap='RdBu', vmin=-1.5, vmax=1.5)
    ax.set_title(f'Stoch Rule 30 σ={sigma}\nbf={bf:.3f}')

# Row 2: bf vs sigma plots
ax = axes[2, 0]
xs = [r[1] for r in results if r[0] == 'Rule 30 + noise']
ys = [r[2] for r in results if r[0] == 'Rule 30 + noise']
ax.plot(xs, ys, 'o-', linewidth=2, label='Rule 30 + noise')
xs = [r[1] for r in results if r[0] == 'Stoch Rule 30']
ys = [r[2] for r in results if r[0] == 'Stoch Rule 30']
ax.plot(xs, ys, 's-', linewidth=2, label='Stoch Rule 30')
ax.axhline(0.414, color='red', linestyle='--', label='Adler ceiling')
ax.set_xlabel('sigma')
ax.set_ylabel('bf')
ax.set_title('bf vs noise level')
ax.legend()
ax.grid(True, alpha=0.3)

# Summary text
ax = axes[2, 1]
ax.axis('off')
text = "M26: Rule 30 with continuous noise\n\n"
text += "Pure binary Rule 30: bf undefined\n"
text += "(range is {0,1}, no continuum)\n\n"
text += "With Gaussian noise σ=0.1: bf=" + f"{results[1][2]:.3f}\n"
text += "With Gaussian noise σ=0.3: bf=" + f"{results[3][2]:.3f}\n\n"
text += "Note: bf requires continuous state!\n"
text += "Binary systems need different metric."
ax.text(0, 1, text, fontsize=10, family='monospace', va='top')

# histogram of values
ax = axes[2, 2]
h = rule30_with_continuum(N=128, T=300, sigma=0.2)
ax.hist(h[100:].flatten(), bins=50, edgecolor='black')
ax.set_xlabel('cell value')
ax.set_ylabel('count')
ax.set_title('Distribution: Rule 30 + σ=0.2')
ax.set_yscale('log')

plt.suptitle('M26: Embedding Rule 30 in continuous noise', fontsize=14)
plt.tight_layout()
plt.savefig('_artifacts/m26_rule30_with_continuum.png', dpi=110, bbox_inches='tight')
print('\nSaved m26_rule30_with_continuum.png')

import json
data = {'results': [{'system': s, 'param': p, 'bf': bf, 'extra': e} for s, p, bf, e in results]}
with open('_artifacts/m26_rule30_with_continuum.json', 'w') as f:
    json.dump(data, f, indent=2)