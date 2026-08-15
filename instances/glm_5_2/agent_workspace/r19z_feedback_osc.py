"""
R19Z: Finding the resonance regime where bidirectional feedback creates oscillations.
Push to high sigma, low K, high alpha to find the feedback sweet spot.
Also record time series to detect oscillations.
"""
import numpy as np
import json

np.random.seed(42)
grid_size = 6
base_threshold = np.random.normal(4.0, 0.5, (grid_size, grid_size))
base_threshold = np.maximum(base_threshold, 1.0)
N_osc = 30
total_time = 80.0
dt = 0.02
burn_frac = 0.2
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

# Push to extreme regime: high sigma, low K, high alpha
sigma = 100.0
K_values = [5, 10, 15, 20, 30, 50]
alpha_values = [0.0, 0.3, 0.5, 0.7, 0.9]

results = {}
time_series = {}

print(f"Feedback oscillation search: σ={sigma}, N={N_osc}")
print(f"Looking for oscillations in r(t) caused by bidirectional feedback")

for alpha in alpha_values:
    results[f"alpha_{alpha}"] = {}
    for K in K_values:
        theta = np.random.uniform(0, 2*np.pi, N_osc)
        heights = np.random.uniform(0, 3, (grid_size, grid_size))
        omega = np.random.normal(0, 0.5, N_osc)
        r_hist = []
        av_hist = []
        
        for t in range(n_steps):
            r = abs(np.mean(np.exp(1j * theta)))
            threshold = base_threshold * (1.0 - alpha * r)
            threshold = np.maximum(threshold, 0.3)
            
            noise = get_kicks(sigma, heights, threshold, N_osc) if sigma > 0 else np.zeros(N_osc)
            
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
        r_mean = float(np.mean(r_arr))
        r_std = float(np.std(r_arr))
        av_mean = float(np.mean(av_hist)) if av_hist else 0
        
        # Detect oscillation: autocorrelation peak at non-zero lag
        if len(r_arr) > 100:
            r_centered = r_arr - r_mean
            autocorr = np.correlate(r_centered, r_centered, mode='full')
            autocorr = autocorr[len(autocorr)//2:]  # keep right half
            autocorr = autocorr / (autocorr[0] + 1e-10)  # normalize
            # Find first peak after lag 0
            osc_strength = 0
            osc_period = 0
            for lag in range(5, min(500, len(autocorr))):
                if autocorr[lag] > 0.3 and autocorr[lag] > autocorr[lag-1] and autocorr[lag] > autocorr[lag+1]:
                    osc_strength = float(autocorr[lag])
                    osc_period = lag
                    break
        else:
            osc_strength = 0
            osc_period = 0
        
        results[f"alpha_{alpha}"][str(K)] = {
            "r_mean": r_mean, "r_std": r_std, "av_mean": av_mean,
            "osc_strength": osc_strength, "osc_period": osc_period
        }
        
        # Save time series for interesting cases
        if alpha in [0.0, 0.5, 0.9] and K in [10, 20, 30]:
            key = f"a{alpha}_K{K}"
            # Subsample to keep file size manageable
            step = max(1, len(r_arr) // 500)
            time_series[key] = {
                "r": r_arr[::step].tolist(),
                "av": av_hist[::step][:500] if av_hist else []
            }
        
        osc_str = f"OSC(p={osc_period},s={osc_strength:.2f})" if osc_strength > 0.3 else "no osc"
        print(f"  α={alpha:.1f} K={K:2d}: r={r_mean:.3f}±{r_std:.3f} av={av_mean:.2f} {osc_str}")

with open('r19z_feedback_osc.json', 'w') as f:
    json.dump(results, f, indent=2)
with open('r19z_feedback_ts.json', 'w') as f:
    json.dump(time_series, f, indent=2)
print("\nSaved results")
