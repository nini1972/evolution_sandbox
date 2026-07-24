import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(42)

def mandelbrot_escape(w, h, x0, x1, y0, y1, mi):
    x = np.linspace(x0, x1, w)
    y = np.linspace(y0, y1, h)
    X, Y = np.meshgrid(x, y)
    C = X + 1j * Y
    Z = np.zeros_like(C)
    esc = np.zeros((h, w))
    for i in range(mi):
        m = np.abs(Z) <= 2
        Z[m] = Z[m]**2 + C[m]
        esc[m] = i
    return esc

def rule30_seeded(seed_row, w, steps):
    grid = np.zeros((steps, w), dtype=np.int32)
    grid[0] = seed_row
    for t in range(1, steps):
        p = grid[t-1]
        l = np.roll(p, 1)
        r = np.roll(p, -1)
        grid[t] = (l ^ p ^ r) & 1
    return grid

def gray_scott_seeded(sd, w, h, steps, F=0.055, k=0.062, Du=0.16, Dv=0.08, dt=1.0):
    U = np.ones((h, w))
    V = np.zeros((h, w))
    U -= sd * 0.5
    V += sd * 0.25
    U = np.clip(U, 0, 1)
    V = np.clip(V, 0, 1)
    for _ in range(steps):
        lU = (np.roll(U,1,0)+np.roll(U,-1,0)+np.roll(U,1,1)+np.roll(U,-1,1)-4*U)
        lV = (np.roll(V,1,0)+np.roll(V,-1,0)+np.roll(V,1,1)+np.roll(V,-1,1)-4*V)
        U += dt*(Du*lU - U*V*V + F*(1-U))
        V += dt*(Dv*lV + U*V*V - (F+k)*V)
        U = np.clip(U, 0, 1)
        V = np.clip(V, 0, 1)
    return U, V

N = 200
print('Stage 1: Mandelbrot escape field...')
mandel = mandelbrot_escape(N, N, -2.0, 0.5, -1.25, 1.25, 80)
mandel_norm = mandel / mandel.max()

print('Stage 2: Rule 30 seeded by Mandelbrot...')
mid_row = mandel_norm[N//2]
seed = (mid_row > np.median(mid_row)).astype(np.int32)
ca = rule30_seeded(seed, N, N)
ca_density = ca.astype(float)
ca_density[ca_density > 0] = 1.0

print('Stage 3: Gray-Scott seeded by Rule 30...')
U, V = gray_scott_seeded(ca_density, N, N, 500)

fig, axes = plt.subplots(1, 4, figsize=(28, 7))
fig.suptitle('Triple Resonance Cascade: Mandelbrot -> Rule 30 -> Gray-Scott', fontsize=16, fontweight='bold')

axes[0].imshow(mandel_norm, cmap='magma', extent=[-2.0, 0.5, -1.25, 1.25])
axes[0].set_title('Stage 1: Mandelbrot Escape Field')

axes[1].imshow(ca, cmap='binary')
axes[1].set_title('Stage 2: Rule 30 (Mandelbrot-seeded)')

axes[2].imshow(V, cmap='inferno')
axes[2].set_title('Stage 3: Gray-Scott V (Rule 30-seeded)')

diff = V - mandel_norm
axes[3].imshow(diff, cmap='RdBu_r', vmin=-0.5, vmax=0.5)
axes[3].set_title('Resonance: V - Mandelbrot')

for ax in axes:
    ax.axis('off')
fig.tight_layout()
fig.savefig('../../shared_space/resonance_triple_cascade.png', dpi=150, bbox_inches='tight')
print('Saved resonance_triple_cascade.png')

# Analysis
print('Mandelbrot entropy:', -np.sum(mandel_norm * np.log2(mandel_norm + 1e-12)))
print('Rule 30 entropy:', -np.sum(ca_density * np.log2(ca_density + 1e-12)))
corr = np.corrcoef(V.flatten(), mandel_norm.flatten())[0,1]
print('Correlation V vs Mandelbrot:', corr)
print('Done.')
