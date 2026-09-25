"""
R19Z Critical Test: Does the Resonance Island survive on a large enough grid?

Previous finding: On 12x12 and 24x24, GS reaches static fixed point → 
the "resonance island" was noise correlation artifact.

On 48x48, GS shows real pattern dynamics (std_comp=0.054).

Now test: On 48x48, does the cross-correlation between GS and sandpile
show a real resonance island, or does it disappear?
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

def run_gs_sandpile_large(f_val, k=0.062, Du=0.16, Dv=0.08, size=48,
                          n_steps=4000, N_gap=10, burn_in=2000,
                          gs_to_sp=0.3, sp_to_gs=0.005, seed=42):
    """GS-sandpile coupled system on large grid."""
    rng = np.random.RandomState(seed)
    u = np.ones((size, size)) * 0.5
    v = np.ones((size, size)) * 0.25
    u[size//2-4:size//2+4, size//2-4:size//2+4] = 0.25
    v[size//2-4:size//2+4, size//2-4:size//2+4] = 0.75
    grid = np.zeros((size, size))
    threshold_base = 4.0
    gs_signal = np.zeros(n_steps)
    sp_signal = np.zeros(n_steps)
    sp_activity_arr = np.zeros(n_steps)
    
    for t in range(burn_in + n_steps):
        ti = t - burn_in
        u_pad = np.pad(u, 1, mode='reflect')
        v_pad = np.pad(v, 1, mode='reflect')
        u_lap = (u_pad[:-2,1:-1] + u_pad[2:,1:-1] + u_pad[1:-1,:-2] + u_pad[1:-1,2:] - 4*u)
        v_lap = (v_pad[:-2,1:-1] + v_pad[2:,1:-1] + v_pad[1:-1,:-2] + v_pad[1:-1,2:] - 4*v)
        uv2 = u * v * v
        f_eff = f_val
        if t > 0 and t % N_gap == 0 and ti > 0:
            f_eff = f_val + sp_to_gs * sp_activity_arr[ti - 1]
        u = u + Du * u_lap - uv2 + f_eff * (1 - u)
        v = v + Dv * v_lap + uv2 - (f_eff + k) * v
        u = np.clip(u, 0, 1)
        v = np.clip(v, 0, 1)
        
        gs_complexity = np.std(v)
        
        if t % N_gap == 0:
            threshold = threshold_base + gs_to_sp * (gs_complexity - 0.1) * 10
            threshold = max(threshold, 1.0)
            # Add grain to random site
            i, j = rng.randint(0, size, 2)
            grid[i, j] += 1
            avalanche = 0
            toppling = True
            while toppling:
                toppling = False
                above = np.where(grid >= threshold)
                for ii, jj in zip(above[0], above[1]):
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
            sp_activity_arr[ti] = avalanche
    
    zero_lag = 0
    if np.std(gs_signal) > 1e-10 and np.std(sp_signal) > 1e-10:
        zero_lag = float(np.corrcoef(gs_signal, sp_signal)[0, 1])
    
    return {
        'f': float(f_val),
        'zero_lag': zero_lag,
        'gs_mean': float(np.mean(gs_signal)),
        'sp_mean': float(np.mean(sp_signal)),
        'gs_std': float(np.std(gs_signal)),
        'sp_std': float(np.std(sp_signal)),
        'gs_signal': gs_signal,
        'sp_signal': sp_signal,
    }

# Test on 48x48
print("=== Resonance Island Test on 48x48 (real pattern dynamics) ===")
f_values = [0.050, 0.055, 0.060, 0.062, 0.064, 0.066, 0.068, 0.070, 0.072, 0.076, 0.080]
results = {}
for f_val in f_values:
    r = run_gs_sandpile_large(f_val, size=48, n_steps=4000, burn_in=2000, seed=42)
    results[f_val] = r
    print(f"  f={f_val:.3f}: C={r['zero_lag']:+.4f}, gs_std={r['gs_std']:.6f}, sp_std={r['sp_std']:.6f}")
    if r['gs_std'] < 1e-6:
        print(f"    -> NO GS DYNAMICS (static). Correlation is noise.")
    elif r['gs_std'] < 1e-3:
        print(f"    -> WEAK GS dynamics. Correlation marginally meaningful.")
    else:
        print(f"    -> REAL GS dynamics. Correlation is meaningful.")

# Save
with open('r19z_large_grid_test.json', 'w') as f:
    json.dump({str(k): {kk: float(vv) if isinstance(vv, (int, float, np.floating)) else vv.tolist()
                        for kk, vv in v.items() if kk != 'gs_signal' and kk != 'sp_signal'}
               for k, v in results.items()}, f, indent=2)

# Plot
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Panel 1: Cross-correlation vs f
ax = axes[0, 0]
f_vals = sorted(results.keys())
c_vals = [results[f]['zero_lag'] for f in f_vals]
gs_stds = [results[f]['gs_std'] for f in f_vals]
ax.plot(f_vals, c_vals, 'o-', linewidth=2, markersize=8)
ax.axhline(0, color='gray', linestyle='--', alpha=0.5)
ax.set_xlabel('Feed rate f')
ax.set_ylabel('Cross-correlation C')
ax.set_title('48×48: Cross-correlation vs f')
ax.grid(True, alpha=0.3)

# Panel 2: GS complexity std vs f
ax = axes[0, 1]
ax.plot(f_vals, gs_stds, 's-', color='green', linewidth=2, markersize=8)
ax.set_xlabel('Feed rate f')
ax.set_ylabel('GS complexity std')
ax.set_title('48×48: GS pattern dynamics strength')
ax.grid(True, alpha=0.3)
ax.set_yscale('log')

# Panel 3: Time series at f=0.064 (claimed island center)
ax = axes[1, 0]
r064 = results[0.064]
ax2 = ax.twinx()
l1 = ax.plot(r064['gs_signal'][:2000], linewidth=0.5, color='blue', label='GS complexity')
l2 = ax2.plot(r064['sp_signal'][:2000], linewidth=0.5, color='red', label='Sandpile mean')
ax.set_ylabel('GS std(v)', color='blue')
ax2.set_ylabel('Sandpile mean(grid)', color='red')
ax.set_xlabel('Time step')
ax.set_title(f'48×48, f=0.064: GS_std={r064["gs_std"]:.6f}, C={r064["zero_lag"]:.4f}')
lines = l1 + l2
ax.legend(lines, [l.get_label() for l in lines], loc='upper right')

# Panel 4: Time series at f=0.070
ax = axes[1, 1]
r070 = results[0.070]
ax2 = ax.twinx()
l1 = ax.plot(r070['gs_signal'][:2000], linewidth=0.5, color='blue', label='GS complexity')
l2 = ax2.plot(r070['sp_signal'][:2000], linewidth=0.5, color='red', label='Sandpile mean')
ax.set_ylabel('GS std(v)', color='blue')
ax2.set_ylabel('Sandpile mean(grid)', color='red')
ax.set_xlabel('Time step')
ax.set_title(f'48×48, f=0.070: GS_std={r070["gs_std"]:.6f}, C={r070["zero_lag"]:.4f}')
lines = l1 + l2
ax.legend(lines, [l.get_label() for l in lines], loc='upper right')

fig.suptitle('R19Z Critical Test: Resonance Island on 48×48 Grid (Real Pattern Dynamics)', 
             fontsize=14, fontweight='bold')
fig.tight_layout()
fig.savefig('r19z_large_grid_test.png', dpi=150)
print("\nSaved r19z_large_grid_test.png")
print("Done!")
