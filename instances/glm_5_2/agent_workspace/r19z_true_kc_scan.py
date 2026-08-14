import numpy as np
import json

np.random.seed(42)
grid_size = 6
threshold = np.random.normal(4.0, 0.5, (grid_size, grid_size))
threshold = np.maximum(threshold, 1.0)
N_osc = 20
total_time = 30.0
dt = 0.02
burn_frac = 0.4
sandpile_interval = max(1, int(0.1 / dt))

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
    for _ in range(n_relax):
        u = heights >= threshold
        if not u.any(): break
        for x in range(grid_size):
            for y in range(grid_size):
                if heights[x,y] >= threshold[x,y]:
                    hd = threshold[x,y]
                    heights[x,y] -= hd
                    for nx,ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                        if 0<=nx<grid_size and 0<=ny<grid_size:
                            heights[nx,ny] += hd/4.0
    return heights

# Fine K scan to find true K_c(sigma) 
sigma_values = [0, 5, 20, 50, 100]
K_values = list(np.arange(0, 30.5, 1.0))  # fine scan 0 to 30
n_steps = int(total_time / dt)
burn_in = int(n_steps * burn_frac)

results = {}
print("Fine K_c scan with RK4 (dt=0.02)...")
print(f"K values: {K_values}")

for sigma in sigma_values:
    results[str(sigma)] = []
    for K in K_values:
        theta = np.random.uniform(0, 2*np.pi, N_osc)
        heights = np.random.uniform(0, 3, (grid_size, grid_size))
        omega = np.random.normal(0, 0.5, N_osc)
        r_hist = []
        
        for t in range(n_steps):
            noise = get_kicks(sigma, heights, threshold, N_osc) if sigma > 0 else np.zeros(N_osc)
            k1 = kuramoto_rhs(theta, omega, K, N_osc) + noise
            k2 = kuramoto_rhs(theta + 0.5*dt*k1, omega, K, N_osc) + noise
            k3 = kuramoto_rhs(theta + 0.5*dt*k2, omega, K, N_osc) + noise
            k4 = kuramoto_rhs(theta + dt*k3, omega, K, N_osc) + noise
            theta = (theta + (dt/6.0)*(k1 + 2*k2 + 2*k3 + k4)) % (2*np.pi)
            
            if t > burn_in:
                r_hist.append(abs(np.mean(np.exp(1j * theta))))
            if t % sandpile_interval == 0:
                heights = sandpile_step(heights, threshold)
        
        r_mean = float(np.mean(r_hist))
        results[str(sigma)].append({"K": K, "r": r_mean})
    
    # Find K_c where r crosses 0.5
    rs = [d["r"] for d in results[str(sigma)]]
    ks = [d["K"] for d in results[str(sigma)]]
    kc = None
    for i in range(len(rs)-1):
        if rs[i] < 0.5 <= rs[i+1]:
            # Linear interpolation
            kc = ks[i] + (0.5 - rs[i]) / (rs[i+1] - rs[i]) * (ks[i+1] - ks[i])
            break
    print(f"σ={sigma:3d}: K_c(0.5) ≈ {kc:.2f}  | r(K=0)={rs[0]:.3f} r(K=30)={rs[-1]:.3f}")

with open('r19z_kc_scan.json', 'w') as f:
    json.dump(results, f, indent=2)
print("Saved r19z_kc_scan.json")
