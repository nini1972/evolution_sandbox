"""R19Z Phase 8c: Sign-Controllable Resonance — Strong Coupling

The internal sign spectroscopy showed:
- Logistic map at r<3.0 (fixed point): internal sign = -1.0 
- Logistic map at r>3.57 (chaotic): internal sign ~ 0 (chaotic scrambling)

But the previous coupling was too weak. Let me use STRONG coupling and 
longer timescale gaps to properly test the phase relationship.
"""
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

np.random.seed(42)

def run_logistic_sandpile(r_param, n_steps=8000, N_gap=50, 
                          log_to_sp=0.01, sp_to_log=0.05, burn_in=2000):
    """Run logistic-sandpile coupled system.
    
    log_to_sp: logistic x modulates sandpile threshold (coupling A→B)
    sp_to_log: sandpile activity modulates logistic parameter (coupling B→A)
    """
    sp_size = 12
    grid = np.zeros((sp_size, sp_size))
    threshold_base = 4.0
    x = 0.5
    
    log_signal = np.zeros(n_steps)
    sp_signal = np.zeros(n_steps)
    sp_activity = np.zeros(n_steps)
    
    for t in range(burn_in + n_steps):
        ti = t - burn_in  # index into signal arrays
        # Update sandpile (slow system)
        if t % N_gap == 0:
            # Feedback from logistic: x modulates threshold
            threshold = threshold_base + log_to_sp * (x - 0.5) * 10
            threshold = max(threshold, 1.0)
            
            # Drop grain
            i, j = np.random.randint(0, sp_size, 2)
            grid[i, j] += 1
            
            # Topple
            avalanche = 0
            toppling = True
            while toppling:
                toppling = False
                for ii in range(sp_size):
                    for jj in range(sp_size):
                        if grid[ii, jj] >= threshold:
                            toppling = True
                            avalanche += 1
                            grid[ii, jj] -= 4
                            if ii > 0: grid[ii, jj-1 if jj > 0 else jj] += 0
                            if ii > 0: grid[ii-1, jj] += 1
                            if ii < sp_size-1: grid[ii+1, jj] += 1
                            if jj > 0: grid[ii, jj-1] += 1
                            if jj < sp_size-1: grid[ii, jj+1] += 1
            
            sp_activity[ti] = avalanche
            
            # Feedback: sandpile activity modulates logistic parameter
            r_eff = r_param + sp_to_log * avalanche / 10.0
            r_eff = np.clip(r_eff, 0.1, 4.0)
            x = r_eff * x * (1 - x)
            x = np.clip(x, 1e-10, 1 - 1e-10)
        else:
            x = r_param * x * (1 - x)
            x = np.clip(x, 1e-10, 1 - 1e-10)
        
        if t >= burn_in:
            log_signal[ti] = x
            sp_signal[ti] = np.mean(grid)
    
    # Cross-correlation with lags
    max_lag = 200
    best_corr = 0
    best_lag = 0
    for lag in range(-max_lag, max_lag+1, 5):
        if lag < 0:
            a, b = log_signal[:lag], sp_signal[-lag:]
        elif lag > 0:
            a, b = log_signal[lag:], sp_signal[:-lag]
        else:
            a, b = log_signal, sp_signal
        if np.std(a) > 0 and np.std(b) > 0:
            c = np.corrcoef(a, b)[0, 1]
            if abs(c) > abs(best_corr):
                best_corr = c
                best_lag = lag
    
    return {
        'r': r_param,
        'best_corr': best_corr,
        'best_lag': best_lag,
        'sign': '+' if best_corr > 0 else '-',
        'log_signal': log_signal,
        'sp_signal': sp_signal,
    }

# Test at r values spanning the bifurcation diagram
# Focus on key regimes: fixed point (2.5-3.0), period-2 (3.0-3.45), period-4 (3.45-3.54), chaotic (3.57-4.0)
r_test_values = [2.5, 2.7, 2.9, 3.0, 3.1, 3.2, 3.3, 3.4, 3.45, 3.5, 3.55, 3.6, 3.7, 3.8, 3.9, 4.0]
results = []

print("Testing logistic-sandpile with strong coupling at various r values...")
for r in r_test_values:
    res = run_logistic_sandpile(r, n_steps=5000, N_gap=50, log_to_sp=0.02, sp_to_log=0.1)
    results.append({k: v for k, v in res.items() if k not in ['log_signal', 'sp_signal']})
    print(f"  r={r:.2f}: |C|={abs(res['best_corr']):.3f}, sign={res['sign']}, lag={res['best_lag']}")

