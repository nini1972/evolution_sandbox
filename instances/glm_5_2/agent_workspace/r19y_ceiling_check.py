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

# Test: at dt=0.02 (K_crit=100), does the "resilience ceiling" survive?
# Scan K_c(sigma) at this stable dt

dt = 0.02
K_values = np.geomspace(1, 80, 25)
sigma_values = [1.0, 2.0, 3.0, 5.0, 8.0, 12.0]

ceiling_data = {}
for sigma_val in sigma_values:
    r_row = []
    for K in K_values:
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
        r_row.append(float(np.mean(r_hist)))
    ceiling_data[str(sigma_val)] = {'K': K_values.tolist(), 'r': r_row}
    
    # Find K_c where r crosses 0.5
    r_arr = np.array(r_row)
    K_arr = np.array(K_values)
    above = r_arr >= 0.5
    if above.any() and not above.all():
        idx = np.where(above)[0][0]
        if idx > 0:
            # linear interpolation
            r0, r1 = r_arr[idx-1], r_arr[idx]
            K0, K1 = K_arr[idx-1], K_arr[idx]
            K_c = K0 + (0.5 - r0) / (r1 - r0) * (K1 - K0)
        else:
            K_c = K_arr[0]
    elif above.all():
        K_c = K_arr[0]
    else:
        K_c = float('nan')
    
    # Check if r saturates at high K (ceiling test)
    r_high = np.mean(r_arr[-3:])  # avg of last 3 points
    
    print(f"σ={sigma_val:5.1f}: K_c={K_c:6.2f}, r_high={r_high:.4f}, r range=[{min(r_row):.3f}, {max(r_row):.3f}]")

with open('r19y_ceiling_data.json', 'w') as f:
    json.dump(ceiling_data, f)
print("\nSaved ceiling_data.json")
