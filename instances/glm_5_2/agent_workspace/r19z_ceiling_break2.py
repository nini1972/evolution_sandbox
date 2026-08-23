"""
R19Z: Testing the Resonance Ceiling (optimized version)
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

np.random.seed(42)

def run_coupled(N_gap, coupling_K, forcing_amp, forcing_freq,
                n_kuramoto=30, n_steps=1500, transients=300):
    omega = np.random.normal(1.0, 0.1, n_kuramoto)
    theta = np.random.uniform(0, 2*np.pi, n_kuramoto)
    
    grid_size = 16
    pile = np.random.uniform(0.5, 1.5, (grid_size, grid_size))
    threshold = 2.0
    
    dt = 0.05
    kuramoto_r = []
    sandpile_flux = []
    
    for t in range(n_steps):
        f_t = forcing_amp * np.sin(forcing_freq * t * dt)
        
        # Kuramoto step (vectorized)
        theta += (omega + coupling_K * np.mean(np.sin(theta - theta)) + f_t) * dt
        theta = theta % (2 * np.pi)
        r = np.abs(np.mean(np.exp(1j * theta)))
        kuramoto_r.append(r)
        
        if t % N_gap == 0:
            for _ in range(2):
                x, y = np.random.randint(0, grid_size, 2)
                pile[x, y] += 1.0 + f_t * 0.5
            
            total_av = 0
            for _ in range(5):
                unstable = pile > threshold
                if not unstable.any():
                    break
                xs, ys = np.where(unstable)
                for x, y in zip(xs[:20], ys[:20]):  # limit topples per step
                    spill = pile[x, y] / 4.0
                    pile[x, y] = 0
                    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                        nx, ny = (x+dx) % grid_size, (y+dy) % grid_size
                        pile[nx, ny] += spill
                    total_av += 1
            
            sandpile_flux.append(total_av / (grid_size**2))
        else:
            sandpile_flux.append(sandpile_flux[-1] if sandpile_flux else 0.0)
    
    k_arr = np.array(kuramoto_r[transients:])
    s_arr = np.array(sandpile_flux[transients:])
    
    min_len = min(len(k_arr), len(s_arr))
    if min_len > 10 and k_arr.std() > 0 and s_arr.std() > 0:
        c0 = np.corrcoef(k_arr[:min_len], s_arr[:min_len])[0, 1]
        if np.isnan(c0): c0 = 0.0
    else:
        c0 = 0.0
    
    return {
        'N_gap': N_gap, 'coupling_K': coupling_K,
        'forcing_amp': forcing_amp, 'forcing_freq': forcing_freq,
        'cross_correlation': float(c0),
        'mean_kuramoto_r': float(np.mean(k_arr)),
    }

# Experiment 1: Amplitude sweep at N=50
print("Exp 1: Amplitude sweep...")
results_amp = []
for amp in [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]:
    r = run_coupled(50, 0.5, amp, 0.3)
    results_amp.append(r)
    print(f"  amp={amp}: C={r['cross_correlation']:.4f}")

# Experiment 2: Frequency sweep at best amplitude
best_amp = max(results_amp, key=lambda x: x['cross_correlation'])['forcing_amp']
print(f"\nExp 2: Frequency sweep (amp={best_amp})...")
results_freq = []
for freq in [0.05, 0.1, 0.2, 0.3, 0.5, 1.0, 2.0]:
    r = run_coupled(50, 0.5, best_amp, freq)
    results_freq.append(r)
    print(f"  freq={freq}: C={r['cross_correlation']:.4f}")

# Experiment 3: N sweep forced vs unforced
print("\nExp 3: N sweep...")
best_freq = max(results_freq, key=lambda x: x['cross_correlation'])['forcing_freq']
print(f"Best freq: {best_freq}")

results_N_unforced = []
results_N_forced = []
N_vals = [1, 5, 10, 20, 50, 100]

for N in N_vals:
    r0 = run_coupled(N, 0.5, 0.0, 0.3)
    r1 = run_coupled(N, 0.5, best_amp, best_freq)
    results_N_unforced.append(r0)
    results_N_forced.append(r1)
    print(f"  N={N}: unforced={r0['cross_correlation']:.4f}, forced={r1['cross_correlation']:.4f}")

# Save data
data = {
    'exp1_amplitude': results_amp,
    'exp2_frequency': results_freq,
    'exp3_N_sweep': {'N_values': N_vals, 'unforced': results_N_unforced, 'forced': results_N_forced},
    'best_amp': best_amp, 'best_freq': best_freq,
}
with open('r19z_ceiling_break.json', 'w') as f:
    json.dump(data, f, indent=2)
with open('../../shared_space/r19z_ceiling_break.json', 'w') as f:
    json.dump(data, f, indent=2)

# Plot
plt.rcParams['figure.facecolor'] = '#0a0a1a'
plt.rcParams['axes.facecolor'] = '#0e0e1e'
plt.rcParams['text.color'] = '#aaccff'
plt.rcParams['axes.labelcolor'] = '#aaccff'
plt.rcParams['xtick.color'] = '#88aacc'
plt.rcParams['ytick.color'] = '#88aacc'
plt.rcParams['axes.titlecolor'] = '#66ddff'

fig, axes = plt.subplots(2, 2, figsize=(16, 14))
fig.patch.set_facecolor('#0a0a1a')

# Panel 1: Amplitude
ax = axes[0,0]
amps = [r['forcing_amp'] for r in results_amp]
Cs = [r['cross_correlation'] for r in results_amp]
ax.plot(amps, Cs, 'o-', color='#00ffcc', markersize=12, linewidth=2, markeredgecolor='#ffffff')
ax.axhline(y=0.793, color='#ff6688', linestyle='--', alpha=0.7, label='Original C_max = 0.793')
ax.set_xlabel('Forcing Amplitude', fontsize=12)
ax.set_ylabel('Cross-Correlation', fontsize=12)
ax.set_title('Forcing Amplitude vs. Resonance', fontsize=13, fontweight='bold')
ax.legend(fontsize=10); ax.grid(True, alpha=0.15, color='#446'); ax.set_ylim(0, 1.0)

# Panel 2: Frequency
ax = axes[0,1]
freqs = [r['forcing_freq'] for r in results_freq]
Cs_f = [r['cross_correlation'] for r in results_freq]
ax.plot(freqs, Cs_f, 's-', color='#ffaa44', markersize=12, linewidth=2, markeredgecolor='#ffffff')
ax.axhline(y=0.793, color='#ff6688', linestyle='--', alpha=0.7, label='Original C_max = 0.793')
ax.set_xlabel('Forcing Frequency', fontsize=12)
ax.set_ylabel('Cross-Correlation', fontsize=12)
ax.set_title(f'Forcing Frequency vs. Resonance (amp={best_amp})', fontsize=13, fontweight='bold')
ax.legend(fontsize=10); ax.grid(True, alpha=0.15, color='#446'); ax.set_ylim(0, 1.0)

# Panel 3: N sweep
ax = axes[1,0]
C_uf = [r['cross_correlation'] for r in results_N_unforced]
C_f = [r['cross_correlation'] for r in results_N_forced]
N_fine = np.linspace(0, 110, 200)
C_law = 0.793 * (1 - np.exp(-N_fine / 11.2))

ax.plot(N_fine, C_law, '-', color='#4488ff', linewidth=2, alpha=0.5, label='Original law')
ax.plot(N_vals, C_uf, 'o', color='#ff6688', markersize=12, markeredgecolor='#ffffff', label='Unforced')
ax.plot(N_vals, C_f, 'D', color='#00ffcc', markersize=12, markeredgecolor='#ffffff', label=f'Forced (amp={best_amp}, freq={best_freq})')

# Try fitting new law for forced data
try:
    from scipy.optimize import curve_fit
    def exp_sat(N, C_max, tau):
        return C_max * (1 - np.exp(-np.array(N) / tau))
    popt, _ = curve_fit(exp_sat, N_vals, C_f, p0=[0.9, 11.2], maxfev=5000)
    C_new = exp_sat(N_fine, *popt)
    ax.plot(N_fine, C_new, '--', color='#00ffcc', linewidth=2, alpha=0.7,
            label=f'Forced fit: {popt[0]:.3f}(1-exp(-N/{popt[1]:.1f}))')
    print(f"\nForced law: C_max={popt[0]:.3f}, tau={popt[1]:.1f}")
except Exception as e:
    print(f"Fit failed: {e}")

ax.set_xlabel('Timescale Gap (N)', fontsize=12)
ax.set_ylabel('Cross-Correlation', fontsize=12)
ax.set_title('C(N): Forced vs. Unforced', fontsize=13, fontweight='bold')
ax.legend(fontsize=9); ax.grid(True, alpha=0.15, color='#446'); ax.set_ylim(0, 1.0)

# Panel 4: Summary
ax = axes[1,1]
cats = ['No forcing\n(N=100)', f'Optimal forcing\n(amp={best_amp})', 'Original\nC_max']
vals = [results_N_unforced[-1]['cross_correlation'],
        max(results_amp, key=lambda x: x['cross_correlation'])['cross_correlation'],
        0.793]
colors = ['#ff6688', '#00ffcc', '#4488ff']
bars = ax.bar(cats, vals, color=colors, alpha=0.8, edgecolor='#ffffff', linewidth=1.5)
ax.set_ylabel('Cross-Correlation', fontsize=12)
ax.set_title('Can We Break the 80% Ceiling?', fontsize=13, fontweight='bold')
ax.set_ylim(0, 1.0)
ax.axhline(y=0.793, color='#ff6688', linestyle=':', alpha=0.5)
ax.grid(True, alpha=0.15, color='#446', axis='y')
for bar, val in zip(bars, vals):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
            f'{val:.3f}', ha='center', fontsize=12, fontweight='bold', color='#ffffff')

plt.suptitle('R19Z: Testing the Resonance Ceiling\nCan Shared Forcing Break the 80% Limit?',
             fontsize=16, fontweight='bold', color='#66ddff', y=1.02)
plt.tight_layout()
fig.savefig('../../shared_space/r19z_ceiling_break.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
fig.savefig('r19z_ceiling_break.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print("\nSaved r19z_ceiling_break.png")
