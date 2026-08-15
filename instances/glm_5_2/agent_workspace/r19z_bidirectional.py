"""
R19Z: Bidirectional SOC-Kuramoto Resonance
Instead of sandpile -> Kuramoto (one-way), make it bidirectional:
- Sandpile avalanches kick oscillators (as before)
- Oscillator synchrony (r) modulates sandpile threshold: high r -> lower threshold -> more avalanches
  (synchronized system pumps energy INTO the sandpile, making it more critical)
  
This creates a true feedback loop: 
  sync -> more avalanches -> more noise -> less sync -> fewer avalanches -> less noise -> more sync
"""
import numpy as np
import json

np.random.seed(42)
grid_size = 6
base_threshold = np.random.normal(4.0, 0.5, (grid_size, grid_size))
base_threshold = np.maximum(base_threshold, 1.0)
N_osc = 30
total_time = 50.0
dt = 0.02
burn_frac = 0.3
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

# Experiment: One-way vs Bidirectional coupling
# Feedback strength: alpha (how much r modulates threshold)
# threshold = base_threshold * (1 - alpha * r)
# When r is high (sync), threshold drops -> more avalanches -> more noise -> r drops
# When r is low (desync), threshold rises -> fewer avalanches -> less noise -> r rises

sigma = 20.0  # moderate noise
K_values = [2, 5, 10, 15, 20, 30]
alpha_values = [0.0, 0.1, 0.3, 0.5]  # 0 = one-way, higher = stronger feedback

results = {}
print("Bidirectional SOC-Kuramoto experiment")
print(f"σ={sigma}, N={N_osc}, grid={grid_size}x{grid_size}, dt={dt}")
print(f"alpha=0: one-way (sandpile→Kuramoto only)")
print(f"alpha>0: bidirectional (Kuramoto r modulates sandpile threshold)")

for alpha in alpha_values:
    results[f"alpha_{alpha}"] = {}
    for K in K_values:
        theta = np.random.uniform(0, 2*np.pi, N_osc)
        heights = np.random.uniform(0, 3, (grid_size, grid_size))
        omega = np.random.normal(0, 0.5, N_osc)
        r_hist = []
        avalanche_hist = []
        
        for t in range(n_steps):
            # Compute current r
            r = abs(np.mean(np.exp(1j * theta)))
            
            # Modulate threshold based on r (bidirectional feedback)
            threshold = base_threshold * (1.0 - alpha * r)
            threshold = np.maximum(threshold, 0.5)  # safety
            
            # Sandpile kicks
            noise = get_kicks(sigma, heights, threshold, N_osc) if sigma > 0 else np.zeros(N_osc)
            
            # RK4 integration
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
                    avalanche_hist.append(av)
        
        r_mean = float(np.mean(r_hist))
        r_std = float(np.std(r_hist))
        av_mean = float(np.mean(avalanche_hist)) if avalanche_hist else 0
        results[f"alpha_{alpha}"][str(K)] = {
            "r_mean": r_mean, "r_std": r_std, 
            "av_mean": av_mean
        }
        print(f"  α={alpha:.1f} K={K:2d}: r={r_mean:.3f}±{r_std:.3f} av={av_mean:.2f}")

with open('r19z_bidirectional.json', 'w') as f:
    json.dump(results, f, indent=2)
print("\nSaved r19z_bidirectional.json")
