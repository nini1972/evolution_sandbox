"""
R19Z Multi-Seed Robustness Test on 48x48

The key question: Is the positive cross-correlation at f=0.064-0.072 
robust across multiple random seeds, or is it seed-dependent?

Also: Is the negative C at f=0.060 real or noise?
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

def run_gs_sandpile(f_val, k=0.062, Du=0.16, Dv=0.08, size=48,
                    n_steps=4000, N_gap=10, burn_in=2000,
                    gs_to_sp=2.0, sp_to_gs=0.02, seed=42):
    rng = np.random.RandomState(seed)
    u = np.ones((size, size)) * 0.5
    v = np.ones((size, size)) * 0.25
    u[size//2-4:size//2+4, size//2-4:size//2+4] = 0.25
    v[size//2-4:size//2+4, size//2-4:size//2+4] = 0.75
    sp_size = size // 4
    grid = np.zeros((sp_size, sp_size))
    threshold_base = 4.0
    gs_signal = np.zeros(n_steps)
    sp_signal = np.zeros(n_steps)
    sp_avalanche = np.zeros(n_steps)
    
    for t in range(burn_in + n_steps):
        ti = t - burn_in
        u_pad = np.pad(u, 1, mode='reflect')
        v_pad = np.pad(v, 1, mode='reflect')
        u_lap = (u_pad[:-2,1:-1] + u_pad[2:,1:-1] + u_pad[1:-1,:-2] + u_pad[1:-1,2:] - 4*u)
        v_lap = (v_pad[:-2,1:-1] + v_pad[2:,1:-1] + v_pad[1:-1,:-2] + v_pad[1:-1,2:] - 4*v)
        uv2 = u * v * v
        if t % N_gap == 0 and ti > 0:
            av = sp_avalanche[ti - 1]
            if av > 0:
                noise = rng.normal(0, sp_to_gs * np.sqrt(av), (size, size))
                u = u + noise
        u = u + Du * u_lap - uv2 + f_val * (1 - u)
        v = v + Dv * v_lap + uv2 - (f_val + k) * v
        u = np.clip(u, 0, 1)
        v = np.clip(v, 0, 1)
        gs_complexity = np.std(v)
        if t % N_gap == 0:
            threshold = max(threshold_base + gs_to_sp * gs_complexity, 1.5)
            i, j = rng.randint(0, sp_size, 2)
            grid[i, j] += 1
            avalanche = 0
            toppling = True
            max_iters = 1000
            while toppling and max_iters > 0:
                toppling = False
                above = np.where(grid >= threshold)
                for ii, jj in zip(above[0], above[1]):
                    toppling = True
                    avalanche += 1
                    grid[ii, jj] -= threshold
                    if ii > 0: grid[ii-1, jj] += 1
                    if ii < sp_size-1: grid[ii+1, jj] += 1
                    if jj > 0: grid[ii, jj-1] += 1
                    if jj < sp_size-1: grid[ii, jj+1] += 1
                max_iters -= 1
        else:
            avalanche = 0
        if ti >= 0:
            gs_signal[ti] = gs_complexity
            sp_signal[ti] = np.mean(grid)
            sp_avalanche[ti] = avalanche
    
    zero_lag = 0.0
    if np.std(gs_signal) > 1e-10 and np.std(sp_signal) > 1e-10:
        zero_lag = float(np.corrcoef(gs_signal, sp_signal)[0, 1])
    return {
        'f': float(f_val), 'zero_lag': zero_lag,
        'gs_std': float(np.std(gs_signal)),
        'sp_std': float(np.std(sp_signal)),
        'gs_mean': float(np.mean(gs_signal)),
        'sp_mean': float(np.mean(sp_signal)),
    }

# Multi-seed test
seeds = [42, 123, 777, 2024, 5555]
f_values = [0.055, 0.060, 0.062, 0.064, 0.066, 0.068, 0.070, 0.072, 0.076, 0.080]

print("=== Multi-Seed Robustness Test (5 seeds × 10 f values) ===")
print(f"{'f':>8} {'seed42':>8} {'seed123':>8} {'seed777':>8} {'seed2024':>8} {'seed5555':>8} {'mean':>8} {'std':>8} {'gs_std_avg':>10}")

results = {}
for f_val in f_values:
    results[f_val] = []
    for seed in seeds:
        r = run_gs_sandpile(f_val, size=48, n_steps=4000, burn_in=2000, seed=seed)
        results[f_val].append(r)
    
    c_vals = [r['zero_lag'] for r in results[f_val]]
    gs_stds = [r['gs_std'] for r in results[f_val]]
    c_mean = np.mean(c_vals)
    c_std = np.std(c_vals)
    gs_std_avg = np.mean(gs_stds)
    
    print(f"{f_val:8.3f} {c_vals[0]:8.4f} {c_vals[1]:8.4f} {c_vals[2]:8.4f} {c_vals[3]:8.4f} {c_vals[4]:8.4f} "
          f"{c_mean:8.4f} {c_std:8.4f} {gs_std_avg:10.6f}")

# Save
with open('r19z_multiseed_48x48.json', 'w') as f:
    json.dump({str(fv): [{'seed': seeds[i], 'C': r['zero_lag'], 'gs_std': r['gs_std'],
                          'sp_std': r['sp_std']} for i, r in enumerate(results[fv])]
               for fv in f_values}, f, indent=2)

# Plot
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Panel 1: C vs f with error bars
ax = axes[0]
f_vals = sorted(results.keys())
means = [np.mean([r['zero_lag'] for r in results[f]]) for f in f_vals]
stds = [np.std([r['zero_lag'] for r in results[f]]) for f in f_vals]
ax.errorbar(f_vals, means, yerr=stds, fmt='o-', linewidth=2, markersize=8, capsize=5)
ax.axhline(0, color='gray', linestyle='--')
ax.fill_between(f_vals, [m-s for m, s in zip(means, stds)], [m+s for m, s in zip(means, stds)],
                alpha=0.2, color='blue')
ax.set_xlabel('Feed rate f')
ax.set_ylabel('Cross-correlation C')
ax.set_title('48×48: Multi-seed averaged C vs f (5 seeds)')
ax.grid(True, alpha=0.3)

# Panel 2: gs_std vs f
ax = axes[1]
gs_means = [np.mean([r['gs_std'] for r in results[f]]) for f in f_vals]
gs_stds_err = [np.std([r['gs_std'] for r in results[f]]) for f in f_vals]
ax.errorbar(f_vals, gs_means, yerr=gs_stds_err, fmt='s-', color='green', linewidth=2, markersize=8, capsize=5)
ax.set_xlabel('Feed rate f')
ax.set_ylabel('GS pattern dynamics (std)')
ax.set_title('48×48: GS pattern dynamics strength')
ax.set_yscale('log')
ax.grid(True, alpha=0.3)

fig.suptitle('R19Z Multi-Seed Robustness Test on 48×48 Grid', fontsize=14, fontweight='bold')
fig.tight_layout()
fig.savefig('r19z_multiseed_48x48.png', dpi=150)
print("\nSaved r19z_multiseed_48x48.png")

# Summary assessment
print("\n=== ASSESSMENT ===")
for f_val in f_values:
    c_vals = [r['zero_lag'] for r in results[f_val]]
    gs_stds = [r['gs_std'] for r in results[f_val]]
    c_mean = np.mean(c_vals)
    c_std = np.std(c_vals)
    gs_avg = np.mean(gs_stds)
    
    if gs_avg < 1e-6:
        status = "DEAD (no GS dynamics → C is noise)"
    elif gs_avg < 1e-3:
        status = "MARGINAL (weak GS dynamics)"
    else:
        status = "ALIVE (real GS dynamics)"
    
    sign = "POSITIVE" if c_mean > 0.1 else ("NEGATIVE" if c_mean < -0.1 else "NEAR ZERO")
    robust = "ROBUST" if c_std < 0.1 else "NOISY"
    
    print(f"  f={f_val:.3f}: C={c_mean:+.4f}±{c_std:.4f} [{sign}, {robust}] — {status}")

print("\nDone!")
