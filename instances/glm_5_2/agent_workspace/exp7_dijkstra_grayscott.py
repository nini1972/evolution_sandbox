import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
import heapq

with open('../../shared_space/dijkstra_output.json') as f:
    data = json.load(f)

rows, cols = data['rows'], data['cols']
graph = data['graph']
start = data['start_node']

dist = {}
for node in graph:
    dist[node] = float('inf')
dist[start] = 0
pq = [(0, start)]
while pq:
    d, u = heapq.heappop(pq)
    if d > dist[u]:
        continue
    for v, w in graph[u].items():
        nd = d + w
        if nd < dist[v]:
            dist[v] = nd
            heapq.heappush(pq, (nd, v))

dist_grid = np.zeros((rows, cols))
for r in range(rows):
    for c in range(cols):
        key = '%d-%d' % (r, c)
        dist_grid[r, c] = dist.get(key, 0)

dmax = dist_grid.max()
dist_norm = dist_grid / (dmax + 1e-9)

scale = 10
big_dist = np.kron(dist_norm, np.ones((scale, scale)))

def gray_scott(steps, F_base, k, Du, Dv, feed_map):
    h, w = feed_map.shape
    U = np.ones((h, w))
    V = np.zeros((h, w))
    ch, cw = h // 2, w // 2
    r = 5
    U[ch-r:ch+r, cw-r:cw+r] = 0.5
    V[ch-r:ch+r, cw-r:cw+r] = 0.25
    U += np.random.randn(h, w) * 0.01
    V += np.random.randn(h, w) * 0.01
    for i in range(steps):
        F = F_base + 0.02 * feed_map
        Lu = (np.roll(U,1,0) + np.roll(U,-1,0) + np.roll(U,1,1) + np.roll(U,-1,1) - 4*U)
        Lv = (np.roll(V,1,0) + np.roll(V,-1,0) + np.roll(V,1,1) + np.roll(V,-1,1) - 4*V)
        uvv = U * V * V
        U += Du * Lu - uvv + F * (1 - U)
        V += Dv * Lv + uvv - (F + k) * V
        U = np.clip(U, 0, 1)
        V = np.clip(V, 0, 1)
    return U, V

np.random.seed(7)
U, V = gray_scott(300, 0.037, 0.06, 0.16, 0.08, big_dist)

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

axes[0].imshow(dist_norm, cmap='viridis', interpolation='nearest')
axes[0].set_title('Dijkstra Distance Field', fontsize=12, color='white')
axes[0].axis('off')

axes[1].imshow(V, cmap='inferno')
axes[1].set_title('Gray-Scott V (feed=Dijkstra dist)', fontsize=12, color='white')
axes[1].axis('off')

axes[2].imshow(V, cmap='inferno', alpha=0.8)
axes[2].contour(big_dist, levels=10, colors='cyan', linewidths=0.5, alpha=0.6)
axes[2].set_title('Overlay: Dijkstra contours on GS', fontsize=12, color='white')
axes[2].axis('off')

fig.suptitle('R7: Shortest-Path Distances -> Reaction-Diffusion Feed Rate', fontsize=14, color='white')
plt.tight_layout()
plt.savefig('resonance_dijkstra_grayscott_v2.png', dpi=120, bbox_inches='tight', facecolor='#0a0a12')
print('Saved resonance_dijkstra_grayscott_v2.png')
