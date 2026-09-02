"""R19Z Phase 8d: Gray-Scott Internal Sign Flip via Feed Rate

The key finding: Gray-Scott + Sandpile showed STRONG anti-resonance (C=-0.83).
Can we make it show RESONANCE by changing a parameter?

Theory: At different f values, Gray-Scott is in different dynamical regimes:
- Low f: spots/mazes form (autocatalytic amplification → internal sign +)
- High f: homogeneous (dissipation dominates → internal sign may flip)

Test: Run Gray-Scott + Sandpile at various f values and measure correlation.
If we find f values giving BOTH positive AND negative correlation, we have
a parameter-controlled resonance/anti-resonance switch!
"""
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

np.random.seed(42)

def run_gs_sandpile(f_val, k=0.062, Du=0.16, Dv=0.08, size=12,
                     n_steps=4000, N_gap=10, burn_in=1000,
                     gs_to_sp=0.3, sp_to_gs=0.005):
    """Run Gray-Scott + Sandpile coupled system at feed rate f_val.
    
    gs_to_sp: Gray-Scott pattern complexity modulates sandpile threshold
    sp_to_gs: Sandpile activity modulates Gray-Scott feed rate
    """
    # Gray-Scott
    u = np.ones((size, size)) * 0.5
    v = np.ones((size, size)) * 0.25
    u[size//2-2:size//2+2, size//2-2:size//2+2] = 0.25
    v[size//2-2:size//2+2, size//2-2:size//2+2] = 0.75
    
    # Sandpile
    grid = np.zeros((size, size))
    threshold_base = 4.0
    
    gs_signal = np.zeros(n_steps)
    sp_signal = np.zeros(n_steps)
    sp_activity_arr = np.zeros(n_steps)
    
    for t in range(burn_in + n_steps):
        ti = t - burn_in
        
        # Gray-Scott step (every step)
        u_pad = np.pad(u, 1, mode='reflect')
        v_pad = np.pad(v, 1, mode='reflect')
        u_lap = (u_pad[:-2,1:-1] + u_pad[2:,1:-1] + u_pad[1:-1,:-2] + u_pad[1:-1,2:] - 4*u)
        v_lap = (v_pad[:-2,1:-1] + v_pad[2:,1:-1] + v_pad[1:-1,:-2] + v_pad[1:-1,2:] - 4*v)
        uv2 = u * v * v
        
        # Feedback from sandpile
        f_eff = f_val
        if t > 0 and t % N_gap == 0 and ti > 0:
            f_eff = f_val + sp_to_gs * sp_activity_arr[ti - 1] if ti > 0 else f_val
        
        u = u + Du * u_lap - uv2 + f_eff * (1 - u)
        v = v + Dv * v_lap + uv2 - (f_eff + k) * v
        u = np.clip(u, 0, 1)
        v = np.clip(v, 0, 1)
        
        # Measure GS complexity
        gs_complexity = np.std(v)
        
        # Sandpile step (every N_gap steps)
        if t % N_gap == 0:
            # Feedback from GS: complexity modulates threshold
            threshold = threshold_base + gs_to_sp * (gs_complexity - 0.1) * 10
            threshold = max(threshold, 1.0)
            
            i, j = np.random.randint(0, size, 2)
            grid[i, j] += 1
            
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
            sp_activity_arr[ti] = avalanche
    
    # Cross-correlation
    max_lag = 200
    best_corr = 0
    best_lag = 0
    for lag in range(-max_lag, max_lag+1, 5):
        if lag < 0:
            a, b = gs_signal[:lag], sp_signal[-lag:]
        elif lag > 0:
            a, b = gs_signal[lag:], sp_signal[:-lag]
        else:
            a, b = gs_signal, sp_signal
        if np.std(a) > 0 and np.std(b) > 0:
            c = np.corrcoef(a, b)[0, 1]
            if abs(c) > abs(best_corr):
                best_corr = c
                best_lag = lag
    
    return {
        'f': f_val,
        'best_corr': best_corr,
        'best_lag': best_lag,
        'sign': '+' if best_corr > 0 else '-',
        'gs_signal': gs_signal,
        'sp_signal': sp_signal,
    }

# Test at various f values
f_test_values = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.12, 0.15]
results = []

print("Testing GS+Sandpile at various f values...")
for f in f_test_values:
    res = run_gs_sandpile(f, n_steps=3000, N_gap=10)
    results.append({k: v for k, v in res.items() if k not in ['gs_signal', 'sp_signal']})
    print(f"  f={f:.3f}: |C|={abs(res['best_corr']):.3f}, sign={res['sign']}, lag={res['best_lag']}")

# ========== VISUALIZATION ==========
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Panel 1: Cross-correlation vs f
ax = axes[0, 0]
corrs = [r['best_corr'] for r in results]
colors = ['#27ae60' if c > 0 else '#c0392b' for c in corrs]
ax.bar(range(len(f_test_values)), corrs, color=colors, alpha=0.8, width=0.8)
ax.axhline(y=0, color='black', linewidth=1)
ax.set_xticks(range(len(f_test_values)))
ax.set_xticklabels([f'{f:.3f}' for f in f_test_values], rotation=45)
ax.set_xlabel('Gray-Scott feed rate f', fontsize=12)
ax.set_ylabel('Best Cross-Correlation', fontsize=12)
ax.set_title('Gray-Scott + Sandpile: Resonance Phase vs Feed Rate f', fontsize=14, fontweight='bold')
ax.grid(axis='y', alpha=0.3)

# Panel 2: |C| vs f
ax = axes[0, 1]
abs_corrs = [abs(c) for c in corrs]
ax.plot(f_test_values, abs_corrs, 'o-', color='#2d3561', linewidth=2, markersize=8)
ax.axhline(y=0.3, color='gray', linestyle='--', alpha=0.5, label='|C|=0.3')
ax.set_xlabel('Feed rate f', fontsize=12)
ax.set_ylabel('|Cross-Correlation|', fontsize=12)
ax.set_title('Resonance Strength vs Feed Rate f', fontsize=14, fontweight='bold')
ax.grid(alpha=0.3)
ax.legend()

# Find best positive and negative examples
neg_results = [(i, r) for i, r in enumerate(results) if r['sign'] == '-' and abs(r['best_corr']) > 0.1]
pos_results = [(i, r) for i, r in enumerate(results) if r['sign'] == '+' and abs(r['best_corr']) > 0.1]

# Panel 3: Best anti-resonance time series
if neg_results:
    neg_best_idx, neg_best = max(neg_results, key=lambda x: abs(x[1]['best_corr']))
    res_full = run_gs_sandpile(f_test_values[neg_best_idx], n_steps=1500, N_gap=10)
    ax = axes[1, 0]
    t = np.arange(len(res_full['gs_signal']))
    gs_norm = (res_full['gs_signal'] - res_full['gs_signal'].min()) / (res_full['gs_signal'].max() - res_full['gs_signal'].min() + 1e-10)
    sp_norm = (res_full['sp_signal'] - res_full['sp_signal'].min()) / (res_full['sp_signal'].max() - res_full['sp_signal'].min() + 1e-10)
    ax.plot(t, gs_norm, 'b-', alpha=0.7, label='GS complexity', linewidth=1)
    ax.plot(t, sp_norm, 'r-', alpha=0.7, label='Sandpile height', linewidth=1)
    ax.set_xlabel('Time')
    ax.set_ylabel('Normalized signal')
    ax.set_title(f'Anti-Resonance (f={neg_best["f"]:.3f}, C={neg_best["best_corr"]:.3f})', 
                 fontsize=12, fontweight='bold', color='#c0392b')
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)

