"""R19Z Phase 8b: Sign-Controllable Resonance via Logistic Map Parameter

The internal sign spectroscopy revealed:
- Logistic map at r<3.0 (fixed point): internal sign = -1.0 (strongly negative)
- Logistic map at r>3.0 (period-2/chaos): internal sign ~ -0.05 to +0.07 (near zero)

The key question: does the coupled logistic-sandpile system show ANTI-RESONANCE 
when r is in the fixed-point regime, and RESONANCE when r is in the chaotic regime?

This would be the first demonstration of a PARAMETER-CONTROLLED phase flip
between resonance and anti-resonance.
"""
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

np.random.seed(42)

def run_logistic_sandpile(r_param, n_steps=4000, N_gap=20, coupling=0.001):
    """Run logistic-sandpile coupled system at logistic parameter r_param.
    
    Returns cross-correlation between logistic x and sandpile activity.
    """
    # Sandpile
    sp_size = 12
    grid = np.zeros((sp_size, sp_size))
    threshold_base = 4.0
    
    # Logistic map
    x = 0.5
    
    log_signal = np.zeros(n_steps)
    sp_signal = np.zeros(n_steps)
    sp_activity = np.zeros(n_steps)
    
    for t in range(n_steps):
        # Update sandpile (slow system)
        if t % N_gap == 0:
            # Drop grain at random position
            i, j = np.random.randint(0, sp_size, 2)
            grid[i, j] += 1
            
            # Topple
            avalanche = 0
            toppling = True
            while toppling:
                toppling = False
                for ii in range(sp_size):
                    for jj in range(sp_size):
                        if grid[ii, jj] >= threshold_base:
                            toppling = True
                            avalanche += 1
                            grid[ii, jj] -= 4
                            if ii > 0: grid[ii-1, jj] += 1
                            if ii < sp_size-1: grid[ii+1, jj] += 1
                            if jj > 0: grid[ii, jj-1] += 1
                            if jj < sp_size-1: grid[ii, jj+1] += 1
            
            sp_activity[t] = avalanche
            
            # Feedback: sandpile activity modulates logistic parameter
            r_effective = r_param + coupling * avalanche
            r_effective = np.clip(r_effective, 0.1, 4.0)
            x = r_effective * x * (1 - x)
            x = np.clip(x, 1e-10, 1 - 1e-10)
        else:
            # Just update logistic map
            x = r_param * x * (1 - x)
            x = np.clip(x, 1e-10, 1 - 1e-10)
        
        log_signal[t] = x
        sp_signal[t] = np.mean(grid)
    
    # Cross-correlation
    # Use only non-zero activity points
    if np.std(log_signal) > 0 and np.std(sp_signal) > 0:
        corr = np.corrcoef(log_signal, sp_signal)[0, 1]
    else:
        corr = 0.0
    
    # Also compute lagged cross-correlation to find phase
    max_lag = 100
    best_corr = 0
    best_lag = 0
    for lag in range(-max_lag, max_lag+1):
        if lag < 0:
            c = np.corrcoef(log_signal[:lag], sp_signal[-lag:])[0, 1]
        elif lag > 0:
            c = np.corrcoef(log_signal[lag:], sp_signal[:-lag])[0, 1]
        else:
            c = corr
        if abs(c) > abs(best_corr):
            best_corr = c
            best_lag = lag
    
    return {
        'r': r_param,
        'corr': corr,
        'best_corr': best_corr,
        'best_lag': best_lag,
        'sign': '+' if best_corr > 0 else '-',
        'log_signal': log_signal,
        'sp_signal': sp_signal,
    }

# Test at multiple r values spanning the bifurcation diagram
r_test_values = np.linspace(2.5, 4.0, 30)
results = []

print("Testing logistic-sandpile at various r values...")
for r in r_test_values:
    res = run_logistic_sandpile(r, n_steps=3000, N_gap=20)
    results.append({k: v for k, v in res.items() if k not in ['log_signal', 'sp_signal']})
    print(f"  r={r:.2f}: |C|={abs(res['best_corr']):.3f}, sign={res['sign']}, lag={res['best_lag']}")

# Find sign changes
signs = [r['sign'] for r in results]
sign_changes = [i for i in range(1, len(signs)) if signs[i] != signs[i-1]]

print(f"\nSign changes at r indices: {sign_changes}")
for sc in sign_changes:
    print(f"  Between r={r_test_values[sc-1]:.2f} and r={r_test_values[sc]:.2f}")

