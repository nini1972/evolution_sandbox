"""
R19Z Deep Dive: Characterize the feedback oscillation at α=0.9, K=10.
Run long simulation, record r(t) and avalanche(t), compute spectra.
"""
import numpy as np
import json

np.random.seed(42)
grid_size = 6
base_threshold = np.random.normal(4.0, 0.5, (grid_size, grid_size))
base_threshold = np.maximum(base_threshold, 1.0)
N_osc = 30
total_time = 200.0
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

# Two configurations: one-way (alpha=0) and bidirectional (alpha=0.9)
# Same K=10, sigma=100
configs = [
    ("one_way", 0.0, 10),
    ("bidirectional", 0.9, 10),
]

all_ts = {}
for name, alpha, K in configs:
    print(f"Running {name}: α={alpha}, K={K}, σ=100, T={total_time}")
    theta = np.random.uniform(0, 2*np.pi, N_osc)
    heights = np.random.uniform(0, 3, (grid_size, grid_size))
    omega = np.random.normal(0, 0.5, N_osc)
    r_hist = []
    av_hist = []
    
    for t in range(n_steps):
        r = abs(np.mean(np.exp(1j * theta)))
        threshold = base_threshold * (1.0 - alpha * r)
        threshold = np.maximum(threshold, 0.3)
        noise = get_kicks(100.0, heights, threshold, N_osc)
        
        k1 = kuramoto_rhs(theta, omega, K, N_osc) + noise
        k2 = kuramoto_rhs(theta + 0.5*dt*k1, omega, K, N_osc) + noise
        k3 = kuramoto_rhs(theta + 0.5*dt*k2, omega, K, N_osc) + noise
        k4 = kuramoto_rhs(theta + dt*k3, omega, K, N_osc) + noise
        theta = (theta + (dt/6.0)*(k1 + 2*k2 + 2*k3 + k4)) % (2*np.pi)
        
        if t > burn_in:
            r_hist.append(r)
        if t % sandpile_interval == 0:
            heights, av = sandpile_step(heights, threshold)
            if t > burn_in:
                av_hist.append(av)
    
    r_arr = np.array(r_hist)
    av_arr = np.array(av_hist)
    
    # Subsample for JSON
    step_r = max(1, len(r_arr) // 1000)
    step_av = max(1, len(av_arr) // 1000)
    all_ts[name] = {
        "r": r_arr[::step_r].tolist(),
        "av": av_arr[::step_av].tolist(),
        "r_mean": float(np.mean(r_arr)),
        "r_std": float(np.std(r_arr)),
        "av_mean": float(np.mean(av_arr)),
    }
    
    # Autocorrelation
    r_centered = r_arr - np.mean(r_arr)
    autocorr = np.correlate(r_centered, r_centered, mode='full')
    autocorr = autocorr[len(autocorr)//2:]
    autocorr = autocorr / (autocorr[0] + 1e-10)
    
    # Find oscillation period
    for lag in range(5, min(500, len(autocorr)-1)):
        if autocorr[lag] > 0.2 and autocorr[lag] > autocorr[lag-1] and autocorr[lag] > autocorr[lag+1]:
            all_ts[name]["osc_period"] = lag
            all_ts[name]["osc_strength"] = float(autocorr[lag])
            break
    else:
        all_ts[name]["osc_period"] = 0
        all_ts[name]["osc_strength"] = 0.0
    
    # Save autocorrelation (subsampled)
    all_ts[name]["autocorr"] = autocorr[:500].tolist()
    
    print(f"  r={np.mean(r_arr):.3f}±{np.std(r_arr):.3f} av={np.mean(av_arr):.2f} "
          f"osc_period={all_ts[name]['osc_period']} strength={all_ts[name]['osc_strength']:.3f}")

with open('r19z_feedback_deep.json', 'w') as f:
    json.dump(all_ts, f, indent=2)
print("Saved r19z_feedback_deep.json")
