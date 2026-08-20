#!/usr/bin/env python3
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json, os, heapq

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

def mandelbrot(width, height, max_iter=200, xlim=(-2.0, 1.0), ylim=(-1.5, 1.5)):
    x = np.linspace(xlim[0], xlim[1], width)
    y = np.linspace(ylim[0], ylim[1], height)
    C = x[np.newaxis, :] + 1j * y[:, np.newaxis]
    M = np.zeros(C.shape, dtype=float)
    Z = np.zeros(C.shape, dtype=complex)
    for i in range(max_iter):
        mask = np.abs(Z) <= 2.0
        Z[mask] = Z[mask]**2 + C[mask]
        M[mask] += 1
    return M / max_iter

def rule30_multi_seed(width=512, steps=512, seed_mask=None):
    # If seed_mask is 2D, use the middle row as 1D seed
    if seed_mask is not None and len(seed_mask.shape) == 2:
        ca = np.zeros((steps, width), dtype=np.uint8)
        ca[0] = seed_mask[seed_mask.shape[0]//2].astype(np.uint8)
    else:
        ca = np.zeros((steps, width), dtype=np.uint8)
        if seed_mask is not None:
            ca[0] = seed_mask.astype(np.uint8)
        else:
            ca[0, width//2] = 1
    for t in range(1, steps):
        left = np.roll(ca[t-1], 1)
        center = ca[t-1]
        right = np.roll(ca[t-1], -1)
        ca[t] = (left ^ (center | right)).astype(np.uint8)
    return ca

def lsystem_dragon(iterations=12):
    axiom = 'FX'
    rules = {'X': 'X+YF+', 'Y': '-FX-Y'}
    result = axiom
    for _ in range(iterations):
        new = ''
        for c in result:
            new += rules.get(c, c)
        result = new
    return result

def lsystem_to_field(instructions, width=512, height=512, step=3.0):
    field = np.zeros((height, width), dtype=np.float64)
    x, y = width // 2, height // 2
    angle = 0.0
    for cmd in instructions:
        if cmd == 'F':
            nx = x + step * np.cos(angle)
            ny = y + step * np.sin(angle)
            segs = max(1, int(max(abs(nx-x), abs(ny-y))))
            for t in np.linspace(0, 1, segs):
                xi = int(x + t * (nx - x))
                yi = int(y + t * (ny - y))
                if 0 <= xi < width and 0 <= yi < height:
                    field[yi, xi] += 1.0
            x, y = nx, ny
        elif cmd == '+':
            angle += np.pi / 5
        elif cmd == '-':
            angle -= np.pi / 5
    return field

def gaussian_kernel(size, sigma=2.0):
    ax = np.arange(-size//2 + 1, size//2 + 1)
    xx, yy = np.meshgrid(ax, ax)
    kernel = np.exp(-(xx**2 + yy**2) / (2.0 * sigma**2))
    return kernel / kernel.sum()

def blur_field(field, sigma=3.0):
    size = int(6 * sigma + 1) | 1
    kernel = gaussian_kernel(size, sigma)
    h, w = field.shape
    pad = size // 2
    padded = np.pad(field, pad, mode='edge')
    result = np.zeros_like(field)
    for i in range(size):
        for j in range(size):
            result += padded[i:i+h, j:j+w] * kernel[i, j]
    return result

def gray_scott_evolve(u_init, v_init, F=0.037, k=0.06, steps=4000, Du=0.16, Dv=0.08):
    u = u_init.copy()
    v = v_init.copy()
    # Ensure U + V = 1 (standard GS constraint)
    u = np.clip(1.0 - v, 0.0, 1.0)
    for step in range(steps):
        lap_u = (np.roll(u, 1, axis=0) + np.roll(u, -1, axis=0) +
                 np.roll(u, 1, axis=1) + np.roll(u, -1, axis=1) - 4*u)
        lap_v = (np.roll(v, 1, axis=0) + np.roll(v, -1, axis=0) +
                 np.roll(v, 1, axis=1) + np.roll(v, -1, axis=1) - 4*v)
        uvv = u * v * v
        u_new = u + Du * lap_u - uvv + F * (1.0 - u)
        v_new = v + Dv * lap_v + uvv - (F + k) * v
        u, v = u_new, v_new
        if step % 1000 == 0:
            print(f'  GS step {step}/{steps}, V mass={np.sum(v):.2f}')
    return u, v

def dijkstra_field(width=256, height=256, num_obstacles=15, seed=42):
    rng = np.random.RandomState(seed)
    obstacles = np.zeros((height, width), dtype=np.float64)
    for _ in range(num_obstacles):
        cx = rng.randint(20, width-20)
        cy = rng.randint(20, height-20)
        r = rng.randint(10, 40)
        yy, xx = np.ogrid[:height, :width]
        mask = (xx - cx)**2 + (yy - cy)**2 <= r**2
        obstacles[mask] = 1.0
    INF = float('inf')
    dist = np.full((height, width), INF)
    source = (height//2, width//2)
    dist[source] = 0
    visited = np.zeros((height, width), dtype=bool)
    pq = [(0, source[0], source[1])]
    while pq:
        d, y, x = heapq.heappop(pq)
        if visited[y, x]:
            continue
        visited[y, x] = True
        for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
            ny, nx = y+dy, x+dx
            if 0 <= ny < height and 0 <= nx < width:
                cost = 1.0 + obstacles[ny, nx] * 5.0
                nd = d + cost
                if nd < dist[ny, nx]:
                    dist[ny, nx] = nd
                    heapq.heappush(pq, (nd, ny, nx))
    dist[dist == INF] = np.max(dist[dist != INF])
    return dist / np.max(dist), obstacles

def analyze_pattern(field):
    hist, _ = np.histogram(field.flatten(), bins=50)
    hist = hist / hist.sum()
    entropy = -np.sum(hist * np.log(hist + 1e-10))
    grad_x = np.gradient(field, axis=1)
    grad_y = np.gradient(field, axis=0)
    roughness = float(np.sqrt(np.mean(grad_x**2 + grad_y**2)))
    return {
        'entropy': float(entropy),
        'roughness': roughness,
        'mean': float(np.mean(field)),
        'std': float(np.std(field)),
        'max': float(np.max(field))
    }

def save_genome(genome_data):
    path = os.path.join(OUTPUT_DIR, genome_data['hybrid_id'] + '_genome.json')
    with open(path, 'w') as f:
        json.dump(genome_data, f, indent=2)
    print(f'  Saved genome: {os.path.basename(path)}')

def lineage_tree(ax, p1, p2, offspring, c1='purple', c2='green'):
    ax.axis('off')
    ax.text(0.5, 0.85, 'Lineage Tree', fontsize=12, fontweight='bold',
            transform=ax.transAxes, ha='center')
    ax.plot([0.2, 0.5], [0.6, 0.35], 'k-', linewidth=2)
    ax.plot([0.8, 0.5], [0.6, 0.35], 'k-', linewidth=2)
    ax.text(0.2, 0.65, p1, fontsize=10, ha='center',
            transform=ax.transAxes, color=c1)
    ax.text(0.8, 0.65, p2, fontsize=10, ha='center',
            transform=ax.transAxes, color=c2)
    ax.text(0.5, 0.15, offspring, fontsize=10, ha='center',
            transform=ax.transAxes, color='red', fontweight='bold')
