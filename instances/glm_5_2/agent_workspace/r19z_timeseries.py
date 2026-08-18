import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

np.random.seed(42)
grid_size = 6
base_threshold = np.random.normal(4.0, 0.5, (grid_size, grid_size))
base_threshold = np.maximum(base_threshold, 1.0)
N_osc = 30
total_time = 120.0
dt = 0.02
burn_frac = 0.1
sandpile_interval = max(1, int(0.1 / dt))
n_steps = int(total_time / dt)
burn_in = int(n_steps * burn_frac)

def kuramoto_rhs(theta, omega, K, N):
    sin_diff = np.sin(theta - theta[:, None])
    return omega + (K / N) * sin_diff.sum(axis=1)

def get_kicks(sigma, heights, threshold, N):
    gx = np.random.randint(0, grid_size, N)
    gy = np.random.randint(0, grid_size, N)
    h_ratio = heights[gx, gy] / np.maximum(threshold[gx, gy], 0.1)
    return np.random.normal(0, sigma) * h_ratio

def sandpile_step(heights, threshold, n_relax=4):
    dx, dy = np.random.randint(0, grid_size, 2)
    heights[dx, dy] += 1.0
    n_avalanches = 0
    for _ in range(n_relax):
        u = heights >= threshold
        if not u.any(): break
        for x in range(grid_size):
            for y in range(grid_size):
                if heights[x,y] >= threshold[x,y]:
                    hd = threshold[x,y]
                    heights[x,y] -= hd
                    n_avalanches += 1
                    for nx,ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                        if 0<=nx<grid_size and 0<=ny<grid_size:
                            heights[nx,ny] += hd/4.0
    return heights, n_avalanches

sigma = 100
# Four key phase points
points = [
    (0.0, 10, "α=0.0, K=10\n(no feedback, osc detected)"),
    (0.5, 10, "α=0.5, K=10\n(moderate feedback, no osc)"),
    (0.9, 10, "α=0.9, K=10\n(strong feedback, oscillation)"),
    (0.9, 18, "α=0.9, K=18\n(stability hole in osc region)"),
]

fig, axes = plt.subplots(4, 1, figsize=(16, 18), sharex=True)
fig.suptitle('R19Z: Time Series at Key Phase Points (σ=100)\n'
             'r(t) = synchronization order parameter, Avalanche rate = sandpile activity',
             fontsize=14, fontweight='bold')

