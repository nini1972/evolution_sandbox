import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import deque
N = 200
source = (N // 2, N // 2)
dist = np.full((N, N), -1.0)
dist[source] = 0.0
queue = deque([source])
dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
while queue:
    r, c = queue.popleft()
    for dr, dc in dirs:
        nr, nc = r + dr, c + dc
        if 0 <= nr < N and 0 <= nc < N and dist[nr, nc] < 0:
            dist[nr, nc] = dist[r, c] + 1.0
            queue.append((nr, nc))
dist_norm = dist / dist.max()
source2 = (N // 4, 3 * N // 4)
dist2 = np.full((N, N), -1.0)
dist2[source2] = 0.0
queue2 = deque([source2])
while queue2:
    r, c = queue2.popleft()
    for dr, dc in dirs:
        nr, nc = r + dr, c + dc
        if 0 <= nr < N and 0 <= nc < N and dist2[nr, nc] < 0:
            dist2[nr, nc] = dist2[r, c] + 1.0
            queue2.append((nr, nc))
dist2_norm = dist2 / dist2.max()
wavefront = (dist_norm + dist2_norm) * 0.5
print('Wavefront computed, max:', wavefront.max())
Du = 0.16
Dv = 0.08
Fp = 0.035
kp = 0.065
U = np.ones((N, N))
V = np.where(wavefront < 0.3, wavefront * 0.8, 0.0).astype(np.float64)
def lap(Z):
    L = np.zeros_like(Z)
    L[1:-1, 1:-1] = Z[:-2,1:-1]+Z[2:,1:-1]+Z[1:-1,:-2]+Z[1:-1,2:]-4*Z[1:-1,1:-1]
    return L
dt = 1.0
steps = 4000
snaps = [0, 500, 1000, 2000, 4000]
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
af = axes.flatten()
af[0].imshow(wavefront, cmap='viridis', origin='upper')
af[0].set_title('Dijkstra Wavefront (Dual Source)')
idx = 1
for step in range(1, steps + 1):
    lu = lap(U)
    lv = lap(V)
    uvv = U * V * V
    U += dt * (Du * lu - uvv + Fp * (1 - U))
    V += dt * (Dv * lv + uvv - (Fp + kp) * V)
    U = np.clip(U, 0, 1)
    V = np.clip(V, 0, 1)
    if step in snaps[1:]:
        if idx < 6:
            af[idx].imshow(V, cmap='inferno', origin='upper')
            af[idx].set_title('V at step ' + str(step))
            idx += 1
while idx < 6:
    af[idx].set_visible(False)
    idx += 1
plt.suptitle('Resonance 4: Dijkstra Wavefront -> Gray-Scott', fontsize=13)
plt.tight_layout()
plt.savefig('resonance_dijkstra_gray_scott.png', dpi=150)
print('Saved resonance_dijkstra_gray_scott.png')
