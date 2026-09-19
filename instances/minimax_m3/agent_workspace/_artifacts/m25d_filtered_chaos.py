"""M25d: Rule 90 deeper analysis - why bf=1.0? It's an artifact of binary state."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def band_frac(arr, lo_frac=0.3, hi_frac=0.7):
    flat = arr.flatten()
    lo = flat.min() + lo_frac * (flat.max() - flat.min())
    hi = flat.min() + hi_frac * (flat.max() - flat.min())
    return ((flat >= lo) & (flat <= hi)).mean()

def rule90_ca(N=128, T=300, seed=42):
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

def rule30_ca(N=128, T=300, seed=42):
    """Rule 30: x_i(t+1) = x[i-1] XOR (x[i] OR x[i+1])."""
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

def rule110_ca(N=128, T=300, seed=42):
    """Rule 110 - chaotic."""
    rng = np.random.default_rng(seed)
    x = rng.integers(0, 2, size=N).astype(np.uint8)
    history = np.zeros((T, N), dtype=np.uint8)
    history[0] = x
    for t in range(T-1):
        new_x = x.copy()
        for i in range(N):
            ll = np.uint8(x[(i-2) % N])
            l = np.uint8(x[(i-1) % N])
            c = np.uint8(x[i])
            r = np.uint8(x[(i+1) % N])
            # Rule 110 lookup
            rule_key = (ll << 4) | (l << 3) | (c << 2) | (r << 1) | np.uint8(x[(i+2) % N])
            new_x[i] = np.uint8(110 >> rule_key) & np.uint8(1)
        x = new_x
        history[t+1] = x
    return history.astype(float)

# Better measure: count fraction of "1" cells
def density(arr):
    return arr.mean()

# Density of 1s over time = "1-density"
# bf in binary case is meaningless - need to use a different metric
# Let's use: 4 * p(1) * (1 - p(1)) as variance-like measure, or just p(1)

# ============================================================
# Run experiments
# ============================================================
print('Rule 90, Rule 30, Rule 110 analysis')
print('='*60)

results = []

for label, ca_fn in [('Rule 90', rule90_ca), ('Rule 30', rule30_ca), ('Rule 110', rule110_ca)]:
    h = ca_fn(N=128, T=300)
    bf = band_frac(h[50:])
    density_val = density(h[50:])
    # 1-cells fraction
    f1 = (h[50:] == 1).mean()
    f0 = (h[50:] == 0).mean()
    print(f'\n{label}:')
    print(f'  density(mean) = {density_val:.4f}')
    print(f'  f(0) = {f0:.4f}, f(1) = {f1:.4f}')
    print(f'  bf = {bf:.4f} (NaN for binary - artifact)')
    print(f'  4*p0*p1 (chaos proxy) = {4*f0*f1:.4f}')
    # This is the actual "complexity" proxy: 4 * p * (1-p)
    chaos_metric = 4 * f0 * f1
    results.append((label, chaos_metric, f0, f1))

print('\n' + '='*60)
print('For binary systems, the bf metric is degenerate.')
print('Better metric: 4 * p(0) * p(1) - peaks at p=0.5, max=1.0.')
print('This measures "disorder" = max at perfectly balanced system.')

# Plot
fig, axes = plt.subplots(2, 3, figsize=(15, 9))
for k, (label, ca_fn) in enumerate([('Rule 90', rule90_ca), ('Rule 30', rule30_ca), ('Rule 110', rule110_ca)]):
    ax = axes[0, k]
    h = ca_fn(N=128, T=200)
    im = ax.imshow(h.T, aspect='auto', cmap='binary')
    chaos = 4 * (h[50:] == 0).mean() * (h[50:] == 1).mean()
    ax.set_title(f'{label}, chaos proxy={chaos:.3f}')
    ax.set_xlabel('time t')
    ax.set_ylabel('site i')

# Density vs time for each
for k, (label, ca_fn) in enumerate([('Rule 90', rule90_ca), ('Rule 30', rule30_ca), ('Rule 110', rule110_ca)]):
    ax = axes[1, k]
    h = ca_fn(N=128, T=300)
    d_t = h.mean(axis=1)
    ax.plot(d_t, linewidth=1.5)
    ax.axhline(0.5, color='red', linestyle='--', alpha=0.5, label='balanced')
    ax.set_xlabel('time t')
    ax.set_ylabel('density of 1s')
    ax.set_title(f'{label}: density vs time')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-0.05, 1.05)

plt.suptitle('M25d: Binary chaos — proper metric is 4*p0*p1, not bf', fontsize=14)
plt.tight_layout()
plt.savefig('_artifacts/m25d_filtered_chaos.png', dpi=110, bbox_inches='tight')
print('\nSaved m25d_filtered_chaos.png')

import json
data = {'results': [{'system': l, 'chaos_metric': c, 'f0': f0, 'f1': f1}
                     for l, c, f0, f1 in results]}
with open('_artifacts/m25d_filtered_chaos.json', 'w') as f:
    json.dump(data, f, indent=2)