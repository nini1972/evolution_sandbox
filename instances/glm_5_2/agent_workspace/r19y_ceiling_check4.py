import numpy as np
import json

np.random.seed(42)
grid_size = 6
threshold = np.random.normal(4.0, 0.5, (grid_size, grid_size))
threshold = np.maximum(threshold, 1.0)
N_osc = 20
n_steps = 3000
burn_in = int(n_steps * 0.4)
sandpile_interval = 5
dt = 0.02

# Try increasing K for sigma=160 to see if we can recover sync
sigma_val = 160.0
K_values = [80, 160, 320, 640, 1280]

for K in K_values:
    if K * dt >= 2.0:
        print(f"K={K}: SKIP (K*dt={K*dt:.2f} >= 2, Euler unstable)")
        continue
    theta = np.random.uniform(0, 2*np.pi, N_osc)
    heights = np.random.uniform(0, 3, (grid_size, grid_size))
    omega = np.random.normal(0, 0.5, N_osc)
    r_hist = []
    for t in range(n_steps):
        sin_diff = np.sin(theta - theta[:, None])
        dtheta = omega + (K/N_osc) * sin_diff.sum(axis=1)
        gx = np.random.randint(0, grid_size, N_osc)
        gy = np.random.randint(0, grid_size, N_osc)
        h_ratio = heights[gx, gy] / np.maximum(threshold[gx, gy], 0.1)
        kicks = np.random.normal(0, sigma_val) * h_ratio
        dtheta += kicks
        theta = (theta + dtheta * dt) % (2*np.pi)
        if t > burn_in:
            r_hist.append(abs(np.mean(np.exp(1j * theta))))
        if t % sandpile_interval == 0:
            dx, dy = np.random.randint(0, grid_size, 2)
            heights[dx, dy] += 1.0
            for _ in range(6):
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
    r_mean = float(np.mean(r_hist))
    print(f"σ={sigma_val}, K={K:5d} (K*dt={K*dt:.2f}): r={r_mean:.4f}")

# Now test: at the original dt=0.1, what was K_max?
# Original found K_max ≈ 19.6, and 2/dt = 2/0.1 = 20
# These are suspiciously close!
print(f"\nOriginal dt=0.1: K_crit_Euler = {2/0.1:.1f}")
print(f"Original K_max (resilience ceiling) = 19.6")
print(f"These differ by only {abs(20-19.6)/20*100:.1f}% !!!")
