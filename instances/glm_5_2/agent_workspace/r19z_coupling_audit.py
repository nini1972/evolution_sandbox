"""
R19Z Coupling Audit: Is the feedback actually bidirectional?

Key finding: sp_std = 0.050117 for ALL f values → sandpile is unaffected by GS.
The coupling is effectively one-way. This invalidates "resonance" claims.

This script:
1. Verifies coupling is broken
2. Fixes it with stronger, more direct coupling
3. Re-tests the resonance island with working bidirectional coupling
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

def run_gs_sandpile_fixed(f_val, k=0.062, Du=0.16, Dv=0.08, size=48,
                          n_steps=4000, N_gap=10, burn_in=2000,
                          gs_to_sp=2.0, sp_to_gs=0.02, seed=42):
    """
    Fixed coupling: 
    - GS → SP: GS complexity directly sets sandpile threshold (stronger)
    - SP → GS: Avalanche activity directly perturbs GS u-field (stronger, spatial)
    """
    rng = np.random.RandomState(seed)
    u = np.ones((size, size)) * 0.5
    v = np.ones((size, size)) * 0.25
    u[size//2-4:size//2+4, size//2-4:size//2+4] = 0.25
    v[size//2-4:size//2+4, size//2-4:size//2+4] = 0.75
    
    # Sandpile grid
    sp_size = size // 4  # 12x12 sandpile for 48x48 GS
    grid = np.zeros((sp_size, sp_size))
    threshold_base = 4.0
    
    gs_signal = np.zeros(n_steps)
    sp_signal = np.zeros(n_steps)
    sp_avalanche = np.zeros(n_steps)
    sp_threshold = np.zeros(n_steps)
    
    for t in range(burn_in + n_steps):
        ti = t - burn_in
        
        # --- GS step ---
        u_pad = np.pad(u, 1, mode='reflect')
        v_pad = np.pad(v, 1, mode='reflect')
        u_lap = (u_pad[:-2,1:-1] + u_pad[2:,1:-1] + u_pad[1:-1,:-2] + u_pad[1:-1,2:] - 4*u)
        v_lap = (v_pad[:-2,1:-1] + v_pad[2:,1:-1] + v_pad[1:-1,:-2] + v_pad[1:-1,2:] - 4*v)
        uv2 = u * v * v
        
        # Sandpile → GS: spatial perturbation from avalanche
        if t % N_gap == 0 and ti > 0:
            av = sp_avalanche[ti - 1]
            if av > 0:
                # Inject noise proportional to avalanche
                noise = rng.normal(0, sp_to_gs * np.sqrt(av), (size, size))
                u = u + noise
        
        f_eff = f_val
        u = u + Du * u_lap - uv2 + f_eff * (1 - u)
        v = v + Dv * v_lap + uv2 - (f_eff + k) * v
        u = np.clip(u, 0, 1)
        v = np.clip(v, 0, 1)
        
        gs_complexity = np.std(v)
        
        # --- Sandpile step ---
        if t % N_gap == 0:
            # GS → SP: threshold modulated by GS complexity
            threshold = threshold_base + gs_to_sp * gs_complexity
            threshold = max(threshold, 1.5)
            
            # Add grain
            i, j = rng.randint(0, sp_size, 2)
            grid[i, j] += 1
            
            # Topple
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
                    share = threshold / 4
                    if ii > 0: grid[ii-1, jj] += 1
                    if ii < sp_size-1: grid[ii+1, jj] += 1
                    if jj > 0: grid[ii, jj-1] += 1
                    if jj < sp_size-1: grid[ii, jj+1] += 1
                max_iters -= 1
        else:
            avalanche = 0
            threshold = threshold_base
        
        if ti >= 0:
            gs_signal[ti] = gs_complexity
            sp_signal[ti] = np.mean(grid)
            sp_avalanche[ti] = avalanche
            sp_threshold[ti] = threshold
    
    # Cross-correlation at multiple lags
    lags = range(-50, 51)
    c_lags = []
    for lag in lags:
        if lag >= 0:
            g = gs_signal[:n_steps-lag]
            s = sp_signal[lag:]
        else:
            g = gs_signal[-lag:]
            s = sp_signal[:n_steps+lag]
        if len(g) > 10 and np.std(g) > 1e-10 and np.std(s) > 1e-10:
            c_lags.append(float(np.corrcoef(g, s)[0, 1]))
        else:
            c_lags.append(0.0)
    
    zero_lag = c_lags[50]  # lag=0
    
    return {
        'f': float(f_val),
        'zero_lag': float(zero_lag),
        'max_abs_c': float(max(abs(c) for c in c_lags)),
        'gs_std': float(np.std(gs_signal)),
        'sp_std': float(np.std(sp_signal)),
        'gs_mean': float(np.mean(gs_signal)),
        'sp_mean': float(np.mean(sp_signal)),
        'sp_avalanche_mean': float(np.mean(sp_avalanche)),
        'sp_threshold_mean': float(np.mean(sp_threshold)),
        'sp_threshold_std': float(np.std(sp_threshold)),
        'gs_signal': gs_signal,
        'sp_signal': sp_signal,
        'c_lags': c_lags,
        'sp_avalanche': sp_avalanche,
        'sp_threshold': sp_threshold,
    }

# Test coupling: compare sp_threshold_std across f values
print("=== Coupling Verification: Does GS affect the sandpile? ===")
print(f"{'f':>8} {'C(0)':>8} {'gs_std':>10} {'sp_std':>10} {'sp_thresh_std':>14} {'sp_aval_mean':>14}")
f_values = [0.055, 0.060, 0.064, 0.068, 0.072, 0.076, 0.080]
results = {}
for f_val in f_values:
    r = run_gs_sandpile_fixed(f_val, size=48, n_steps=4000, burn_in=2000, seed=42)
    results[f_val] = r
    print(f"{f_val:8.3f} {r['zero_lag']:8.4f} {r['gs_std']:10.6f} {r['sp_std']:10.6f} "
          f"{r['sp_threshold_std']:14.8f} {r['sp_avalanche_mean']:14.4f}")

# Key diagnostic: if sp_threshold_std varies across f values, coupling IS working
threshold_stds = [results[f]['sp_threshold_std'] for f in f_values]
print(f"\nsp_threshold_std range: [{min(threshold_stds):.8f}, {max(threshold_stds):.8f}]")
if max(threshold_stds) / (min(threshold_stds) + 1e-15) > 1.5:
    print("-> Coupling IS working: GS affects sandpile threshold")
else:
    print("-> Coupling may still be too weak")

# Save data
with open('r19z_coupling_audit.json', 'w') as f:
    json.dump({str(k): {kk: float(vv) if isinstance(vv, (int, float, np.floating)) else vv.tolist()
                        for kk, vv in v.items() if kk not in ('gs_signal', 'sp_signal', 'c_lags', 
                                                               'sp_avalanche', 'sp_threshold')}
               for k, v in results.items()}, f, indent=2)

# Plot
fig, axes = plt.subplots(3, 2, figsize=(14, 15))

# Panel 1: C vs f
ax = axes[0, 0]
f_vals = sorted(results.keys())
c_vals = [results[f]['zero_lag'] for f in f_vals]
colors = ['red' if c < 0 else 'blue' for c in c_vals]
ax.bar(range(len(f_vals)), c_vals, color=colors, alpha=0.7)
ax.set_xticks(range(len(f_vals)))
ax.set_xticklabels([f'{f:.3f}' for f in f_vals])
ax.axhline(0, color='gray', linestyle='--')
ax.set_ylabel('Cross-correlation C(0)')
ax.set_title('48×48: Cross-correlation vs f (fixed coupling)')
ax.grid(True, alpha=0.3)

# Panel 2: Threshold variation
ax = axes[0, 1]
t_stds = [results[f]['sp_threshold_std'] for f in f_vals]
ax.bar(range(len(f_vals)), t_stds, color='green', alpha=0.7)
ax.set_xticks(range(len(f_vals)))
ax.set_xticklabels([f'{f:.3f}' for f in f_vals])
ax.set_ylabel('Sandpile threshold std')
ax.set_title('Coupling strength: GS→SP threshold variation')
ax.grid(True, alpha=0.3)

# Panel 3-6: Time series
for idx, f_val in enumerate([0.064, 0.072]):
    ax = axes[1, idx]
    r = results[f_val]
    ax2 = ax.twinx()
    l1 = ax.plot(r['gs_signal'][:2000], linewidth=0.5, color='blue', label='GS complexity')
    l2 = ax2.plot(r['sp_signal'][:2000], linewidth=0.5, color='red', label='Sandpile mean')
    ax.set_ylabel('GS std(v)', color='blue')
    ax2.set_ylabel('Sandpile mean', color='red')
    ax.set_xlabel('Time step')
    ax.set_title(f'f={f_val}: C={r["zero_lag"]:.4f}, gs_std={r["gs_std"]:.6f}')
    lines = l1 + l2
    ax.legend(lines, [l.get_label() for l in lines], loc='upper right')
    
    # Cross-correlation function
    ax = axes[2, idx]
    lags = range(-50, 51)
    ax.plot(list(lags), r['c_lags'], linewidth=1.5)
    ax.axhline(0, color='gray', linestyle='--')
    ax.set_xlabel('Lag')
    ax.set_ylabel('Cross-correlation')
    ax.set_title(f'f={f_val}: Cross-correlation function')
    ax.grid(True, alpha=0.3)

fig.suptitle('R19Z Coupling Audit: Fixed Bidirectional Coupling on 48×48', 
             fontsize=14, fontweight='bold')
fig.tight_layout()
fig.savefig('r19z_coupling_audit.png', dpi=150)
print("\nSaved r19z_coupling_audit.png")
print("Done!")
