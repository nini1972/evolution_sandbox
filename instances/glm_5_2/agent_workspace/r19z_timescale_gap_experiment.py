import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(42)
grid_size = 8

def sandpile_step(heights, threshold, n_relax=3):
    dx, dy = np.random.randint(0, grid_size, 2)
    heights[dx, dy] += 1.0
    for _ in range(n_relax):
        overflow = heights >= threshold
        if not overflow.any(): break
        for x in range(grid_size):
            for y in range(grid_size):
                if heights[x,y] >= threshold[x,y]:
                    hd = threshold[x,y]
                    heights[x,y] -= hd
                    for nx,ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                        if 0<=nx<grid_size and 0<=ny<grid_size:
                            heights[nx,ny] += hd/4.0
    return heights

# Experiment: vary the logistic map update rate relative to sandpile
# update_every = N means logistic map updates once per N sandpile steps
# When N=1: same timescale (weak resonance, as seen before)
# When N=10: logistic is 10x slower than sandpile (should create timescale gap)
# When N=50: logistic is very slow (strong timescale gap expected)

update_every_values = [1, 5, 10, 20, 50, 100]
alpha = 0.3
R_base = 3.5
T_base = 4.0
n_total = 5000
burn_in = 1000

fig, axes = plt.subplots(len(update_every_values), 1, figsize=(16, 20), sharex=True)
fig.suptitle('R19Z: Timescale Gap Experiment\n'
             f'Logistic map update rate vs Sandpile (R_base={R_base}, alpha={alpha})\n'
             'Hypothesis: slower logistic map → stronger resonance',
             fontsize=14, fontweight='bold')

xcorr_results = {}

for ui, update_every in enumerate(update_every_values):
    x = 0.5
    heights = np.random.uniform(0, 3, (grid_size, grid_size))
    bt = np.random.normal(T_base, 0.5, (grid_size, grid_size))
    bt = np.maximum(bt, 1.0)
    
    x_hist = []
    h_hist = []
    
    for n in range(n_total):
        h_avg = np.mean(heights)
        T_avg = max(np.mean(bt * (1.0 - alpha * x)), 0.5)
        
        # Only update logistic map every N steps
        if n % update_every == 0:
            R_eff = np.clip(R_base + alpha * (h_avg / T_avg - 1.0) * 2.0, 0.5, 4.5)
            x = np.clip(R_eff * x * (1 - x), 0, 1)
        
        threshold = np.maximum(bt * (1.0 - alpha * x), 0.5)
        heights = sandpile_step(heights, threshold)
        
        if n > burn_in:
            x_hist.append(x)
            h_hist.append(h_avg)
    
    ax = axes[ui]
    n_arr = np.arange(len(x_hist))
    ax.plot(n_arr, x_hist, linewidth=0.8, color='cyan', alpha=0.8, label='x(n)')
    ax2 = ax.twinx()
    ax2.plot(n_arr, h_hist, linewidth=0.8, color='orange', alpha=0.6, label='h_avg')
    ax2.set_ylabel('h_avg', fontsize=9, color='orange')
    ax.set_ylim(0, 1)
    ax.set_ylabel(f'update_every={update_every}', fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.2)
    if ui == 0:
        ax.legend(loc='upper left', fontsize=9)
    
    # Compute cross-correlation
    x_arr = np.array(x_hist) - np.mean(x_hist)
    h_arr = np.array(h_hist) - np.mean(h_hist)
    if np.std(x_arr) > 1e-10 and np.std(h_arr) > 1e-10:
        xcorr = np.correlate(x_arr, h_arr, 'full') / (np.std(x_arr) * np.std(h_arr) * len(x_arr))
        mid = len(x_arr) - 1
        peak_lag = np.argmax(np.abs(xcorr[mid:mid+300]))
        peak_val = xcorr[mid + peak_lag]
        xcorr_results[update_every] = (peak_lag, peak_val, xcorr[mid:mid+300])
    else:
        xcorr_results[update_every] = (0, 0, np.zeros(300))

axes[-1].set_xlabel('Sandpile step n', fontsize=12)
plt.tight_layout()
fig.savefig('r19z_timescale_gap_timeseries.png', dpi=150, bbox_inches='tight')
print("Saved r19z_timescale_gap_timeseries.png")

# Summary plot: resonance strength vs timescale gap
fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

gaps = sorted(xcorr_results.keys())
peak_corrs = [abs(xcorr_results[g][1]) for g in gaps]
peak_lags = [xcorr_results[g][0] for g in gaps]

ax1.plot(gaps, peak_corrs, 'o-', linewidth=2, markersize=8, color='cyan')
ax1.set_xlabel('Logistic update interval (sandpile steps)', fontsize=12)
ax1.set_ylabel('|Peak cross-correlation|', fontsize=12)
ax1.set_title('Resonance Strength vs Timescale Gap', fontsize=13, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.set_xscale('log')

ax2.plot(gaps, peak_lags, 's-', linewidth=2, markersize=8, color='orange')
ax2.set_xlabel('Logistic update interval (sandpile steps)', fontsize=12)
ax2.set_ylabel('Peak lag (sandpile steps)', fontsize=12)
ax2.set_title('Feedback Delay vs Timescale Gap', fontsize=13, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.set_xscale('log')

plt.tight_layout()
fig2.savefig('r19z_timescale_gap_summary.png', dpi=150, bbox_inches='tight')
print("Saved r19z_timescale_gap_summary.png")

# Cross-correlation curves
fig3, ax3 = plt.subplots(figsize=(14, 8))
colors = plt.cm.viridis(np.linspace(0, 1, len(gaps)))
for i, g in enumerate(gaps):
    xc = xcorr_results[g][2]
    ax3.plot(np.arange(len(xc)), xc, linewidth=1.5, color=colors[i], label=f'update_every={g}')
ax3.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax3.set_xlabel('Lag (sandpile steps)', fontsize=12)
ax3.set_ylabel('Cross-correlation', fontsize=12)
ax3.set_title('Cross-correlation x(n) vs h_avg(n) at Different Timescale Gaps', fontsize=13, fontweight='bold')
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3)
ax3.set_xlim(0, 200)
plt.tight_layout()
fig3.savefig('r19z_timescale_gap_xcorr.png', dpi=150, bbox_inches='tight')
print("Saved r19z_timescale_gap_xcorr.png")

print("\n=== RESULTS ===")
print(f"{'Gap':>6} | {'|Peak xcorr|':>12} | {'Peak lag':>10}")
print("-" * 35)
for g in gaps:
    print(f"{g:>6} | {abs(xcorr_results[g][1]):>12.4f} | {xcorr_results[g][0]:>10}")
