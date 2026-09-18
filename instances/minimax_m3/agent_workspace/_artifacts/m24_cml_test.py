"""M24: Coupled Map Lattice — bridging discrete chaos and spatiotemporal systems."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def band_frac(arr, lo_frac=0.3, hi_frac=0.7):
    """bf for 2D array: treat all values together."""
    flat = arr.flatten()
    lo = flat.min() + lo_frac * (flat.max() - flat.min())
    hi = flat.min() + hi_frac * (flat.max() - flat.min())
    return ((flat >= lo) & (flat <= hi)).mean()

def coupled_logistic_lattice(N=64, T=300, eps=0.4, r=3.9, x0_center=0.5):
    """Coupled logistic lattice with nearest-neighbor diffusive coupling.
    x_i(t+1) = (1-eps)*f(x_i(t)) + (eps/2)*(f(x_{i-1}(t)) + f(x_{i+1}(t)))
    Periodic BCs.
    """
    f = lambda x: r * x * (1 - x)
    x = np.zeros((T, N))
    # Initial condition: small perturbation
    x[0] = x0_center + 0.01 * np.random.randn(N)
    x[0] = np.clip(x[0], 0, 1)

    for t in range(T-1):
        f_curr = f(x[t])
        # Periodic shift
        f_left = np.roll(f_curr, 1)
        f_right = np.roll(f_curr, -1)
        x[t+1] = (1 - eps) * f_curr + (eps/2) * (f_left + f_right)
    return x

# Test multiple (eps, r) combinations
print('Coupled logistic lattice sweep (N=64, T=300):')
results = []
np.random.seed(42)
for r in [3.5, 3.7, 3.9, 4.0]:
    for eps in [0.0, 0.1, 0.3, 0.5, 0.7]:
        x = coupled_logistic_lattice(N=64, T=300, eps=eps, r=r)
        bf = band_frac(x[100:])  # discard transient
        results.append((eps, r, bf))
        print(f'  eps={eps:.2f}, r={r:.2f}: bf={bf:.4f}, R={bf/0.4142:.3f}')

# Plot
fig, axes = plt.subplots(2, 3, figsize=(15, 10))

# Show example lattice
ax = axes[0, 0]
x = coupled_logistic_lattice(N=64, T=200, eps=0.4, r=3.9)
im = ax.imshow(x.T, aspect='auto', cmap='viridis')
ax.set_xlabel('time t')
ax.set_ylabel('site i')
ax.set_title(f'CML snapshot\neps=0.4, r=3.9')
plt.colorbar(im, ax=ax)

# Sweep heatmap
ax = axes[0, 1]
r_vals = sorted(set(r for _, r, _ in results))
eps_vals = sorted(set(e for e, _, _ in results))
bf_grid = np.zeros((len(r_vals), len(eps_vals)))
for eps, r, bf in results:
    i = r_vals.index(r)
    j = eps_vals.index(eps)
    bf_grid[i, j] = bf
im = ax.imshow(bf_grid, aspect='auto', cmap='RdYlBu_r',
               extent=[-0.5, len(eps_vals)-0.5, -0.5, len(r_vals)-0.5])
ax.set_xticks(range(len(eps_vals)))
ax.set_xticklabels([f'{e:.2f}' for e in eps_vals])
ax.set_yticks(range(len(r_vals)))
ax.set_yticklabels([f'{r:.2f}' for r in r_vals])
ax.set_xlabel('eps (coupling)')
ax.set_ylabel('r (logistic parameter)')
ax.set_title('bf map across (eps, r)')
plt.colorbar(im, ax=ax)

# bf vs eps for different r
ax = axes[0, 2]
for r in r_vals:
    bfs = [bf for e, rr, bf in results if rr == r]
    ax.plot(eps_vals, bfs, 'o-', linewidth=2, label=f'r={r}')
ax.axhline(0.414, color='red', linestyle='--', label='Adler ceiling')
ax.axhline(0.4, color='gray', linestyle=':', label='uniform (0.4)')
ax.set_xlabel('eps (coupling)')
ax.set_ylabel('bf')
ax.set_title('bf vs coupling strength')
ax.legend()
ax.grid(True, alpha=0.3)

# Marginal distribution example
ax = axes[1, 0]
x = coupled_logistic_lattice(N=64, T=300, eps=0.4, r=3.9)
ax.hist(x[100:].flatten(), bins=50, density=True, alpha=0.7)
lo = x[100:].min(); hi = x[100:].max()
ax.axvspan(lo + 0.3*(hi-lo), lo + 0.7*(hi-lo), alpha=0.2, color='red', label='middle band')
ax.set_xlabel('x value')
ax.set_ylabel('density')
ax.set_title(f'Marginal distribution (eps=0.4, r=3.9)')
ax.legend()

# Power spectrum
ax = axes[1, 1]
x = coupled_logistic_lattice(N=64, T=300, eps=0.4, r=3.9)
# Average over space
mean_field = x[100:].mean(axis=1)
fft_vals = np.abs(np.fft.fft(mean_field - mean_field.mean()))**2
freq = np.fft.fftfreq(len(fft_vals))
pos = freq > 0
ax.loglog(freq[pos], fft_vals[pos])
ax.set_xlabel('frequency')
ax.set_ylabel('power')
ax.set_title('Power spectrum of mean field')

# Final summary
ax = axes[1, 2]
ax.axis('off')
text = """M24: Coupled Map Lattice

bf values at (eps, r):
"""
for eps, r, bf in results[:12]:
    text += f'  eps={eps:.2f}, r={r:.2f}: bf={bf:.3f}\n'
ax.text(0, 1, text, fontsize=9, family='monospace', va='top')

plt.suptitle('M24: Coupled Map Lattice — Bridging Discrete and Spatiotemporal',
             fontsize=14, y=1.00)
plt.tight_layout()
plt.savefig('_artifacts/m24_cml.png', dpi=110, bbox_inches='tight')
print('\nSaved m24_cml.png')

# Save data
import json
data = {
    'sweep': [{'eps': e, 'r': r, 'bf': bf, 'R': bf/0.4142} for e, r, bf in results]
}
with open('_artifacts/m24_cml.json', 'w') as f:
    json.dump(data, f, indent=2)