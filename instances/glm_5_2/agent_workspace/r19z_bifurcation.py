"""
R19Z Bifurcation: Map the transition from stability to oscillation.
Fix σ=100, scan K in fine steps at α=0.9.
Track: r_mean, r_std, oscillation frequency, oscillation strength.
A Hopf bifurcation would show: r_std increasing from ~0, oscillation frequency appearing at a critical K.
"""
import numpy as np
import json

np.random.seed(42)
grid_size = 6
base_threshold = np.random.normal(4.0, 0.5, (grid_size, grid_size))
base_threshold = np.maximum(base_threshold, 1.0)
N_osc = 30
total_time = 120.0
dt = 0.02
burn_frac = 0.15
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
    avalanche_size = 0
    for _ in range(n_relax):
        u = heights >= threshold
        if not u.any(): break
        for x in range(grid_size):
            for y in range(grid_size):
                if heights[x,y] >= threshold[x,y]:
                    avalanche_size += 1
                    hd = threshold[x,y]
                    heights[x,y] -= hd
                    for nx,ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                        if 0<=nx<grid_size and 0<=ny<grid_size:
                            heights[nx,ny] += hd/4.0
    return heights, avalanche_size

sigma = 100.0
alpha = 0.9
K_values = [6, 8, 10, 12, 14, 16, 18, 20, 25, 30]
results = {}

print(f"Bifurcation scan: α={alpha}, σ={sigma}")
print(f"{'K':>4s} {'r_mean':>8s} {'r_std':>8s} {'osc_str':>8s} {'osc_per':>8s} {'dom_freq':>10s}")

for K in K_values:
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
            heights, av = sandpile_step(heights, threshold)
    
    r_arr = np.array(r_hist)
    r_mean = float(np.mean(r_arr))
    r_std = float(np.std(r_arr))
    
    # Oscillation detection
    osc_strength = 0
    osc_period = 0
    r_centered = r_arr - r_mean
    autocorr = np.correlate(r_centered, r_centered, mode='full')
    autocorr = autocorr[len(autocorr)//2:]
    autocorr = autocorr / (autocorr[0] + 1e-10)
    for lag in range(5, min(300, len(autocorr)-1)):
        if autocorr[lag] > 0.15 and autocorr[lag] > autocorr[lag-1] and autocorr[lag] > autocorr[lag+1]:
            osc_strength = float(autocorr[lag])
            osc_period = lag
            break
    
    # Dominant frequency via FFT
    fft = np.abs(np.fft.rfft(r_centered))
    freqs = np.fft.rfftfreq(len(r_arr), d=dt)
    dom_idx = np.argmax(fft[1:]) + 1  # skip DC
    dom_freq = float(freqs[dom_idx]) if dom_idx < len(freqs) else 0
    
    results[str(K)] = {
        "r_mean": r_mean, "r_std": r_std,
        "osc_strength": osc_strength, "osc_period": osc_period,
        "dom_freq": dom_freq
    }
    
    print(f"{K:4d} {r_mean:8.3f} {r_std:8.3f} {osc_strength:8.3f} {osc_period:8d} {dom_freq:10.4f}")

with open('r19z_bifurcation.json', 'w') as f:
    json.dump(results, f, indent=2)
print("\nSaved r19z_bifurcation.json")
