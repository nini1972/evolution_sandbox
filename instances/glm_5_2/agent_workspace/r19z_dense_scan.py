"""R19Z Phase 9: Dense f-scan + internal dynamics correlation.

The fine scan revealed that the resonance sign ALTERNATES as f increases,
not just flipping once. This is a resonance ARCHIPELAGO - alternating
sign bands. We need:
1. Denser f-scan (every 0.001) to map the band structure
2. Simultaneous uncoupled GS dynamics to identify the mechanism
3. Multi-seed robustness check at key points
"""
import numpy as np, json, time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ---- GS + Sandpile coupled system ----
def run_coupled(f_val, k=0.062, Du=0.16, Dv=0.08, size=12,
               n_steps=4000, N_gap=10, burn_in=800,
               gs_to_sp=0.3, sp_to_gs=0.005, seed=42):
    rng = np.random.RandomState(seed)
    u = np.ones((size, size)) * 0.5
    v = np.ones((size, size)) * 0.25
    u[size//2-2:size//2+2, size//2-2:size//2+2] = 0.25
    v[size//2-2:size//2+2, size//2-2:size//2+2] = 0.75
    grid = np.zeros((size, size))
    threshold_base = 4.0
    gs_signal = np.zeros(n_steps)
    sp_signal = np.zeros(n_steps)
    sp_act = np.zeros(n_steps)
    for t in range(burn_in + n_steps):
        ti = t - burn_in
        u_pad = np.pad(u, 1, mode='reflect')
        v_pad = np.pad(v, 1, mode='reflect')
        u_lap = (u_pad[:-2,1:-1] + u_pad[2:,1:-1] + u_pad[1:-1,:-2] + u_pad[1:-1,2:] - 4*u)
        v_lap = (v_pad[:-2,1:-1] + v_pad[2:,1:-1] + v_pad[1:-1,:-2] + v_pad[1:-1,2:] - 4*v)
        uv2 = u * v * v
        f_eff = f_val
        if t > 0 and t % N_gap == 0 and ti > 0:
            f_eff = f_val + sp_to_gs * sp_act[ti - 1]
        u = u + Du * u_lap - uv2 + f_eff * (1 - u)
        v = v + Dv * v_lap + uv2 - (f_eff + k) * v
        u = np.clip(u, 0, 1)
        v = np.clip(v, 0, 1)
        gs_complexity = np.std(v)
        if t % N_gap == 0:
            threshold = threshold_base + gs_to_sp * (gs_complexity - 0.1) * 10
            threshold = max(threshold, 1.0)
            i2, j2 = rng.randint(0, size, 2)
            grid[i2, j2] += 1
            avalanche = 0
            toppling = True
            while toppling:
                toppling = False
                for ii in range(size):
                    for jj in range(size):
                        if grid[ii, jj] >= threshold:
                            toppling = True
                            avalanche += 1
                            grid[ii, jj] -= 4
                            if ii > 0: grid[ii-1, jj] += 1
                            if ii < size-1: grid[ii+1, jj] += 1
                            if jj > 0: grid[ii, jj-1] += 1
                            if jj < size-1: grid[ii, jj+1] += 1
        else:
            avalanche = 0
        if ti >= 0:
            gs_signal[ti] = gs_complexity
            sp_signal[ti] = np.mean(grid)
            sp_act[ti] = avalanche
    max_lag = 200
    best_corr = 0
    best_lag = 0
    for lag in range(-max_lag, max_lag+1, 2):
        if lag < 0:
            a, b = gs_signal[:lag], sp_signal[-lag:]
        elif lag > 0:
            a, b = gs_signal[lag:], sp_signal[:-lag]
        else:
            a, b = gs_signal, sp_signal
        if np.std(a) > 1e-10 and np.std(b) > 1e-10:
            c = np.corrcoef(a, b)[0, 1]
            if abs(c) > abs(best_corr):
                best_corr = c
                best_lag = lag
    zero_lag = 0.0
    if np.std(gs_signal) > 1e-10 and np.std(sp_signal) > 1e-10:
        zero_lag = np.corrcoef(gs_signal, sp_signal)[0, 1]
    return {
        'f': float(f_val),
        'best_corr': float(best_corr),
        'best_lag': int(best_lag),
        'zero_lag': float(zero_lag),
        'sign': '+' if best_corr > 0 else '-',
        'gs_mean': float(np.mean(gs_signal)),
        'gs_std': float(np.std(gs_signal)),
        'sp_mean': float(np.mean(sp_signal)),
        'sp_std': float(np.std(sp_signal)),
    }

# ---- Uncoupled GS dynamics ----
def run_uncoupled_gs(f_val, k=0.062, Du=0.16, Dv=0.08, size=12,
                     n_steps=4000, burn_in=800, seed=42):
    u = np.ones((size, size)) * 0.5
    v = np.ones((size, size)) * 0.25
    u[size//2-2:size//2+2, size//2-2:size//2+2] = 0.25
    v[size//2-2:size//2+2, size//2-2:size//2+2] = 0.75
    complexity_ts = np.zeros(n_steps)
    v_mean_ts = np.zeros(n_steps)
    for t in range(burn_in + n_steps):
        ti = t - burn_in
        u_pad = np.pad(u, 1, mode='reflect')
        v_pad = np.pad(v, 1, mode='reflect')
        u_lap = (u_pad[:-2,1:-1] + u_pad[2:,1:-1] + u_pad[1:-1,:-2] + u_pad[1:-1,2:] - 4*u)
        v_lap = (v_pad[:-2,1:-1] + v_pad[2:,1:-1] + v_pad[1:-1,:-2] + v_pad[1:-1,2:] - 4*v)
        uv2 = u * v * v
        u = u + Du * u_lap - uv2 + f_val * (1 - u)
        v = v + Dv * v_lap + uv2 - (f_val + k) * v
        u = np.clip(u, 0, 1)
        v = np.clip(v, 0, 1)
        if ti >= 0:
            complexity_ts[ti] = np.std(v)
            v_mean_ts[ti] = np.mean(v)
    def acf(x, lag):
        if np.std(x) < 1e-12:
            return 1.0
        n = len(x)
        if lag >= n:
            return 0.0
        c = np.corrcoef(x[:n-lag], x[lag:])[0, 1]
        return float(c) if not np.isnan(c) else 0.0
    return {
        'f': float(f_val),
        'complexity_mean': float(np.mean(complexity_ts)),
        'complexity_std': float(np.std(complexity_ts)),
        'v_mean': float(np.mean(v_mean_ts)),
        'ac10': acf(complexity_ts, 10),
        'ac20': acf(complexity_ts, 20),
        'ac50': acf(complexity_ts, 50),
        'ac100': acf(complexity_ts, 100),
    }

# ---- Dense scan ----
f_values = np.arange(0.058, 0.092, 0.001)
print('Dense scan: %d f-values from %.3f to %.3f' % (len(f_values), f_values[0], f_values[-1]))

coupled_results = []
t0 = time.time()
for i, f in enumerate(f_values):
    r = run_coupled(f, n_steps=2500, N_gap=10, burn_in=500, seed=42)
    coupled_results.append(r)
    if (i+1) % 5 == 0 or i == 0:
        elapsed = time.time() - t0
        print('  f=%.3f: C=%+.4f sign=%s  gs_std=%.6f  [%d/%d] (%.1fs)' % (
            f, r['best_corr'], r['sign'], r['gs_std'], i+1, len(f_values), elapsed))

print('\nCoupled scan done in %.1fs' % (time.time()-t0))

uncoupled_results = []
t1 = time.time()
for i, f in enumerate(f_values):
    r = run_uncoupled_gs(f, n_steps=2500, burn_in=500, seed=42)
    uncoupled_results.append(r)
    if (i+1) % 5 == 0 or i == 0:
        elapsed = time.time() - t1
        print('  f=%.3f: ac50=%+.4f ac20=%+.4f comp=%.6f  [%d/%d] (%.1fs)' % (
            f, r['ac50'], r['ac20'], r['complexity_mean'], i+1, len(f_values), elapsed))

print('\nUncoupled scan done in %.1fs' % (time.time()-t1))

# Multi-seed robustness
print('\nMulti-seed robustness check...')
key_fs = [0.061, 0.065, 0.067, 0.069, 0.079, 0.083, 0.089]
multi_seed = {}
for f in key_fs:
    corrs = []
    signs = []
    for s in [42, 123, 7]:
        r = run_coupled(f, n_steps=2500, N_gap=10, burn_in=500, seed=s)
        corrs.append(r['best_corr'])
        signs.append(r['sign'])
    key = '%.3f' % f
    multi_seed[key] = {
        'corrs': corrs,
        'mean_corr': float(np.mean(corrs)),
        'std_corr': float(np.std(corrs)),
        'signs': signs,
        'dominant_sign': '+' if np.mean([1 if s == '+' else -1 for s in signs]) > 0 else '-',
    }
    print('  f=%.3f: mean_C=%+.4f +/- %.4f  signs=%s' % (f, np.mean(corrs), np.std(corrs), signs))

with open('r19z_dense_scan_data.json', 'w') as fp:
    json.dump({
        'f_values': [float(f) for f in f_values],
        'coupled': coupled_results,
        'uncoupled': uncoupled_results,
        'multi_seed': multi_seed,
    }, fp, indent=2)

print('\nData saved to r19z_dense_scan_data.json')

# ---- Visualization ----
fig, axes = plt.subplots(3, 2, figsize=(18, 14))

ax = axes[0, 0]
fs = [r['f'] for r in coupled_results]
cs = [r['best_corr'] for r in coupled_results]
colors = ['#27ae60' if c > 0 else '#c0392b' for c in cs]
ax.bar(range(len(fs)), cs, color=colors, alpha=0.8, width=0.8)
ax.axhline(y=0, color='black', linewidth=1)
ax.set_xticks(range(0, len(fs), 3))
ax.set_xticklabels(['%.3f' % f for f in fs[::3]], rotation=45, fontsize=8)
ax.set_xlabel('Feed rate f')
ax.set_ylabel('Best Cross-Correlation')
ax.set_title('Dense Scan: Coupled Correlation vs Feed Rate', fontsize=13, fontweight='bold')
ax.grid(axis='y', alpha=0.3)

ax = axes[0, 1]
ax.plot(fs, [abs(c) for c in cs], 'o-', color='#2d3561', markersize=4, linewidth=1.5)
ax.set_xlabel('Feed rate f')
ax.set_ylabel('|Cross-Correlation|')
ax.set_title('Resonance Strength vs Feed Rate', fontsize=13, fontweight='bold')
ax.grid(alpha=0.3)

ax = axes[1, 0]
ac50s = [r['ac50'] for r in uncoupled_results]
ac20s = [r['ac20'] for r in uncoupled_results]
ac100s = [r['ac100'] for r in uncoupled_results]
ax.plot(fs, ac50s, 'o-', label='ac(50)', color='#e74c3c', markersize=4)
ax.plot(fs, ac20s, 's-', label='ac(20)', color='#3498db', markersize=4)
ax.plot(fs, ac100s, '^-', label='ac(100)', color='#2ecc71', markersize=4)
ax.axhline(y=0, color='black', linewidth=1, linestyle='--')
ax.set_xlabel('Feed rate f')
ax.set_ylabel('Autocorrelation')
ax.set_title('Uncoupled GS Internal Dynamics', fontsize=13, fontweight='bold')
ax.legend(fontsize=9)
ax.grid(alpha=0.3)

ax = axes[1, 1]
ax2t = ax.twinx()
ax.bar(range(len(fs)), cs, color=colors, alpha=0.4, width=0.8)
ax2t.plot(range(len(fs)), ac50s, 'ko-', markersize=3, linewidth=1.5, label='ac(50)')
ax2t.axhline(y=0, color='gray', linewidth=1, linestyle='--')
ax.set_xlabel('Feed rate f (index)')
ax.set_ylabel('Coupled C', color='blue', fontsize=10)
ax2t.set_ylabel('Uncoupled ac(50)', color='black', fontsize=10)
ax2t.set_title('Overlay: Coupled Sign vs Internal ac(50)', fontsize=13, fontweight='bold')
ax2t.legend(fontsize=9)
ax.grid(alpha=0.2)

ax = axes[2, 0]
comps = [r['complexity_mean'] for r in uncoupled_results]
ax.plot(fs, comps, 'D-', color='#8e44ad', markersize=5, linewidth=2)
ax.set_xlabel('Feed rate f')
ax.set_ylabel('GS complexity (std v)')
ax.set_title('Uncoupled GS Complexity vs Feed Rate', fontsize=13, fontweight='bold')
ax.grid(alpha=0.3)

ax = axes[2, 1]
signs_numeric = [1 if c > 0 else -1 for c in cs]
ax.imshow([signs_numeric], aspect='auto', cmap='RdBu', vmin=-1, vmax=1)
ax.set_yticks([])
ax.set_xticks(range(0, len(fs), 3))
ax.set_xticklabels(['%.3f' % f for f in fs[::3]], rotation=45, fontsize=8)
ax.set_xlabel('Feed rate f')
ax.set_title('Sign Band Map (Red=anti-res, Blue=res)', fontsize=13, fontweight='bold')

plt.suptitle('R19Z Phase 9: Dense f-Scan - Resonance Archipelago\nGray-Scott x Sandpile - Internal Dynamics Control',
             fontsize=15, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('r19z_dense_scan.png', dpi=150, bbox_inches='tight')
plt.close()
print('Plot saved to r19z_dense_scan.png')

print('\n' + '='*60)
print('DENSE SCAN SUMMARY')
print('='*60)
pos_count = sum(1 for c in cs if c > 0)
neg_count = sum(1 for c in cs if c <= 0)
print('f range: %.3f to %.3f (%d points)' % (f_values[0], f_values[-1], len(f_values)))
print('Positive (resonance): %d  Negative (anti-resonance): %d' % (pos_count, neg_count))
transitions = 0
for i in range(1, len(signs_numeric)):
    if signs_numeric[i] != signs_numeric[i-1]:
        transitions += 1
        print('  Transition at f=%.3f (idx %d): %s -> %s' % (
            fs[i], i, '+' if signs_numeric[i-1] > 0 else '-', '+' if signs_numeric[i] > 0 else '-'))
print('Total sign transitions: %d' % transitions)
print('Done.')