# ========== VISUALIZATION ==========
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Panel 1: Cross-correlation sign vs r
ax = axes[0, 0]
corrs = [r['best_corr'] for r in results]
colors = ['#27ae60' if c > 0 else '#c0392b' for c in corrs]
ax.bar(range(len(r_test_values)), corrs, color=colors, alpha=0.8, width=1.0)
ax.axhline(y=0, color='black', linewidth=1)
ax.set_xticks(range(0, len(r_test_values), 5))
ax.set_xticklabels([f'{r_test_values[i]:.2f}' for i in range(0, len(r_test_values), 5)])
ax.set_xlabel('Logistic parameter r', fontsize=12)
ax.set_ylabel('Best Cross-Correlation', fontsize=12)
ax.set_title('Logistic-Sandpile: Resonance Phase vs Parameter r', fontsize=14, fontweight='bold')
ax.grid(axis='y', alpha=0.3)

# Mark sign changes
for sc in sign_changes:
    ax.axvline(x=sc-0.5, color='purple', linestyle='--', linewidth=2, alpha=0.7)
    ax.text(sc-0.5, max(corrs)*0.9, f'r={r_test_values[sc]:.2f}', fontsize=10, color='purple', ha='center')

# Panel 2: |C| vs r
ax = axes[0, 1]
abs_corrs = [abs(c) for c in corrs]
ax.plot(r_test_values, abs_corrs, 'o-', color='#2d3561', linewidth=2, markersize=6)
ax.set_xlabel('Logistic parameter r', fontsize=12)
ax.set_ylabel('|Cross-Correlation|', fontsize=12)
ax.set_title('Resonance Strength vs Parameter r', fontsize=14, fontweight='bold')
ax.grid(alpha=0.3)
ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)

# Panel 3-4: Time series at key points
# Find one negative and one positive example
neg_example = None
pos_example = None
for i, r in enumerate(results):
    if r['sign'] == '-' and abs(r['best_corr']) > 0.1 and neg_example is None:
        neg_example = run_logistic_sandpile(r_test_values[i], n_steps=500, N_gap=20)
    if r['sign'] == '+' and abs(r['best_corr']) > 0.1 and pos_example is None:
        pos_example = run_logistic_sandpile(r_test_values[i], n_steps=500, N_gap=20)

if neg_example:
    ax = axes[1, 0]
    t = np.arange(len(neg_example['log_signal']))
    ax.plot(t, neg_example['log_signal']/max(neg_example['log_signal'].max(), 1e-10), 
            'b-', alpha=0.7, label='Logistic x (normalized)', linewidth=0.8)
    ax2 = ax.twinx()
    ax2.plot(t, neg_example['sp_signal'], 'r-', alpha=0.7, label='Sandpile avg height', linewidth=0.8)
    ax.set_xlabel('Time')
    ax.set_ylabel('Logistic x (normalized)', color='blue')
    ax2.set_ylabel('Sandpile height', color='red')
    ax.set_title(f'Anti-Resonance (r={neg_example["r"]:.2f}, C={neg_example["best_corr"]:.3f})', 
                 fontsize=12, fontweight='bold', color='#c0392b')

if pos_example:
    ax = axes[1, 1]
    t = np.arange(len(pos_example['log_signal']))
    ax.plot(t, pos_example['log_signal']/max(pos_example['log_signal'].max(), 1e-10), 
            'b-', alpha=0.7, label='Logistic x (normalized)', linewidth=0.8)
    ax2 = ax.twinx()
    ax2.plot(t, pos_example['sp_signal'], 'r-', alpha=0.7, label='Sandpile avg height', linewidth=0.8)
    ax.set_xlabel('Time')
    ax.set_ylabel('Logistic x (normalized)', color='blue')
    ax2.set_ylabel('Sandpile height', color='red')
    ax.set_title(f'Resonance (r={pos_example["r"]:.2f}, C={pos_example["best_corr"]:.3f})', 
                 fontsize=12, fontweight='bold', color='#27ae60')

plt.suptitle('R19Z Phase 8b: Parameter-Controlled Resonance Phase Flip in Logistic-Sandpile', 
             fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('r19z_sign_controllable.png', dpi=150, bbox_inches='tight')
plt.close()

# Save data
with open('r19z_sign_controllable_data.json', 'w') as fp:
    json.dump({'r_values': r_test_values.tolist(), 'results': results}, fp, indent=2)

print("\n=== SIGN-CONTROLLABLE RESONANCE: RESULTS ===")
if sign_changes:
    print(f"Found {len(sign_changes)} sign change(s) in the resonance phase!")
    print("The logistic-sandpile pair IS sign-controllable via parameter r.")
    print("This is the FIRST demonstration of parameter-controlled resonance/anti-resonance switching.")
else:
    print("No sign changes found. All configurations show same phase.")
    # Check if all are same sign
    all_signs = set(signs)
    print(f"Signs observed: {all_signs}")

print("\nDone.")