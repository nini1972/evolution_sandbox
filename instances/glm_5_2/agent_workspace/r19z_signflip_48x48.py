"""
R19Z Sign-Flip Test on 48x48 - Reduced version (fewer seeds, shorter sim)
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

def run_gs_sp(f_val, k=0.062, Du=0.16, Dv=0.08, size=48,
              n_steps=2000, N_gap=10, burn_in=1000,
              gs_to_sp=2.0, sp_to_gs=0.02, seed=42,
              gs_sp_sign=+1, sp_gs_sign=+1):
    rng = np.random.RandomState(seed)
    u = np.ones((size, size)) * 0.5
    v = np.ones((size, size)) * 0.25
    u[size//2-4:size//2+4, size//2-4:size//2+4] = 0.25
    v[size//2-4:size//2+4, size//2-4:size//2+4] = 0.75
    sp_size = size // 4
    grid = np.zeros((sp_size, sp_size))
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
                u = u + sp_gs_sign * noise
        u = u + Du * u_lap - uv2 + f_val * (1 - u)
        v = v + Dv * v_lap + uv2 - (f_val + k) * v
        u = np.clip(u, 0, 1)
        v = np.clip(v, 0, 1)
        gs_complexity = np.std(v)
        if t % N_gap == 0:
            threshold = max(4.0 + gs_sp_sign * gs_to_sp * gs_complexity, 1.5)
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
    return {'C': zero_lag, 'gs_std': float(np.std(gs_signal))}

# Test at f=0.070 with 3 seeds and 4 sign combos (reduced from 5 seeds)
f_test = 0.070
seeds = [42, 777, 5555]
sign_combos = [(+1, +1), (+1, -1), (-1, +1), (-1, -1)]
sign_labels = ['(+,+)', '(+,-)', '(-,+)', '(-,-)']

print("=== Sign-Flip Test on 48×48 at f=0.070 (3 seeds, shorter sim) ===")
print(f"{'Sign':>8} {'s42':>8} {'s777':>8} {'s5555':>8} {'mean':>8} {'std':>8}")
results = {}
for (gs_sp, sp_gs), label in zip(sign_combos, sign_labels):
    results[label] = []
    for seed in seeds:
        r = run_gs_sp(f_test, size=48, n_steps=2000, burn_in=1000, seed=seed,
                      gs_sp_sign=gs_sp, sp_gs_sign=sp_gs)
        results[label].append(r)
    c_vals = [r['C'] for r in results[label]]
    print(f"{label:8s} {c_vals[0]:8.4f} {c_vals[1]:8.4f} {c_vals[2]:8.4f} {np.mean(c_vals):8.4f} {np.std(c_vals):8.4f}")

# Save
with open('r19z_signflip_48x48.json', 'w') as f:
    json.dump({label: [{'seed': seeds[i], 'C': r['C'], 'gs_std': r['gs_std']}
                       for i, r in enumerate(results[label])]
               for label in sign_labels}, f, indent=2)

# Plot
fig, ax = plt.subplots(1, 1, figsize=(8, 6))
means = [np.mean([r['C'] for r in results[label]]) for label in sign_labels]
stds = [np.std([r['C'] for r in results[label]]) for label in sign_labels]
colors = ['blue' if m > 0 else 'red' for m in means]
ax.bar(range(4), means, yerr=stds, color=colors, alpha=0.7, capsize=8)
ax.set_xticks(range(4))
ax.set_xticklabels(sign_labels)
ax.axhline(0, color='gray', linestyle='--')
ax.set_ylabel('Cross-correlation C')
ax.set_title('48×48 f=0.070: Sign-flip test (real GS dynamics)')
ax.grid(True, alpha=0.3)
for i, (m, s) in enumerate(zip(means, stds)):
    ax.text(i, m + (0.03 if m > 0 else -0.03), f'{m:+.3f}', ha='center', fontsize=10)

fig.suptitle('R19Z Historical Falsification: Sign-Flip on 48×48', fontsize=14, fontweight='bold')
fig.tight_layout()
fig.savefig('r19z_signflip_48x48.png', dpi=150)
print("\nSaved r19z_signflip_48x48.png")

# Assessment
print("\n=== ASSESSMENT ===")
all_positive = all(np.mean([r['C'] for r in results[label]]) > 0 for label in sign_labels)
all_negative = all(np.mean([r['C'] for r in results[label]]) < 0 for label in sign_labels)
if all_positive:
    print("ALL POSITIVE: Original anti-resonance claim FALSIFIED on 48×48")
    print("The structural anti-resonance was an artifact of small grid + static GS")
elif all_negative:
    print("ALL NEGATIVE: Anti-resonance persists even with real dynamics")
    print("The structural anti-resonance is REAL")
else:
    print("MIXED: Sign-dependent results")
    for label in sign_labels:
        m = np.mean([r['C'] for r in results[label]])
        print(f"  {label}: C={m:+.4f}")
print("Done!")
