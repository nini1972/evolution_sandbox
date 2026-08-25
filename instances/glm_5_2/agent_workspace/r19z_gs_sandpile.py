"""
R19Z Phase 3: Gray-Scott x Sandpile Resonance Experiment
Optimized version with vectorized sandpile and reduced sizes.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

np.random.seed(42)

# === Gray-Scott Reaction-Diffusion (2D, small) ===
class GrayScott:
    def __init__(self, size=16, Du=0.16, Dv=0.08, feed=0.035, kill=0.065):
        self.size = size
        self.Du = Du
        self.Dv = Dv
        self.feed = feed
        self.kill = kill
        self.u = np.ones((size, size))
        self.v = np.zeros((size, size))
        r = max(2, size // 8)
        cx, cy = size // 2, size // 2
        self.u[cx-r:cx+r, cy-r:cy+r] = 0.50
        self.v[cx-r:cx+r, cy-r:cy+r] = 0.25
        self.u += np.random.randn(size, size) * 0.01
        self.v += np.random.randn(size, size) * 0.01
        self.u = np.clip(self.u, 0, 1)
        self.v = np.clip(self.v, 0, 1)

    def laplacian(self, field):
        lap = np.zeros_like(field)
        lap[1:-1, 1:-1] = (field[2:, 1:-1] + field[:-2, 1:-1] +
                          field[1:-1, 2:] + field[1:-1, :-2] -
                          4 * field[1:-1, 1:-1])
        lap[0, :] = lap[1, :]
        lap[-1, :] = lap[-2, :]
        lap[:, 0] = lap[:, 1]
        lap[:, -1] = lap[:, -2]
        return lap

    def step(self, dt=1.0, perturbation=None):
        du = self.Du * self.laplacian(self.u) - self.u * self.v**2 + self.feed * (1 - self.u)
        dv = self.Dv * self.laplacian(self.v) + self.u * self.v**2 - (self.feed + self.kill) * self.v
        if perturbation is not None:
            du += perturbation
        self.u += du * dt
        self.v += dv * dt
        self.u = np.clip(self.u, 0, 1)
        self.v = np.clip(self.v, 0, 1)

    def mean_v(self):
        return float(np.mean(self.v))

    def pattern_complexity(self):
        return float(np.var(self.v))

# === BTW Sandpile (small, vectorized relax) ===
class BTWSandpile:
    def __init__(self, size=8, threshold_mean=4.0, threshold_std=0.5):
        self.size = size
        self.thresholds = np.random.normal(threshold_mean, threshold_std, (size, size))
        self.thresholds = np.maximum(self.thresholds, 2.0)
        self.heights = np.random.uniform(0, 1, (size, size))
        self.avalanche_log = []

    def add_grain(self):
        x, y = np.random.randint(0, self.size, 2)
        self.heights[x, y] += 1

    def relax(self):
        total = 0
        for _ in range(50):
            mask = self.heights >= self.thresholds
            if not np.any(mask):
                break
            n_unstable = int(np.sum(mask))
            total += n_unstable
            # Topple all unstable simultaneously
            toppled = self.thresholds * mask
            self.heights -= toppled
            # Distribute to neighbors (vectorized with padding)
            padded = np.zeros((self.size + 2, self.size + 2))
            padded[1:-1, 1:-1] = toppled
            self.heights += padded[:-2, 1:-1]  # from left neighbor
            self.heights += padded[2:, 1:-1]   # from right neighbor
            self.heights += padded[1:-1, :-2]  # from top neighbor
            self.heights += padded[1:-1, 2:]   # from bottom neighbor
        return total

    def step(self, n_grains=1):
        for _ in range(n_grains):
            self.add_grain()
        av = self.relax()
        self.avalanche_log.append(av)
        return av

    def mean_height(self):
        return float(np.mean(self.heights))

# === Cross-correlation ===
def cross_correlation(x, y, max_lag=30):
    x = (x - np.mean(x)) / (np.std(x) + 1e-10)
    y = (y - np.mean(y)) / (np.std(y) + 1e-10)
    n = len(x)
    lags = np.arange(-max_lag, max_lag + 1)
    corr = np.zeros(len(lags))
    for i, lag in enumerate(lags):
        if lag < 0:
            corr[i] = np.mean(x[-lag:] * y[:n+lag]) if n+lag > 0 else 0
        elif lag > 0:
            corr[i] = np.mean(x[:n-lag] * y[lag:]) if n-lag > 0 else 0
        else:
            corr[i] = np.mean(x * y)
    return lags, corr

# === Coupled system runner ===
def run_coupled(N_gap=1, coupling=0.5, n_steps=150,
                forcing_amp=0.0, forcing_freq=0.1,
                gs_size=16, sp_size=8):
    gs = GrayScott(size=gs_size)
    sp = BTWSandpile(size=sp_size)
    gs_log, sp_log, av_log, forcing_log = [], [], [], []

    for t in range(n_steps):
        forcing = forcing_amp * np.sin(2 * np.pi * forcing_freq * t)
        forcing_log.append(forcing)

        for _ in range(N_gap):
            gs_cx = gs.pattern_complexity()
            threshold_mod = 1.0 + coupling * gs_cx * 0.5
            sp.thresholds *= 0.99
            sp.thresholds += 0.01 * threshold_mod
            sp.step(1)
            if abs(forcing * 0.5) > 0.01:
                n_extra = int(abs(forcing * 0.5) * 5)
                for _ in range(n_extra):
                    sp.add_grain()
                sp.relax()

        avalanche = sp.avalanche_log[-1] if sp.avalanche_log else 0
        av_norm = avalanche / (sp.size * sp.size + 1)
        gs_pert = coupling * av_norm * np.random.randn(gs.size, gs.size) * 0.01
        gs_pert += forcing * 0.01 * np.ones((gs.size, gs.size))
        gs.step(perturbation=gs_pert)

        gs_log.append(gs.mean_v())
        sp_log.append(sp.mean_height())
        av_log.append(avalanche)

    return {
        'gs_v': np.array(gs_log),
        'sp_h': np.array(sp_log),
        'avalanches': np.array(av_log),
        'forcing': np.array(forcing_log),
        'gs_obj': gs,
        'sp_obj': sp
    }

# === EXPERIMENT 1: Resonance Gap Law ===
print('=== Experiment 1: Resonance Gap Law ===')
gaps = [1, 5, 20, 50]
gap_results = []

for N in gaps:
    print(f'  N_gap={N}...')
    corrs = []
    for seed in range(2):
        np.random.seed(seed * 17 + 42)
        result = run_coupled(N_gap=N, coupling=0.5, n_steps=150)
        lags, corr = cross_correlation(result['gs_v'][30:], result['sp_h'][30:], max_lag=40)
        peak = float(np.max(np.abs(corr)))
        peak_lag = float(lags[np.argmax(np.abs(corr))])
        corrs.append((peak, peak_lag))
    mc = np.mean([c[0] for c in corrs])
    ml = np.mean([c[1] for c in corrs])
    sc = np.std([c[0] for c in corrs])
    gap_results.append({'N': N, 'C': float(mc), 'lag': float(ml), 'std': float(sc)})
    print(f'    C={mc:.3f}+/-{sc:.3f}, lag={ml:.1f}')

# Fit resonance law manually (simple grid search since no scipy)
def resonance_law(N, C_max, tau):
    return C_max * (1 - np.exp(-N / tau))

best_err = 1e10
best_params = [0, 0]
for cmax in np.arange(0.1, 1.0, 0.05):
    for tau in np.arange(1, 30, 0.5):
        pred = [resonance_law(n, cmax, tau) for n in gaps]
        err = np.sum((np.array(pred) - np.array([r['C'] for r in gap_results]))**2)
        if err < best_err:
            best_err = err
            best_params = [cmax, tau]

law_text = f'C_max={best_params[0]:.3f}, tau={best_params[1]:.1f}'

# Plot gap law
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
Ns = [r['N'] for r in gap_results]
Cs = [r['C'] for r in gap_results]
Cerrs = [r['std'] for r in gap_results]
lag_vals = [abs(r['lag']) for r in gap_results]

N_fit = np.linspace(0.5, 60, 200)
C_fit = resonance_law(N_fit, *best_params)
ax1.plot(N_fit, C_fit, 'r--', lw=2, alpha=0.7,
         label=f'Fit: C={best_params[0]:.3f}x(1-exp(-N/{best_params[1]:.1f}))')
ax1.errorbar(Ns, Cs, yerr=Cerrs, fmt='bo-', capsize=5, ms=8, lw=2, label='Data')
ax1.set_xlabel('Timescale Gap (N)', fontsize=14)
ax1.set_ylabel('Peak Cross-Correlation |C|', fontsize=14)
ax1.set_title('Gray-Scott x Sandpile: Resonance Gap Law', fontsize=14)
ax1.legend(fontsize=11)
ax1.set_ylim(0, 1.0)
ax1.grid(True, alpha=0.3)

ax2.plot(Ns, lag_vals, 'gs-', ms=8, lw=2)
ax2.set_xlabel('Timescale Gap (N)', fontsize=14)
ax2.set_ylabel('Peak Lag (time steps)', fontsize=14)
ax2.set_title('Feedback Delay vs Gap', fontsize=14)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('r19z_gs_sandpile_gap_law.png', dpi=150, bbox_inches='tight')
plt.close()
print(f'  Law: {law_text}')

# === EXPERIMENT 2: Forcing and anti-resonance ===
print('\n=== Experiment 2: Forcing / Anti-Resonance ===')
forcing_amps = [0.0, 0.5, 2.0, 4.0]
force_results = []

for fa in forcing_amps:
    print(f'  forcing_amp={fa}...')
    corrs = []
    for seed in range(2):
        np.random.seed(seed * 17 + 42)
        result = run_coupled(N_gap=20, coupling=0.5, n_steps=150,
                             forcing_amp=fa, forcing_freq=0.1)
        lags, corr = cross_correlation(result['gs_v'][30:], result['sp_h'][30:], max_lag=40)
        max_pos = float(np.max(corr))
        max_neg = float(np.min(corr))
        peak = float(np.max(np.abs(corr)))
        corrs.append((peak, max_pos, max_neg))
    mc = np.mean([c[0] for c in corrs])
    mp = np.mean([c[1] for c in corrs])
    mn = np.mean([c[2] for c in corrs])
    force_results.append({'fa': fa, 'C': float(mc), 'C_pos': float(mp), 'C_neg': float(mn)})
    print(f'    |C|={mc:.3f}, C+={mp:.3f}, C-={mn:.3f}')

fig, ax = plt.subplots(figsize=(10, 7))
fas = [r['fa'] for r in force_results]
cs = [r['C'] for r in force_results]
cpos = [r['C_pos'] for r in force_results]
cneg = [r['C_neg'] for r in force_results]

ax.plot(fas, cs, 'ko-', ms=10, lw=2, label='|C| (absolute)')
ax.plot(fas, cpos, 'b^-', ms=10, lw=2, label='C+ (positive resonance)')
ax.plot(fas, cneg, 'rs-', ms=10, lw=2, label='C- (anti-resonance)')
ax.axhline(y=0, color='gray', ls='--', alpha=0.5)
ax.set_xlabel('Forcing Amplitude A', fontsize=14)
ax.set_ylabel('Cross-Correlation C', fontsize=14)
ax.set_title('Gray-Scott x Sandpile: Forcing Resonance Landscape', fontsize=14)
ax.legend(fontsize=12)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('r19z_gs_sandpile_forcing.png', dpi=150, bbox_inches='tight')
plt.close()

# === EXPERIMENT 3: Time series ===
print('\n=== Experiment 3: Time Series ===')
fig, axes = plt.subplots(2, 2, figsize=(16, 10))
configs = [
    (1, 0.0, 'N=1, A=0 (no gap, no forcing)'),
    (20, 0.0, 'N=20, A=0 (gap, no forcing)'),
    (20, 1.0, 'N=20, A=1.0 (gap + forcing)'),
    (20, 4.0, 'N=20, A=4.0 (gap + strong forcing)')
]
for ax, (ng, fa, title) in zip(axes.flat, configs):
    np.random.seed(42)
    result = run_coupled(N_gap=ng, coupling=0.5, n_steps=150,
                         forcing_amp=fa, forcing_freq=0.1)
    t = np.arange(len(result['gs_v']))
    ax.plot(t, result['gs_v'] / (np.max(result['gs_v']) + 1e-10), 'b-', lw=1.5, label='GS mean_v')
    ax.plot(t, result['sp_h'] / (np.max(result['sp_h']) + 1e-10), 'r-', lw=1.5, label='SP mean_h')
    if fa > 0:
        ax.plot(t, result['forcing'] / (np.max(np.abs(result['forcing'])) + 1e-10), 'g--', lw=1, alpha=0.5, label='Forcing')
    ax.set_title(title, fontsize=12)
    ax.set_xlabel('Time step')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig('r19z_gs_sandpile_timeseries.png', dpi=150, bbox_inches='tight')
plt.close()

# === Save data ===
output = {
    'experiment': 'Gray-Scott x Sandpile resonance',
    'gap_law_results': gap_results,
    'gap_law_fit': {'C_max': float(best_params[0]), 'tau': float(best_params[1]), 'text': law_text},
    'forcing_results': force_results,
    'comparison': {
        'kuramoto_C_max': 0.793,
        'kuramoto_tau': 11.2,
        'gs_C_max': float(best_params[0]),
        'gs_tau': float(best_params[1])
    }
}
with open('r19z_gs_sandpile_data.json', 'w') as f:
    json.dump(output, f, indent=2)

print('\n=== Summary ===')
print(f'Resonance Gap Law: C = {best_params[0]:.3f} x (1 - exp(-N/{best_params[1]:.1f}))')
print(f'Kuramoto-Sandpile: C_max=0.793, tau=11.2')
print(f'Gray-Scott-Sandpile: C_max={best_params[0]:.3f}, tau={best_params[1]:.1f}')
print(f'Anti-resonance detected: {any(r["C_neg"] < -0.3 for r in force_results)}')
print('Done. Files saved.')
