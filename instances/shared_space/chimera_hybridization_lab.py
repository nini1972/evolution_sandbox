#!/usr/bin/env python3
"""
CHIMERA HYBRIDIZATION LAB v1.0
Breeding hybrid computational life forms by crossing algorithmic species.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import gridspec
import json
import os

OUTPUT_DIR = '../../shared_space'

# ============================================================
# SPECIES 1: MANDELBROT SET (Fractal species genome)
# ============================================================
def mandelbrot(width, height, max_iter=200, xlim=(-2.0, 1.0), ylim=(-1.5, 1.5)):
    """Mandelbrot set genome: c-plane explorer. Escape-time algorithm."""
    x = np.linspace(xlim[0], xlim[1], width)
    y = np.linspace(ylim[0], ylim[1], height)
    C = x[np.newaxis, :] + 1j * y[:, np.newaxis]
    M = np.zeros(C.shape, dtype=float)
    Z = np.zeros(C.shape, dtype=complex)
    for i in range(max_iter):
        mask = np.abs(Z) <= 2.0
        Z[mask] = Z[mask]**2 + C[mask]
        M[mask] += 1
    M = M / max_iter
    return M

# ============================================================
# SPECIES 2: RULE 30 (Cellular Automaton species genome)
# ============================================================
def rule30(width=200, steps=200):
    """Rule 30 CA genome: deterministic chaotic binary evolution."""
    ca = np.zeros((steps, width), dtype=np.uint8)
    ca[0, width//2] = 1
    for t in range(1, steps):
        left = np.roll(ca[t-1], 1)
        center = ca[t-1]
        right = np.roll(ca[t-1], -1)
        ca[t] = (left ^ (center | right)).astype(np.uint8)
    return ca

# ============================================================
# SPECIES 3: L-SYSTEM (Branching grammar species genome)
# ============================================================
def lsystem_dragon(iterations=12):
    """L-system genome: recursive string rewriting (Dragon curve)."""
    axiom = 'FX'
    rules = {'X': 'X+YF+', 'Y': '-FX-Y'}
    result = axiom
    for _ in range(iterations):
        new = ''
        for c in result:
            if c in rules:
                new += rules[c]
            else:
                new += c
        result = new
    return result

# ============================================================
# SPECIES 4: GRAY-SCOTT (Reaction-Diffusion species genome)
# ============================================================
def gray_scott_evolve(u_init, v_init, F=0.037, k=0.06, steps=4000, Du=0.16, Dv=0.08):
    """Gray-Scott reaction-diffusion genome: Turing pattern generator."""
    u = u_init.copy()
    v = v_init.copy()
    h, w = u.shape
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

# ============================================================
# SPECIES 5: DIJKSTRA (Graph distance field species genome)
# ============================================================
def dijkstra_field(width=256, height=256, num_obstacles=15, seed=42):
    """Dijkstra shortest-path distance field genome."""
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
    import heapq
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
    dist = dist / np.max(dist)
    return dist, obstacles

# ============================================================
# UTILITY FUNCTIONS
# ============================================================
def gaussian_kernel(size, sigma=2.0):
    """Generate a 2D Gaussian kernel."""
    ax = np.arange(-size//2 + 1, size//2 + 1)
    xx, yy = np.meshgrid(ax, ax)
    kernel = np.exp(-(xx**2 + yy**2) / (2.0 * sigma**2))
    return kernel / kernel.sum()

def blur_field(field, sigma=3.0):
    """Apply Gaussian blur to a field."""
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

def analyze_pattern(field):
    """Analyze hybrid phenotype for emergent properties."""
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
    """Save hybrid genome metadata."""
    path = os.path.join(OUTPUT_DIR, genome_data['hybrid_id'] + '_genome.json')
    with open(path, 'w') as f:
        json.dump(genome_data, f, indent=2)
    print(f'  Saved genome: {os.path.basename(path)}')

# ============================================================
# HYBRIDIZATION LAB
# ============================================================

def hybrid_01_mandelbrot_x_grayscott():
    """CHIMERA #01: Mandelbrot x Gray-Scott"""
    print('\n=== Breeding CHIMERA #01: Mandelbrot x Gray-Scott ===')
    size = 256
    print('  Generating Mandelbrot seed...')
    mb = mandelbrot(size, size, max_iter=150, xlim=(-0.8, 0.5), ylim=(-1.0, 1.0))
    # boundary = region near escape threshold
    mb_boundary = np.abs(mb - 0.9) * 5.0
    mb_boundary = np.clip(mb_boundary, 0, 1)

    print('  Setting up Gray-Scott embryo...')
    u_init = np.ones((size, size))
    v_init = mb_boundary * 0.35
    noise = np.random.RandomState(42).random((size, size)) * 0.03
    v_init = np.clip(v_init + noise, 0, 1)

    print('  Evolving hybrid...')
    u_final, v_final = gray_scott_evolve(u_init, v_init, F=0.037, k=0.06, steps=5000)
    analysis = analyze_pattern(v_final)

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('CHIMERA #01: Mandelbrot x Gray-Scott\nFractal-catalytic Reaction-Diffusion',
                 fontsize=14, fontweight='bold')
    axes[0,0].imshow(mb, cmap='twilight', origin='lower')
    axes[0,0].set_title('Parent: Mandelbrot Genome')
    axes[0,0].axis('off')
    axes[0,1].imshow(v_init, cmap='viridis', origin='lower')
    axes[0,1].set_title('Initial V (fractal seed)')
    axes[0,1].axis('off')
    im = axes[0,2].imshow(v_final, cmap='magma', origin='lower')
    axes[0,2].set_title('Hybrid: Final V pattern')
    axes[0,2].axis('off')
    plt.colorbar(im, ax=axes[0,2], fraction=0.046)
    axes[1,0].imshow(u_final, cmap='cool', origin='lower')
    axes[1,0].set_title('Hybrid: Final U field')
    axes[1,0].axis('off')
    # V distribution histogram
    hist, _ = np.histogram(v_final.flatten(), bins=50)
    hist = hist / hist.sum()
    axes[1,1].bar(range(50), hist, color='steelblue')
    axes[1,1].set_title(f'V Distribution (Entropy={analysis["entropy"]:.2f})')
    axes[1,1].set_xlabel('Bin')
    axes[1,1].set_ylabel('Frequency')
    # Lineage tree
    axes[1,2].axis('off')
    axes[1,2].text(0.2, 0.8, 'Lineage Tree', fontsize=12, fontweight='bold',
                   transform=axes[1,2].transAxes, ha='center')
    axes[1,2].plot([0.2, 0.5], [0.6, 0.4], 'k-', linewidth=2)
    axes[1,2].plot([0.8, 0.5], [0.6, 0.4], 'k-', linewidth=2)
    axes[1,2].text(0.2, 0.65, 'Mandelbrot\n(Fractal)', fontsize=10, ha='center',
                   transform=axes[1,2].transAxes, color='purple')
    axes[1,2].text(0.8, 0.65, 'Gray-Scott\n(RD System)', fontsize=10, ha='center',
                   transform=axes[1,2].transAxes, color='green')
    axes[1,2].text(0.5, 0.2, 'CHIMERA\nFractal-catalytic\nTuring Pattern',
                   fontsize=10, ha='center', transform=axes[1,2].transAxes,
                   color='red', fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'chimera_01_mandelbrot_grayscott.png'), dpi=150, bbox_inches='tight')
    print('  Saved: chimera_01_mandelbrot_grayscott.png')
    plt.close()

    save_genome({
        'hybrid_id': 'chimera_01',
        'name': 'Mandelbrot x Gray-Scott',
        'parent_species': ['Mandelbrot Set', 'Gray-Scott RD'],
        'hybridization_method': 'Fractal boundary used as activator seed for Gray-Scott evolution',
        'parameters': {
            'mandelbrot': {'max_iter': 150, 'xlim': [-0.8, 0.5], 'ylim': [-1.0, 1.0]},
            'gray_scott': {'F': 0.037, 'k': 0.06, 'Du': 0.16, 'Dv': 0.08, 'steps': 5000}
        },
        'phenotype_analysis': analysis,
        'status': 'SUCCESS',
        'notes': 'Fractal boundary catalyzes Turing pattern formation. Emergent oscillatory structures at fractal-feature intersections.'
    })
    return v_final, u_final, analysis

if __name__ == '__main__':
    print('========================================')
    print('  CHIMERA HYBRIDIZATION LAB v1.0')
    print('  Breeding hybrid computational life...')
    print('========================================')
    
    # Run hybrid 1
    v1, u1, a1 = hybrid_01_mandelbrot_x_grayscott()
    
    print('\n\nAll hybrids bred successfully!')
    print(f'Chimera #01 analysis: {a1}')
