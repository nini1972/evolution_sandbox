import numpy as np
import json

np.random.seed(42)
grid_size = 8
threshold = np.random.normal(4.0, 0.5, (grid_size, grid_size))
threshold = np.maximum(threshold, 1.0)
N_osc = 30
dt = 0.02  # stable up to K=100
n_steps = 4000  # 80 time units
burn_in = int(n_steps * 0.4)
sandpile_interval = 5  # every 0.1 time units

# K values: log-spaced 1 to 60
K_values = np.geomspace(1, 60, 20)
sigma_values = [0.0, 1.0, 2.0, 3.0, 5.0, 8.0]

phase_data = {}
for si, sigma_val in enumerate(sigma_values):
    r_row = []
    for ki, K in enumerate(K_values):
        theta = np.random.uniform(0, 2*np.pi, N_osc)
        heights = np.random.uniform(0, 3, (grid_size, grid_size))
        omega = np.random.normal(0, 0.5, N_osc)
        r_hist = []
        for t in range(n_steps):
            sin_diff = np.sin(theta - theta[:, None])
            dtheta = omega + (K/N_osc) * sin_diff.sum(axis=1)
            if sigma_val > 0:
                gx = np.random.randint(0, grid_size, N_osc)
                gy = np.random.randint(0, grid_size, N_osc)
                h_ratio = heights[gx, gy] / np.maximum(threshold[gx, gy], 0.1)
                kicks = np.random.normal(0, sigma_val) * h_ratio
                dtheta += kicks
            theta = (theta + dtheta * dt) % (2*np.pi)
            if t > burn_in:
                r_hist.append(abs(np.mean(np.exp(1j * theta))))
            if t % sandpile_interval == 0 and sigma_val > 0:
                dx, dy = np.random.randint(0, grid_size, 2)
                heights[dx, dy] += 1.0
                for _ in range(8):
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
        r_row.append(r_mean)
    phase_data[str(sigma_val)] = {'K': K_values.tolist(), 'r': r_row}
    print(f"sigma={sigma_val}: done, r range [{min(r_row):.3f}, {max(r_row):.3f}]")

with open('r19y_phase_data.json', 'w') as f:
    json.dump(phase_data, f)
print("Saved phase data")
