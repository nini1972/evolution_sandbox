import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(42)
grid_size = 6
base_threshold = np.random.normal(4.0, 0.5, (grid_size, grid_size))
base_threshold = np.maximum(base_threshold, 1.0)
N_osc = 30
total_time = 100.0
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
alpha = 0.9
K_values = [6, 8, 10, 12, 14, 16, 20, 30]

freq_data = []

for ki, K in enumerate(K_values):
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
    r_detrended = r_arr - np.mean(r_arr)
    
    # FFT
    fft_vals = np.fft.rfft(r_detrended)
    freqs = np.fft.rfftfreq(len(r_detrended), d=dt)
    power = np.abs(fft_vals)**2
    
    if power[0] > 0:
        power_norm = power / power[0]
    else:
        power_norm = power
    
    if len(power) > 2:
        peak_idx = np.argmax(power[1:]) + 1
        peak_freq = freqs[peak_idx]
        peak_power = power_norm[peak_idx]
    else:
        peak_freq = 0
        peak_power = 0
    
    freq_data.append((K, peak_freq, peak_power, 1/peak_freq if peak_freq > 0 else 0))
    print(f"K={K}: freq={peak_freq:.4f}, power={peak_power:.4f}, period={1/peak_freq if peak_freq > 0 else 0:.2f}")

# Summary plot
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
fig.suptitle(f'R19Z: Oscillation Frequency vs Coupling K (α={alpha}, σ={sigma})',
             fontsize=14, fontweight='bold')

Ks = [d[0] for d in freq_data]
freqs_dom = [d[1] for d in freq_data]
powers = [d[2] for d in freq_data]
periods = [d[3] if d[3] < 200 else 0 for d in freq_data]

colors = ['red' if p > 0.01 else 'green' for p in powers]

ax1.bar(Ks, freqs_dom, color=colors, alpha=0.7, width=0.8)
ax1.set_xlabel('Coupling K', fontsize=12)
ax1.set_ylabel('Dominant Frequency', fontsize=12)
ax1.set_title('Oscillation Frequency (red=oscillating, green=stable)')
ax1.grid(True, alpha=0.3)

ax2.bar(Ks, periods, color=colors, alpha=0.7, width=0.8)
ax2.set_xlabel('Coupling K', fontsize=12)
ax2.set_ylabel('Oscillation Period (time units)', fontsize=12)
ax2.set_title('Oscillation Period')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
fig.savefig('r19z_frequency_vs_K.png', dpi=150, bbox_inches='tight')
print("Saved r19z_frequency_vs_K.png")

# FFT spectrum for 4 representative K values
fig2, axes = plt.subplots(4, 1, figsize=(14, 12), sharex=True)
fig2.suptitle(f'R19Z: Power Spectrum at α={alpha}, σ={sigma}', fontsize=14, fontweight='bold')
repr_Ks = [6, 10, 16, 20]

for idx, K in enumerate(repr_Ks):
    if K in K_values:
        ki = K_values.index(K)
    else:
        continue
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
    r_detrended = r_arr - np.mean(r_arr)
    fft_vals = np.fft.rfft(r_detrended)
    freqs = np.fft.rfftfreq(len(r_detrended), d=dt)
    power = np.abs(fft_vals)**2
    if power[0] > 0:
        power_norm = power / power[0]
    else:
        power_norm = power
    
    axes[idx].plot(freqs[:150], power_norm[:150], linewidth=1.5, color='cyan')
    axes[idx].fill_between(freqs[:150], 0, power_norm[:150], alpha=0.3, color='cyan')
    axes[idx].set_ylabel(f'K={K}', fontsize=11, fontweight='bold')
    axes[idx].grid(True, alpha=0.2)

axes[-1].set_xlabel('Frequency', fontsize=12)
plt.tight_layout()
fig2.savefig('r19z_fft_spectrum.png', dpi=150, bbox_inches='tight')
print("Saved r19z_fft_spectrum.png")