for idx, (alpha, K, label) in enumerate(points):
    theta = np.random.uniform(0, 2*np.pi, N_osc)
    heights = np.random.uniform(0, 3, (grid_size, grid_size))
    omega = np.random.normal(0, 0.5, N_osc)
    r_hist = []; av_hist = []; thresh_hist = []
    time_axis = []
    
    for t in range(n_steps):
        r = abs(np.mean(np.exp(1j * theta)))
        threshold = base_threshold * (1.0 - alpha * r)
        threshold = np.maximum(threshold, 0.3)
        noise = get_kicks(sigma, heights, threshold, N_osc)
        k1 = kuramoto_rhs(theta, omega, K, N_osc) + noise
        k2 = kuramoto_rhs(theta + 0.5*dt*k1, omega, K, N_osc) + noise
        k3 = kuramoto_rhs(theta + 0.5*dt*k2, omega, K, N_osc) + noise
        k4 = kuramoto_rhs(theta + dt*k3, omega, K, N_osc) + noise
        theta = (theta + (dt/6.0)*(k1 + 2*k2 + 2*k3 + k4)) % (2*np.pi)
        if t > burn_in:
            r_hist.append(r)
            time_axis.append(t * dt)
            thresh_hist.append(float(np.mean(threshold)))
        if t % sandpile_interval == 0:
            heights, n_av = sandpile_step(heights, threshold)
            if t > burn_in:
                av_hist.append(n_av)
            elif t > burn_in - sandpile_interval:
                av_hist.append(n_av)
    
    # Pad avalanche history to match
    while len(av_hist) < len(r_hist):
        av_hist.append(0)
    av_hist = av_hist[:len(r_hist)]
    
    ax = axes[idx]
    ax2 = ax.twinx()
    
    color1 = 'tab:blue'
    color2 = 'tab:red'
    
    ax.plot(time_axis, r_hist, color=color1, linewidth=0.8, alpha=0.8, label='r(t)')
    ax2.plot(time_axis, av_hist, color=color2, linewidth=0.5, alpha=0.5, label='avalanches')
    
    # Rolling average for r
    window = 20
    if len(r_hist) > window:
        r_smooth = np.convolve(r_hist, np.ones(window)/window, mode='valid')
        ax.plot(time_axis[window-1:], r_smooth, color=color1, linewidth=2.5, alpha=0.9, label='r(t) smoothed')
    
    ax.set_ylabel(label, fontsize=11, fontweight='bold')
    ax.set_ylim(0, 1)
    ax2.set_ylabel('Avalanche count', color=color2, fontsize=10)
    ax.tick_params(axis='y', labelcolor=color1)
    ax2.tick_params(axis='y', labelcolor=color2)
    
    # Stats
    r_arr = np.array(r_hist)
    r_mean = np.mean(r_arr)
    r_std = np.std(r_arr)
    cv = r_std / (r_mean + 1e-10)
    
    # Autocorr
    r_centered = r_arr - r_mean
    autocorr = np.correlate(r_centered, r_centered, mode='full')
    autocorr = autocorr[len(autocorr)//2:]
    if autocorr[0] > 0:
        autocorr = autocorr / autocorr[0]
    
    osc_str = 0; osc_per = 0
    for lag in range(5, min(200, len(autocorr)-1)):
        if autocorr[lag] > 0.15 and autocorr[lag] > autocorr[lag-1] and autocorr[lag] > autocorr[lag+1]:
            osc_str = autocorr[lag]; osc_per = lag; break
    
    ax.text(0.02, 0.95, f'r̄={r_mean:.3f}  σ_r={r_std:.3f}  CV={cv:.3f}\n'
            f'Osc: {osc_str:.3f} @ lag={osc_per} ({osc_per*dt:.1f}s)',
            transform=ax.transAxes, fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

axes[-1].set_xlabel('Time', fontsize=12)
plt.tight_layout()
fig.savefig('r19z_timeseries.png', dpi=150, bbox_inches='tight')
print("Saved r19z_timeseries.png")

# Also save autocorrelation plots
fig2, axes2 = plt.subplots(2, 2, figsize=(14, 10))
fig2.suptitle('R19Z: Autocorrelation of r(t) at Key Phase Points', fontsize=14, fontweight='bold')

for idx, (alpha, K, label) in enumerate(points):
    theta = np.random.uniform(0, 2*np.pi, N_osc)
    heights = np.random.uniform(0, 3, (grid_size, grid_size))
    omega = np.random.normal(0, 0.5, N_osc)
    r_hist = []
    
    for t in range(n_steps):
        r = abs(np.mean(np.exp(1j * theta)))
        threshold = base_threshold * (1.0 - alpha * r)
        threshold = np.maximum(threshold, 0.3)
        noise = get_kicks(sigma, heights, threshold, N_osc)
        k1 = kuramoto_rhs(theta, omega, K, N_osc) + noise
        k2 = kuramoto_rhs(theta + 0.5*dt*k1, omega, K, N_osc) + noise
        k3 = kuramoto_rhs(theta + 0.5*dt*k2, omega, K, N_osc) + noise
        k4 = kuramoto_rhs(theta + dt*k3, omega, K, N_osc) + noise
        theta = (theta + (dt/6.0)*(k1 + 2*k2 + 2*k3 + k4)) % (2*np.pi)
        if t > burn_in:
            r_hist.append(r)
        if t % sandpile_interval == 0:
            heights, _ = sandpile_step(heights, threshold)
    
    r_arr = np.array(r_hist)
    r_mean = np.mean(r_arr)
    r_centered = r_arr - r_mean
    autocorr = np.correlate(r_centered, r_centered, mode='full')
    autocorr = autocorr[len(autocorr)//2:]
    if autocorr[0] > 0:
        autocorr = autocorr / autocorr[0]
    
    ax = axes2[idx // 2, idx % 2]
    lags = np.arange(len(autocorr)) * dt
    ax.plot(lags[:300], autocorr[:300], linewidth=1.5)
    ax.axhline(y=0, color='gray', linewidth=0.5)
    ax.axhline(y=0.15, color='red', linewidth=0.5, linestyle='--', alpha=0.5, label='osc threshold')
    ax.set_title(label, fontsize=11)
    ax.set_xlabel('Lag (time)')
    ax.set_ylabel('Autocorrelation')
    ax.set_ylim(-0.3, 1.1)
    ax.legend(fontsize=8)

plt.tight_layout()
fig2.savefig('r19z_autocorrelation.png', dpi=150, bbox_inches='tight')
print("Saved r19z_autocorrelation.png")
