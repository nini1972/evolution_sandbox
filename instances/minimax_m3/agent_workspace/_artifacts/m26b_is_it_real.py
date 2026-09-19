"""M26b: Critical control test - is high bf from rule dynamics or just from the Gaussian noise itself?"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def band_frac(arr, lo_frac=0.3, hi_frac=0.7):
    flat = arr.flatten()
    lo = flat.min() + lo_frac * (flat.max() - flat.min())
    hi = flat.min() + hi_frac * (flat.max() - flat.min())
    return ((flat >= lo) & (flat <= hi)).mean()

def pure_gaussian(N=128, T=300, sigma=0.3, seed=42):
    """Pure Gaussian noise (no dynamics, just sigma*randn at each step)."""
    rng = np.random.default_rng(seed)
    history = np.zeros((T, N))
    for t in range(T):
        history[t] = sigma * rng.normal(size=N)
    return history

def rule30_with_continuum(N=128, T=300, sigma=0.3, seed=42):
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

# Compare: same sigma, with vs without dynamics
print('M26b: Is high bf from Rule 30 dynamics or from Gaussian noise itself?')
print('='*60)

results = []
for sigma in [0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 1.0]:
    h_dyn = rule30_with_continuum(N=128, T=300, sigma=sigma)
    h_pure = pure_gaussian(N=128, T=300, sigma=sigma)
    bf_dyn = band_frac(h_dyn[50:])
    bf_pure = band_frac(h_pure[50:])
    results.append((sigma, bf_dyn, bf_pure))
    print(f'σ={sigma:.2f}: Rule30+noise bf={bf_dyn:.4f}  vs  Pure Gaussian bf={bf_pure:.4f}')

# Theoretical expectation for pure Gaussian:
# If values are N(0, sigma), then [0.3*min, 0.7*min] would be... min ≈ -3σ, max ≈ +3σ
# So window = [0.3*(-3σ), 0.7*(-3σ)] = [-0.9σ, -2.1σ] if min is negative
# Wait, let's compute properly. For N(0,σ): P(|X| < 0.4σ) ≈ 2*0.155 = 0.31 (using Z=0.4)
# But our window depends on min/max. After finite N=128*T samples, min ≈ -3σ, max ≈ +3σ
# So window = [min+0.3*(max-min), min+0.7*(max-min)] = [min+0.3*6σ, min+0.7*6σ]
#   = [-3σ + 1.8σ, -3σ + 4.2σ] = [-1.2σ, +1.2σ]
# P(|X|<1.2σ) for N(0,σ) ≈ P(|Z|<1.2) = 0.7698

# So for PURE GAUSSIAN, expected bf ≈ 0.77, regardless of sigma.
# For Rule 30 + noise, if bf is higher than 0.77, it's the dynamics!

print('\nTheoretical pure Gaussian bf: ~0.77 (regardless of σ)')
print('So if Rule 30 + noise gives bf > 0.77, the dynamics are amplifying it.')

# Find crossovers
for sigma, bf_dyn, bf_pure in results:
    diff = bf_dyn - bf_pure
    print(f'  σ={sigma:.2f}: Δ(bf)={diff:+.4f}')

# Plot
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

ax = axes[0, 0]
sigmas = [r[0] for r in results]
bf_dyns = [r[1] for r in results]
bf_pures = [r[2] for r in results]
ax.plot(sigmas, bf_dyns, 'o-', linewidth=2, label='Rule 30 + noise')
ax.plot(sigmas, bf_pures, 's-', linewidth=2, label='Pure Gaussian (control)')
ax.axhline(0.414, color='red', linestyle='--', label='Adler ceiling')
ax.set_xlabel('σ')
ax.set_ylabel('bf')
ax.set_title('bf vs noise level')
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[0, 1]
h_dyn = rule30_with_continuum(N=128, T=200, sigma=0.3)
ax.imshow(h_dyn.T, aspect='auto', cmap='viridis')
ax.set_title('Rule 30 + σ=0.3\nbf=' + f'{band_frac(h_dyn[50:]):.3f}')

ax = axes[1, 0]
h_pure = pure_gaussian(N=128, T=200, sigma=0.3)
ax.imshow(h_pure.T, aspect='auto', cmap='viridis')
ax.set_title('Pure Gaussian σ=0.3\nbf=' + f'{band_frac(h_pure[50:]):.3f}')

ax = axes[1, 1]
ax.hist([h_dyn[100:].flatten(), h_pure[100:].flatten()],
        bins=30, label=['Rule 30 + σ=0.3', 'Pure Gaussian σ=0.3'])
ax.set_xlabel('value')
ax.set_ylabel('count')
ax.set_title('Distribution comparison')
ax.legend()
ax.set_yscale('log')

plt.suptitle('M26b: Critical control test — pure Gaussian vs Rule 30 + noise', fontsize=14)
plt.tight_layout()
plt.savefig('_artifacts/m26b_is_it_real.png', dpi=110, bbox_inches='tight')
print('\nSaved m26b_is_it_real.png')

import json
data = {'results': [{'sigma': s, 'bf_dyn': bd, 'bf_pure': bp} for s, bd, bp in results]}
with open('_artifacts/m26b_is_it_real.json', 'w') as f:
    json.dump(data, f, indent=2)