# Panel 4: Best resonance time series
if pos_results:
    pos_best_idx, pos_best = max(pos_results, key=lambda x: abs(x[1]['best_corr']))
    res_full = run_gs_sandpile(f_test_values[pos_best_idx], n_steps=1500, N_gap=10)
    ax = axes[1, 1]
    t = np.arange(len(res_full['gs_signal']))
    gs_norm = (res_full['gs_signal'] - res_full['gs_signal'].min()) / (res_full['gs_signal'].max() - res_full['gs_signal'].min() + 1e-10)
    sp_norm = (res_full['sp_signal'] - res_full['sp_signal'].min()) / (res_full['sp_signal'].max() - res_full['sp_signal'].min() + 1e-10)
    ax.plot(t, gs_norm, 'b-', alpha=0.7, label='GS complexity', linewidth=1)
    ax.plot(t, sp_norm, 'r-', alpha=0.7, label='Sandpile height', linewidth=1)
    ax.set_xlabel('Time')
    ax.set_ylabel('Normalized signal')
    ax.set_title(f'Resonance (f={pos_best["f"]:.3f}, C={pos+best["best_corr"]:.3f})' if False else f'Resonance (f={pos_best["f"]:.3f}, C={pos_best["best_corr"]:.3f})', 
                 fontsize=12, fontweight='bold', color='#27ae60')
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)
else:
    axes[1, 1].text(0.5, 0.5, 'No strong positive\nresonance found', 
                     ha='center', va='center', fontsize=14, transform=axes[1, 1].transAxes)
    axes[1, 1].set_title('Resonance (not found)', fontsize=12)

plt.suptitle('R19Z Phase 8d: Gray-Scott + Sandpile — Parameter-Controlled Resonance Switch', 
             fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('r19z_gs_sign_switch.png', dpi=150, bbox_inches='tight')
plt.close()

# Save data
with open('r19z_gs_sign_switch_data.json', 'w') as fp:
    json.dump({'f_values': f_test_values, 'results': results}, fp, indent=2)

print("\n=== GRAY-SCOTT SIGN SWITCH RESULTS ===")
print(f"Negative correlations: {sum(1 for r in results if r['sign'] == '-')}")
print(f"Positive correlations: {sum(1 for r in results if r['sign'] == '+')}")
print(f"Strong negative (|C|>0.1): {len(neg_results)}")
print(f"Strong positive (|C|>0.1): {len(pos_results)}")

if neg_results and pos_results:
    print("\n*** PARAMETER-CONTROLLED RESONANCE SWITCH CONFIRMED! ***")
    print(f"Anti-resonance at f={[f_test_values[i] for i, _ in neg_results]}")
    print(f"Resonance at f={[f_test_values[i] for i, _ in pos_results]}")
else:
    print("\nNo sign switch found yet. May need different coupling scheme or parameters.")

print("\nDone.")