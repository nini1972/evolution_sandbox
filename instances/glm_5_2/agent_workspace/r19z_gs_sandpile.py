"""
R19Z Phase 3: Gray-Scott x Sandpile Resonance Experiment
Third resonance pair: continuous PDE (Gray-Scott) x discrete SOC (BTW sandpile)
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
from scipy.optimize import curve_fit

np.random.seed(42)

# === Gray-Scott Reaction-Diffusion (2D) ===
class GrayScott:
    def __init__(self, size=32, Du=0.16, Dv=0.08, feed=0.035, kill=0.065):
        self.size = size
        self.Du = Du
        self.Dv = Dv
        self.feed = feed
        self.kill = kill
        self.u = np.ones((size, size))
        self.v = np.zeros((size, size))
        r = size // 8
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

# === BTW Sandpile (2D) ===
class BTWSandpile:
    def __init__(self, size=16, threshold_mean=4.0, threshold_std=0.5):
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
        for _ in range(500):
            unstable = np.where(self.heights >= self.thresholds)
            if len(unstable[0]) == 0:
                break
            total += len(unstable[0])
            for x, y in zip(*unstable):
                self.heights[x, y] -= self.thresholds[x, y]
                for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < self.size and 0 <= ny < self.size:
                        self.heights[nx, ny] += 1
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
def cross_correlation(x, y, max_lag=50):
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
def run_coupled(N_gap=1, coupling=0.5, n_steps=400,
                forcing_amp=0.0, forcing_freq=0.1,
                gs_size=32, sp_size=16):
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

# === EXPERIMENT 1: Resonance Gap Law test ===
print('=== Experiment 1: Resonance Gap Law Test ===')
gaps = [1, 2, 5, 10, 20, 50]
gap_results = []

for N in gaps:
    print(f'  N_gap={N}...')
    corrs = []
    for seed in range(3):
        np.random.seed(seed * 17 + 42)
        result = run_coupled(N_gap=N, coupling=0.5, n_steps=400)
        lags, corr = cross_correlation(result['gs_v'][50:], result['sp_h'][50:], max_lag=80)
        peak = np.max(np.abs(corr))
        peak_lag = lags[np.argmax(np.abs(corr))]
        corrs.append((peak, peak_lag))
    mc = np.mean([c[0] for c in corrs])
    ml = np.mean([c[1] for c in corrs])
    sc = np.std([c[0] for c in corrs])
    gap_results.append({'N': N, 'C': float(mc), 'lag': float(ml), 'std': float(sc)})
    print(f'    C={mc:.3f}+/-{sc:.3f}, lag={ml:.1f}')

# Plot gap law
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
Ns = [r['N'] for r in gap_results]
Cs = [r['C'] for r in gap_results]
Cerrs = [r['std'] for r in gap_results]
lag_vals = [abs(r['lag']) for r in gap_results]

def resonance_law(N, C_max, tau):
    return C_max * (1 - np.exp(-N / tau))

try:
    popt, pcov = curve_fit(resonance_law, Ns, Cs, p0=[0.8, 10])
    N_fit = np.linspace(0.5, 60, 200)
    C_fit = resonance_law(N_fit, *popt)
    ax1.plot(N_fit, C_fit, 'r--', lw=2, alpha=0.7,
             label=f'Fit: C={popt[0]:.3f}x(1-exp(-N/{popt[1]:.1f}))')
    law_text = f'C_max={popt[0]:.3f}, tau={popt[1]:.1f}'
except Exception as e:
    law_text = f'Fit failed: {e}'
    popt = [0, 0]

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
print(f'  Law fit: {law_text}')

# === EXPERIMENT 2: Forcing and anti-resonance ===
print('\n=== Experiment 2: Forcing / Anti-Resonance ===')
forcing_amps = [0.0, 0.2, 0.5, 1.0, 2.0, 4.0]
force_results = []

for fa in forcing_amps:
    print(f'  forcing_amp={fa}...')
    corrs = []
    for seed in range(3):
        np.random.seed(seed * 17 + 42)
        result = run_coupled(N_gap=20, coupling=0.5, n_steps=400,
                             forcing_amp=fa, forcing_freq=0.1)
        lags, corr = cross_correlation(result['gs_v'][50:], result['sp_h'][50:], max_lag=80)
        # Track both max positive and max negative
        max_pos = np.max(corr)
        max_neg = np.min(corr)
        peak = np.max(np.abs(corr))
        peak_lag = lags[np.argmax(np.abs(corr))]
        corrs.append((peak, peak_lag, max_pos, max_neg))
    mc = np.mean([c[0] for c in corrs])
    mp = np.mean([c[2] for c in corrs])
    mn = np.mean([c[3] for c in corrs])
    force_results.append({'fa': fa, 'C': float(mc), 'C_pos': float(mp), 'C_neg': float(mn)})
    print(f'    |C|={mc:.3f}, C+={mp:.3f}, C-={mn:.3f}')

# Plot forcing results
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

# === EXPERIMENT 3: Time series at key points ===
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
    result = run_coupled(N_gap=ng, coupling=0.5, n_steps=300,
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
    'gap_law_fit': {'C_max': float(popt[0]), 'tau': float(popt[1]), 'text': law_text},
    'forcing_results': force_results,
    'comparison_to_kuramoto_sandpile': {
        'kuramoto_C_max': 0.793,
        'kuramoto_tau': 11.2,
        'gs_C_max': float(popt[0]),
        'gs_tau': float(popt[1])
    }
}
with open('r19z_gs_sandpile_data.json', 'w') as f:
    json.dump(output, f, indent=2)

print('\n=== Summary ===')
print(f'Resonance Gap Law: C = {popt[0]:.3f} x (1 - exp(-N/{popt[1]:.1f}))')
print(f'Kuramoto-Sandpile: C_max=0.793, tau=11.2')
print(f'Gray-Scott-Sandpile: C_max={popt[0]:.3f}, tau={popt[1]:.1f}')
print(f'\nAnti-resonance detected: {any(r["C_neg"] < -0.3 for r in force_results)}')
print('Done. Files saved.')
