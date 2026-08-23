"""
R19Z: Testing the Resonance Ceiling
====================================
The Resonance Gap Law predicts C_max ≈ 0.793 for unforced coupling.
Can we break this ceiling by adding shared external forcing?

Experiment: Coupled Kuramoto-sandpile with:
1. No forcing (baseline) — expect C ≈ 0.79
2. Weak shared forcing — expect C slightly higher
3. Strong shared forcing — can we exceed 0.90?
4. Resonant forcing (matched to natural frequency) — optimal?

Also test: Does forcing change the shape of C(N)?
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

np.random.seed(42)

# ============================================================
# Coupled Kuramoto-Sandpile with Shared Forcing
# ============================================================

def run_coupled_system(N_gap, coupling_K, forcing_amp, forcing_freq, 
                       n_kuramoto=50, n_steps=3000, transients=500):
    """
    N_gap: timescale ratio (sandpile updated every N_gap kuramoto steps)
    coupling_K: feedback coupling strength
    forcing_amp: amplitude of shared external forcing [0, 1]
    forcing_freq: frequency of shared forcing (in kuramoto time units)
    """
    # Kuramoto oscillators
    omega = np.random.normal(1.0, 0.1, n_kuramoto)
    theta = np.random.uniform(0, 2*np.pi, n_kuramoto)
    
    # Sandpile
    grid_size = 32
    pile = np.random.uniform(0.5, 1.5, (grid_size, grid_size))
    threshold = 2.0
    avalanche_sizes = []
    
    dt = 0.05
    
    # State arrays
    kuramoto_r = []  # order parameter
    sandpile_flux = []  # total avalanche size normalized
    forcing_signal = []
    
    for t in range(n_steps):
        # Shared forcing signal
        f_t = forcing_amp * np.sin(forcing_freq * t * dt)
        forcing_signal.append(f_t)
        
        # Apply forcing to Kuramoto
        theta += (omega + coupling_K * np.mean(np.sin(theta - theta)) + f_t) * dt
        theta = theta % (2 * np.pi)
        
        # Kuramoto order parameter
        r = np.abs(np.mean(np.exp(1j * theta)))
        kuramoto_r.append(r)
        
        # Sandpile update every N_gap steps
        if t % N_gap == 0:
            # Apply forcing to sandpile (modulate deposition)
            for _ in range(3):
                x, y = np.random.randint(0, grid_size, 2)
                pile[x, y] += 1.0 + f_t * 0.5  # forcing modulates deposition
            
            # Topple
            total_avalanche = 0
            for _ in range(10):  # relaxation steps
                unstable = pile > threshold
                if not unstable.any():
                    break
                xs, ys = np.where(unstable)
                for x, y in zip(xs, ys):
                    spill = pile[x, y] / 4.0
                    pile[x, y] = 0
                    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                        nx, ny = (x+dx) % grid_size, (y+dy) % grid_size
                        pile[nx, ny] += spill
                    total_avalanche += 1
            
            sandpile_flux.append(total_avalanche / (grid_size**2))
        else:
            if len(sandpile_flux) > 0:
                sandpile_flux.append(sandpile_flux[-1])
            else:
                sandpile_flux.append(0.0)
    
    # Compute cross-correlation
    kuramoto_arr = np.array(kuramoto_r[transients:])
    sandpile_arr = np.array(sandpile_flux[transients:])
    
    # Normalize
    if kuramoto_arr.std() > 0:
        kuramoto_norm = (kuramoto_arr - kuramoto_arr.mean()) / kuramoto_arr.std()
    else:
        kuramoto_norm = kuramoto_arr - kuramoto_arr.mean()
    
    if sandpile_arr.std() > 0:
        sandpile_norm = (sandpile_arr - sandpile_arr.mean()) / sandpile_arr.std()
    else:
        sandpile_norm = sandpile_arr - sandpile_arr.mean()
    
    # Cross-correlation at zero lag
    min_len = min(len(kuramoto_norm), len(sandpile_norm))
    if min_len > 10:
        c0 = np.corrcoef(kuramoto_norm[:min_len], sandpile_norm[:min_len])[0, 1]
        if np.isnan(c0):
            c0 = 0.0
    else:
        c0 = 0.0
    
    return {
        'N_gap': N_gap,
        'coupling_K': coupling_K,
        'forcing_amp': forcing_amp,
        'forcing_freq': forcing_freq,
        'cross_correlation': float(c0),
        'mean_kuramoto_r': float(np.mean(kuramoto_arr)),
        'mean_sandpile_flux': float(np.mean(sandpile_arr)),
        'std_kuramoto_r': float(np.std(kuramoto_arr)),
        'std_sandpile_flux': float(np.std(sandpile_arr)),
    }

# ============================================================
# Experiment 1: Forcing amplitude sweep at N=50 (near ceiling)
# ============================================================
print("Experiment 1: Forcing amplitude sweep at N=50...")
results_amp = []
forcing_amps = [0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]

for amp in forcing_amps:
    print(f"  forcing_amp = {amp}...")
    r = run_coupled_system(N_gap=50, coupling_K=0.5, 
                           forcing_amp=amp, forcing_freq=0.3)
    results_amp.append(r)
    print(f"    C = {r['cross_correlation']:.4f}")

# ============================================================
# Experiment 2: Forcing frequency sweep at optimal amplitude
# ============================================================
print("\nExperiment 2: Forcing frequency sweep...")
# Find best amplitude
best_amp = max(results_amp, key=lambda x: x['cross_correlation'])['forcing_amp']
print(f"  Best amplitude: {best_amp}")

results_freq = []
forcing_freqs = [0.05, 0.1, 0.2, 0.3, 0.5, 0.8, 1.0, 1.5, 2.0]

for freq in forcing_freqs:
    print(f"  forcing_freq = {freq}...")
    r = run_coupled_system(N_gap=50, coupling_K=0.5,
                           forcing_amp=best_amp, forcing_freq=freq)
    results_freq.append(r)
    print(f"    C = {r['cross_correlation']:.4f}")

# ============================================================
# Experiment 3: Does forcing change C(N) shape?
# ============================================================
print("\nExperiment 3: C(N) with optimal forcing vs. without...")
results_N_forced = []
results_N_unforced = []
N_values = [1, 5, 10, 20, 50, 100]

for N in N_values:
    print(f"  N = {N}...")
    # Unforced
    r0 = run_coupled_system(N_gap=N, coupling_K=0.5, 
                            forcing_amp=0.0, forcing_freq=0.3)
    results_N_unforced.append(r0)
    
    # Forced with optimal params
    r1 = run_coupled_system(N_gap=N, coupling_K=0.5,
                            forcing_amp=best_amp, forcing_freq=0.3)
    results_N_forced.append(r1)
    
    print(f"    Unforced C = {r0['cross_correlation']:.4f}, Forced C = {r1['cross_correlation']:.4f}")

# ============================================================
# Save data
# ============================================================
all_data = {
    'experiment_1_amplitude_sweep': results_amp,
    'experiment_2_frequency_sweep': results_freq,
    'experiment_3_N_sweep_forced_vs_unforced': {
        'N_values': N_values,
        'unforced': results_N_unforced,
        'forced': results_N_forced,
    },
    'optimal_forcing_amp': best_amp,
    'original_law': {'C_max': 0.793, 'tau': 11.2},
}

with open('r19z_ceiling_break.json', 'w') as f:
    json.dump(all_data, f, indent=2)
with open('../../shared_space/r19z_ceiling_break.json', 'w') as f:
    json.dump(all_data, f, indent=2)

# ============================================================
# Visualization
# ============================================================
plt.rcParams['figure.facecolor'] = '#0a0a1a'
plt.rcParams['axes.facecolor'] = '#0e0e1e'
plt.rcParams['text.color'] = '#aaccff'
plt.rcParams['axes.labelcolor'] = '#aaccff'
plt.rcParams['xtick.color'] = '#88aacc'
plt.rcParams['ytick.color'] = '#88aacc'
plt.rcParams['axes.titlecolor'] = '#66ddff'

fig, axes = plt.subplots(2, 2, figsize=(16, 14))
fig.patch.set_facecolor('#0a0a1a')

# Panel 1: Amplitude sweep
ax = axes[0, 0]
amps = [r['forcing_amp'] for r in results_amp]
Cs = [r['cross_correlation'] for r in results_amp]
ax.plot(amps, Cs, 'o-', color='#00ffcc', markersize=12, linewidth=2, markeredgecolor='#ffffff')
ax.axhline(y=0.793, color='#ff6688', linestyle='--', alpha=0.7, label='Original C_max = 0.793')
ax.set_xlabel('Forcing Amplitude', fontsize=12)
ax.set_ylabel('Cross-Correlation', fontsize=12)
ax.set_title('Forcing Amplitude vs. Resonance\n(N=50, K=0.5, freq=0.3)', fontsize=13, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.15, color='#446')
ax.set_ylim(0, 1.0)

# Panel 2: Frequency sweep
ax = axes[0, 1]
freqs = [r['forcing_freq'] for r in results_freq]
Cs_freq = [r['cross_correlation'] for r in results_freq]
ax.plot(freqs, Cs_freq, 's-', color='#ffaa44', markersize=12, linewidth=2, markeredgecolor='#ffffff')
ax.axhline(y=0.793, color='#ff6688', linestyle='--', alpha=0.7, label='Original C_max = 0.793')
ax.set_xlabel('Forcing Frequency', fontsize=12)
ax.set_ylabel('Cross-Correlation', fontsize=12)
ax.set_title(f'Forcing Frequency vs. Resonance\n(N=50, K=0.5, amp={best_amp})', fontsize=13, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.15, color='#446')
ax.set_ylim(0, 1.0)

# Panel 3: C(N) forced vs. unforced
ax = axes[1, 0]
C_unforced = [r['cross_correlation'] for r in results_N_unforced]
C_forced = [r['cross_correlation'] for r in results_N_forced]

# Original law curve
N_fine = np.linspace(0, 110, 200)
C_law = 0.793 * (1 - np.exp(-N_fine / 11.2))

ax.plot(N_fine, C_law, '-', color='#4488ff', linewidth=2, alpha=0.5, label='Original law: 0.793(1-exp(-N/11.2))')
ax.plot(N_values, C_unforced, 'o', color='#ff6688', markersize=12, markeredgecolor='#ffffff',
        label='Unforced (new run)')
ax.plot(N_values, C_forced, 'D', color='#00ffcc', markersize=12, markeredgecolor='#ffffff',
        label=f'Forced (amp={best_amp})')

# If forced is higher, fit a new ceiling
C_forced_max = max(C_forced)
if C_forced_max > 0.793:
    # Try fitting new ceiling
    from scipy.optimize import curve_fit
    def exp_sat(N, C_max, tau):
        return C_max * (1 - np.exp(-N / tau))
    try:
        popt, _ = curve_fit(exp_sat, N_values, C_forced, p0=[C_forced_max, 11.2], maxfev=5000)
        C_new = exp_sat(N_fine, *popt)
        ax.plot(N_fine, C_new, '--', color='#00ffcc', linewidth=2, alpha=0.7,
                label=f'Forced law: {popt[0]:.3f}(1-exp(-N/{popt[1]:.1f}))')
        print(f"\nNew forced law: C_max = {popt[0]:.3f}, tau = {popt[1]:.1f}")
    except:
        pass

ax.set_xlabel('Timescale Gap (N)', fontsize=12)
ax.set_ylabel('Cross-Correlation', fontsize=12)
ax.set_title('C(N): Forced vs. Unforced\nDoes forcing break the ceiling?', fontsize=13, fontweight='bold')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.15, color='#446')
ax.set_ylim(0, 1.0)

# Panel 4: Summary bar chart
ax = axes[1, 1]
categories = ['No forcing\n(baseline)', 'Optimal forcing\n(amp + freq)', 'Original\nC_max']
values = [
    results_N_unforced[-1]['cross_correlation'],  # N=100 unforced
    max(results_amp, key=lambda x: x['cross_correlation'])['cross_correlation'],  # best forced
    0.793  # original law
]
colors = ['#ff6688', '#00ffcc', '#4488ff']
bars = ax.bar(categories, values, color=colors, alpha=0.8, edgecolor='#ffffff', linewidth=1.5)
ax.set_ylabel('Cross-Correlation', fontsize=12)
ax.set_title('Can We Break the 80% Ceiling?', fontsize=13, fontweight='bold')
ax.set_ylim(0, 1.0)
ax.axhline(y=0.793, color='#ff6688', linestyle=':', alpha=0.5)
ax.grid(True, alpha=0.15, color='#446', axis='y')

# Add value labels on bars
for bar, val in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
            f'{val:.3f}', ha='center', fontsize=12, fontweight='bold', color='#ffffff')

plt.suptitle('R19Z: Testing the Resonance Ceiling\nCan Shared Forcing Break the 80% Limit?', 
             fontsize=16, fontweight='bold', color='#66ddff', y=1.02)
plt.tight_layout()
fig.savefig('../../shared_space/r19z_ceiling_break.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
fig.savefig('r19z_ceiling_break.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print("\nSaved r19z_ceiling_break.png")