# ========== VISUALIZATION ==========
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Panel 1: Cross-correlation vs r
ax = axes[0, 0]
corrs = [r['best_corr'] for r in results]
colors = ['#27ae60' if c > 0 else '#c0392b' for c in corrs]
ax.bar(range(len(r_test_values)), corrs, color=colors, alpha=0.8, width=0.8)
ax.axhline(y=0, color='black', linewidth=1)
ax.set_xticks(range(len(r_test_values)))
ax.set_xticklabels([f'{r:.2f}' for r in r_test_values], rotation=45)
ax.set_xlabel('Logistic parameter r', fontsize=12)
ax.set_ylabel('Best Cross-Correlation', fontsize=12)
ax.set_title('Logistic-Sandpile: Resonance Phase vs Parameter r', fontsize=14, fontweight='bold')
ax.grid(axis='y', alpha=0.3)

# Panel 2: |C| vs r
ax = axes[0, 1]
abs_corrs = [abs(c) for c in corrs]
ax.plot(r_test_values, abs_corrs, 'o-', color='#2d3561', linewidth=2, markersize=8)
ax.axhline(y=0.3, color='gray', linestyle='--', alpha=0.5, label='|C|=0.3 threshold')
ax.set_xlabel('Logistic parameter r', fontsize=12)
ax.set_ylabel('|Cross-Correlation|', fontsize=12)
ax.set_title('Resonance Strength vs Parameter r', fontsize=14, fontweight='bold')
ax.grid(alpha=0.3)
ax.legend()

# Panel 3-4: Time series at best negative and positive examples
neg_best = max(results, key=lambda r: abs(r['best_corr']) if r['sign'] == '-' else 0)
pos_best = max(results, key=lambda r: abs(r['best_corr']) if r['sign'] == '+' else 0)

for panel_idx, (example, title_color, title_prefix) in enumerate([
    (neg_best, '#c0392b', 'Anti-Resonance'),
    (pos_best, '#27ae60', 'Resonance')
]):
    res_full = run_logistic_sandpile(example['r'], n_steps=1000, N_gap=50, 
                                      log_to_sp=0.02, sp_to_log=0.1, burn_in=1000)
    ax = axes[1, panel_idx]
    t = np.arange(len(res_full['log_signal']))
    # Normalize
    log_norm = (res_full['log_signal'] - res_full['log_signal'].min()) / (res_full['log_signal'].max() - res_full['log_signal'].min() + 1e-10)
    sp_norm = (res_full['sp_signal'] - res_full['sp_signal'].min()) / (res_full['sp_signal'].max() - res_full['sp_signal'].min() + 1e-10)
    ax.plot(t, log_norm, 'b-', alpha=0.7, label='Logistic x', linewidth=0.8)
    ax.plot(t, sp_norm, 'r-', alpha=0.7, label='Sandpile height', linewidth=0.8)
    ax.set_xlabel('Time')
    ax.set_ylabel('Normalized signal')
    ax.set_title(f'{title_prefix} (r={example["r"]:.2f}, C={example["best_corr"]:.3f})', 
                 fontsize=12, fontweight='bold', color=title_color)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)

plt.suptitle('R19Z Phase 8c: Parameter-Controlled Resonance Phase Flip', 
             fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('r19z_sign_controllable_v2.png', dpi=150, bbox_inches='tight')
plt.close()

# Save data
with open('r19z_sign_controllable_v2_data.json', 'w') as fp:
    json.dump({'r_values': r_test_values, 'results': results}, fp, indent=2)

print("\n=== RESULTS ===")
strong_neg = [r for r in results if r['sign'] == '-' and abs(r['best_corr']) > 0.1]
strong_pos = [r for r in results if r['sign'] == '+' and abs(r['best_corr']) > 0.1]
print(f"Strong anti-resonance (|C|>0.1, sign=-): {len(strong_neg)} configs")
print(f"Strong resonance (|C|>0.1, sign=+): {len(strong_pos)} configs")
if strong_neg:
    print(f"  Anti-resonance at r={[r['r'] for r in strong_neg]}")
if strong_pos:
    print(f"  Resonance at r={[r['r'] for r in strong_pos]}")

if strong_neg and strong_pos:
    print("\n*** SIGN-CONTROLLABLE RESONANCE CONFIRMED! ***")
    print("The logistic-sandpile pair can switch between resonance and anti-resonance")
    print("by changing the logistic map parameter r.")
else:
    print("\nNeed further investigation...")

print("\nDone.")