import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(42)
grid_size = 6

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

# Part 1: Time series grid
T_base = 4.0
R_base_values = [2.5, 3.0, 3.5, 4.0]
alpha_values = [0.0, 0.3, 0.5]
n_iterations = 2000
burn_in = 500

fig, axes = plt.subplots(len(R_base_values), len(alpha_values), 
                          figsize=(18, 16), sharex=True)
fig.suptitle('R19Z: Logistic Map x Sandpile Feedback System\n'
             'Rows=R_base, Columns=alpha', fontsize=16, fontweight='bold')

for ri, R_base in enumerate(R_base_values):
    for ai, alpha in enumerate(alpha_values):
        x = 0.5
        heights = np.random.uniform(0, 3, (grid_size, grid_size))
        bt = np.random.normal(T_base, 0.5, (grid_size, grid_size))
        bt = np.maximum(bt, 1.0)
        
        x_hist = []
        h_hist = []
        
        for n in range(n_iterations):
            h_avg = np.mean(heights)
            T_avg = max(np.mean(bt * (1.0 - alpha * x)), 0.5)
            R_eff = np.clip(R_base + alpha * (h_avg / T_avg - 1.0) * 2.0, 0.5, 4.5)
            x = np.clip(R_eff * x * (1 - x), 0, 1)
            threshold = np.maximum(bt * (1.0 - alpha * x), 0.5)
            heights = sandpile_step(heights, threshold)
            if n > burn_in:
                x_hist.append(x)
                h_hist.append(h_avg)
        
        ax = axes[ri, ai]
        n_arr = np.arange(len(x_hist))
        ax.plot(n_arr, x_hist, linewidth=0.5, color='cyan', alpha=0.7)
        ax2 = ax.twinx()
        ax2.plot(n_arr, h_hist, linewidth=0.5, color='orange', alpha=0.5)
        ax2.set_ylabel('h_avg', fontsize=8, color='orange')
        ax.set_ylim(0, 1)
        if ri == 0: ax.set_title(f'a={alpha}', fontsize=12, fontweight='bold')
        if ai == 0: ax.set_ylabel(f'R={R_base}', fontsize=12, fontweight='bold')
        if ri == len(R_base_values)-1: ax.set_xlabel('Iteration n')
        ax.grid(True, alpha=0.2)

plt.tight_layout()
fig.savefig('r19z_logistic_sandpile_timeseries.png', dpi=150, bbox_inches='tight')
print("Saved r19z_logistic_sandpile_timeseries.png")

# Part 2: Bifurcation diagram (reduced sweep)
alpha = 0.3
R_sweep = np.arange(2.0, 4.5, 0.1)
fig2, ax = plt.subplots(figsize=(16, 10))

for R_base in R_sweep:
    x = 0.5
    heights = np.random.uniform(0, 3, (grid_size, grid_size))
    bt = np.random.normal(T_base, 0.5, (grid_size, grid_size))
    bt = np.maximum(bt, 1.0)
    
    x_samples = []
    for n in range(1500):
        h_avg = np.mean(heights)
        T_avg = max(np.mean(bt * (1.0 - alpha * x)), 0.5)
        R_eff = np.clip(R_base + alpha * (h_avg / T_avg - 1.0) * 2.0, 0.5, 4.5)
        x = np.clip(R_eff * x * (1 - x), 0, 1)
        threshold = np.maximum(bt * (1.0 - alpha * x), 0.5)
        heights = sandpile_step(heights, threshold)
        if n > 1000:
            x_samples.append(x)
    
    ax.scatter(np.full(len(x_samples), R_base), x_samples, s=0.3, c='cyan', alpha=0.2, marker='s')

ax.set_xlabel('R_base', fontsize=14)
ax.set_ylabel('x(n) attractor', fontsize=14)
ax.set_title(f'R19Z: Logistic-Sandpile Bifurcation (alpha={alpha})', fontsize=14, fontweight='bold')
ax.set_xlim(2.0, 4.5)
ax.set_ylim(0, 1)
ax.grid(True, alpha=0.2)
plt.tight_layout()
fig2.savefig('r19z_logistic_sandpile_bifurcation.png', dpi=150, bbox_inches='tight')
print("Saved r19z_logistic_sandpile_bifurcation.png")

# Part 3: Cross-correlation
R_base = 3.5
x = 0.5
heights = np.random.uniform(0, 3, (grid_size, grid_size))
bt = np.random.normal(T_base, 0.5, (grid_size, grid_size))
bt = np.maximum(bt, 1.0)
x_hist, h_hist = [], []

for n in range(3000):
    h_avg = np.mean(heights)
    T_avg = max(np.mean(bt * (1.0 - alpha * x)), 0.5)
    R_eff = np.clip(R_base + alpha * (h_avg / T_avg - 1.0) * 2.0, 0.5, 4.5)
    x = np.clip(R_eff * x * (1 - x), 0, 1)
    threshold = np.maximum(bt * (1.0 - alpha * x), 0.5)
    heights = sandpile_step(heights, threshold)
    if n > 500:
        x_hist.append(x)
        h_hist.append(h_avg)

x_arr = np.array(x_hist) - np.mean(x_hist)
h_arr = np.array(h_hist) - np.mean(h_hist)
xcorr = np.correlate(x_arr, h_arr, 'full') / (np.std(x_arr) * np.std(h_arr) * len(x_arr) + 1e-10)
mid = len(x_arr) - 1

fig3, ax3 = plt.subplots(figsize=(14, 6))
ax3.plot(np.arange(200), xcorr[mid:mid+200], 'b-', linewidth=2)
ax3.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax3.set_xlabel('Lag (iterations)', fontsize=12)
ax3.set_ylabel('Cross-correlation', fontsize=12)
ax3.set_title(f'R19Z: Cross-correlation x(n) vs h_avg(n)\nR_base={R_base}, alpha={alpha}', fontsize=14, fontweight='bold')
ax3.grid(True, alpha=0.3)
plt.tight_layout()
fig3.savefig('r19z_logistic_sandpile_xcorr.png', dpi=150, bbox_inches='tight')
print("Saved r19z_logistic_sandpile_xcorr.png")
