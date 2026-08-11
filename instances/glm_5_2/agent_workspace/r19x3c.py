import numpy as np

np.random.seed(42)
grid_size = 8
threshold = np.random.normal(4.0, 0.5, (grid_size, grid_size))
threshold = np.maximum(threshold, 1.0)
N_osc = 20
sigma = 5.0
dt = 0.01
n_steps = 30000  # shorter to fit in time
burn_in = 15000
sandpile_interval = 10

K_values = [10, 15, 20, 25, 30, 40]
for K in K_values:
    theta = np.random.uniform(0, 2*np.pi, N_osc)
    heights = np.random.uniform(0, 3, (grid_size, grid_size))
    omega = np.random.normal(0, 0.5, N_osc)
    r_history = []
    for t in range(n_steps):
        sin_diff = np.sin(theta - theta[:, None])
        dtheta = omega + (K/N_osc) * sin_diff.sum(axis=1)
        gx = np.random.randint(0, grid_size, N_osc)
        gy = np.random.randint(0, grid_size, N_osc)
        h_ratio = heights[gx, gy] / np.maximum(threshold[gx, gy], 0.1)
        kicks = np.random.normal(0, sigma) * h_ratio
        dtheta += kicks
        theta = (theta + dtheta * dt) % (2*np.pi)
        if t > burn_in:
            r = np.abs(np.mean(np.exp(1j * theta)))
            r_history.append(r)
        if t % sandpile_interval == 0:
            drop_x, drop_y = np.random.randint(0, grid_size, 2)
            heights[drop_x, drop_y] += 1.0
            for _ in range(6):
                unstable = heights >= threshold
                if not unstable.any():
                    break
                for x in range(grid_size):
                    for y in range(grid_size):
                        if heights[x, y] >= threshold[x, y]:
                            h_drop = threshold[x, y]
                            heights[x, y] -= h_drop
                            for nx, ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                                if 0 <= nx < grid_size and 0 <= ny < grid_size:
                                    heights[nx, ny] += h_drop / 4.0
    print(f"K={K:3d}: r={np.mean(r_history):.6f}")
