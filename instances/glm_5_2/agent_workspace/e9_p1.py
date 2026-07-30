import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R9: Triadic Resonance: Lorenz -> Mandelbrot -> Gray-Scott ===')

# Phase 1: Lorenz Attractor
print('Phase 1: Lorenz...')
sigma, rho, beta = 10.0, 28.0, 8/3.0
dt = 0.01
N = 10000
xs = np.zeros(N); ys = np.zeros(N); zs = np.zeros(N)
x, y, z = 0.1, 0.0, 0.0
for i in range(N):
    dx = sigma*(y-x); dy = x*(rho-z)-y; dz = x*y - beta*z
    x += dx*dt; y += dy*dt; z += dz*dt
    xs[i], ys[i], zs[i] = x, y, z

idx = np.linspace(2000, N-1, 8).astype(int)
lorenz_pts = list(zip(xs[idx], ys[idx], zs[idx]))
print('Sampled {} Lorenz points'.format(len(lorenz_pts)))

# Phase 2: Mandelbrot with Lorenz-modulated power
print('Phase 2: Mandelbrot with Lorenz modulation...')
W, Hh = 200, 200
re = np.linspace(-2.0, 0.5, W)
im = np.linspace(-1.25, 1.25, Hh)
RE, IM = np.meshgrid(re, im)
C = RE + 1j*IM

max_iter = 60
escape = np.zeros((Hh, W))
for py in range(Hh):
    lidx = int((py / Hh) * len(lorenz_pts))
    lidx = min(lidx, len(lorenz_pts)-1)
    lx, ly, lz = lorenz_pts[lidx]
    power = 2.0 + (lx / 30.0)
    Z = np.zeros(W, dtype=complex)
    c_row = C[py]
    for it in range(max_iter):
        Z = Z**power + c_row
        escaped = np.abs(Z) > 2
        not_yet = escape[py] == 0
        newly = escaped & not_yet
        escape[py, newly] = it
    if py % 50 == 0:
        print('  row {}/{}, power={:.3f}'.format(py, Hh, power))

escape_norm = escape / max_iter
print('Mandelbrot phase complete. Mean escape: {:.3f}'.format(escape_norm.mean()))

# Phase 3: Gray-Scott seeded by Mandelbrot escape field
print('Phase 3: Gray-Scott seeded by Mandelbrot escape...')
Du, Dv = 0.16, 0.08
F_base = 0.025
k_base = 0.060
F_field = F_base + 0.01 * escape_norm
k_field = k_base + 0.01 * (1 - escape_norm)

U = np.ones((Hh, W))
V = np.zeros((Hh, W))
seed_mask = (escape_norm > 0.2) & (escape_norm < 0.7)
V[seed_mask] = 0.5
U[seed_mask] = 0.5
V += np.random.rand(Hh, W) * 0.05 * seed_mask
U = np.clip(U, 0, 1)
V = np.clip(V, 0, 1)

print('Running Gray-Scott...')
for step in range(500):
    lap_U = (np.roll(U,1,0)+np.roll(U,-1,0)+np.roll(U,1,1)+np.roll(U,-1,1)-4*U)
    lap_V = (np.roll(V,1,0)+np.roll(V,-1,0)+np.roll(V,1,1)+np.roll(V,-1,1)-4*V)
    uv2 = U*V*V
    U += Du*lap_U - uv2 + F_field*(1-U)
    V += Dv*lap_V + uv2 - k_field*V
    U = np.clip(U, 0, 1)
    V = np.clip(V, 0, 1)
    if step % 100 == 0:
        print('  step {}/500'.format(step))

print('Gray-Scott complete.')

# Phase 4: Visualize all three stages
print('Phase 4: Visualization...')
fig, axes = plt.subplots(1, 4, figsize=(24, 6))

# Stage 1: Lorenz attractor
ax = axes[0]
ax.plot(xs, ys, lw=0.3, alpha=0.7, color='cyan')
ax.scatter(xs[idx], ys[idx], c='red', s=20, zorder=5)
ax.set_title('Stage 1: Lorenz Attractor\n(8 sample points)')
ax.set_xlabel('x'); ax.set_ylabel('y')
ax.set_facecolor('#0a0a1a')

# Stage 2: Mandelbrot escape field (Lorenz-modulated)
ax = axes[1]
ax.imshow(escape_norm, extent=[-2.0, 0.5, -1.25, 1.25], origin='lower', cmap='inferno', aspect='auto')
ax.set_title('Stage 2: Mandelbrot Escape\n(Lorenz-modulated power)')
ax.set_xlabel('Re'); ax.set_ylabel('Im')

# Stage 3: Gray-Scott V field
ax = axes[2]
ax.imshow(V, cmap='magma', origin='lower', aspect='auto')
ax.set_title('Stage 3: Gray-Scott V\n(seeded by Mandelbrot)')
ax.set_xlabel('x'); ax.set_ylabel('y')

# Stage 4: Composite overlay - Mandelbrot + Gray-Scott
ax = axes[3]
composite = escape_norm * 0.5 + V * 0.5
ax.imshow(composite, cmap='twilight_shifted', origin='lower', aspect='auto')
ax.set_title('Stage 4: Composite\nMandelbrot + Gray-Scott')
ax.set_xlabel('x'); ax.set_ylabel('y')

plt.suptitle('R9: Triadic Resonance - Lorenz -> Mandelbrot -> Gray-Scott', fontsize=16, color='white', y=1.02)
plt.tight_layout()
fig.savefig('../../shared_space/resonance_triadic_lorenz_mandelbrot_gray_scott.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('Saved: resonance_triadic_lorenz_mandelbrot_gray_scott.png')

# Also save the data
np.save('../../shared_space/e9_escape_norm.npy', escape_norm)
np.save('../../shared_space/e9_V_field.npy', V)
np.save('../../shared_space/e9_lorenz_pts.npy', np.array(lorenz_pts))
print('Data saved.')
print('=== R9 COMPLETE ===')
