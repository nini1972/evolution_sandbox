# R19Z Turn 14b: Critical test — does the resonance island width depend on simulation length?
# And does the internal oscillation period lengthen with f?
import numpy as np, json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from r19z_deep_lib import run_gs_sandpile, run_gs_only

# Test at 4 key f values with multiple run lengths
f_test = [0.064, 0.070, 0.076]
configs = [
    ('short', 1000, 400),
    ('medium', 2000, 800),
    ('long', 4000, 1600),
]

print('=== Length dependence test ===')
length_results = []
for f in f_test:
    for name, n_steps, burn_in in configs:
        res = run_gs_sandpile(f, n_steps=n_steps, N_gap=10, burn_in=burn_in, seed=42)
        C = res['best_corr']
        length_results.append({'f': f, 'config': name, 'C': C, 'gs_std': res['gs_std']})
        print(f'  f={f:.3f} ({name:6s}): C={C:+.4f}, gs_std={res["gs_std"]:.4f}')

# === Autocorrelation profile — full lag scan ===
print('\n=== Autocorrelation lag scan ===')
ac_results = {}
for f in f_test:
    comp_sig, mv_sig = run_gs_only(f, n_steps=4000, burn_in=1600)
    s = int(4000 * 0.1)
    x = comp_sig[s:] - np.mean(comp_sig[s:])
    lags = range(0, 300, 5)
    acs = []
    for lag in lags:
        if lag == 0:
            acs.append(1.0)
        elif lag < len(x):
            c = np.corrcoef(x[:len(x)-lag], x[lag:])[0,1]
            acs.append(0.0 if np.isnan(c) else float(c))
        else:
            acs.append(0.0)
    ac_results[f] = (list(lags), acs)
    # Find first zero crossing
    first_zero = None
    for i in range(1, len(acs)):
        if acs[i] * acs[i-1] < 0:
            first_zero = lags[i]
            break
    print(f'  f={f:.3f}: first zero-crossing at lag={first_zero}, min ac={min(acs):.3f} at lag={list(lags)[np.argmin(acs)]}')

# === Visualization ===
fig = plt.figure(figsize=(16, 10))
fig.subplots_adjust(hspace=0.35, wspace=0.3)

# Panel 1: Length dependence
ax1 = fig.add_subplot(2, 2, 1)
for f in f_test:
    fr = [r for r in length_results if r['f'] == f]
    xs = [r['config'] for r in fr]
    ys = [r['C'] for r in fr]
    ax1.plot(xs, ys, 'o-', ms=8, label=f'f={f:.3f}')
ax1.axhline(0, color='gray', ls='--', lw=0.5)
ax1.set_xlabel('Simulation length')
ax1.set_ylabel('Cross-correlation C')
ax1.set_title('Resonance vs Simulation Length')
ax1.legend()

# Panel 2: Autocorrelation profiles
ax2 = fig.add_subplot(2, 2, 2)
colors = ['orange', 'red', 'darkred']
for i, (f, (lags, acs)) in enumerate(ac_results.items()):
    ax2.plot(lags, acs, 'o-', ms=3, label=f'f={f:.3f}', color=colors[i])
ax2.axhline(0, color='gray', ls='--', lw=0.5)
ax2.set_xlabel('Lag')
ax2.set_ylabel('Autocorrelation')
ax2.set_title('Uncoupled GS: Full Autocorrelation Profile')
ax2.legend()

# Panel 3: Oscillation period estimate vs f
ax3 = fig.add_subplot(2, 2, 3)
periods = []
for f, (lags, acs) in ac_results.items():
    # Period = 2 * first zero crossing (full oscillation cycle)
    first_zero = None
    for i in range(1, len(acs)):
        if acs[i] * acs[i-1] < 0:
            first_zero = lags[i]
            break
    # Also find first minimum
    min_idx = np.argmin(acs)
    min_lag = lags[min_idx]
    periods.append((f, first_zero, min_lag))
    ax3.plot(f, min_lag, 'rs', ms=10)
    if first_zero:
        ax3.plot(f, first_zero, 'b^', ms=10)
ax3.set_xlabel('f')
ax3.set_ylabel('Lag')
ax3.set_title('Internal Oscillation Period vs f')
ax3.legend(['First minimum', 'First zero-crossing'])

# Panel 4: Sample time series
ax4 = fig.add_subplot(2, 2, 4)
for i, f in enumerate(f_test):
    comp_sig, _ = run_gs_only(f, n_steps=2000, burn_in=800)
    ax4.plot(comp_sig[200:], alpha=0.7, label=f'f={f:.3f}')
ax4.set_xlabel('Time')
ax4.set_ylabel('std(v) (complexity)')
ax4.set_title('Uncoupled GS Time Series')
ax4.legend()

fig.suptitle('R19Z Turn 14b: Resonance Island Length Dependence & Internal Oscillation Period',
             fontsize=14, fontweight='bold')
fig.savefig('r19z_island_length.png', dpi=150, bbox_inches='tight')
print('\nSaved r19z_island_length.png')

# Save data
with open('r19z_island_length_data.json', 'w') as fp:
    json.dump({
        'length_results': length_results,
        'ac_results': {str(k): {'lags': v[0], 'acs': v[1]} for k, v in ac_results.items()},
        'periods': periods,
    }, fp, indent=2)
print('Done!')
