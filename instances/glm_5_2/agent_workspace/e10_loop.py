import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R10: Closed-Loop Resonance ===')
print('Lorenz -> Mandelbrot -> Gray-Scott -> feedback -> Lorenz')
print()

# We run 3 iterations of the loop
# Each iteration: Lorenz generates trajectory, samples points,
# Mandelbrot uses those points, Gray-Scott evolves,
# then GS V-field stats feed back as Lorenz perturbations

W, Hh = 150, 150
Du, Dv = 0.16, 0.08
max_iter = 50
gs_steps = 300

# Feedback parameters
lorenz_perturbation = np.array([0.0, 0.0, 0.0])

all_lorenz = []
all_escape = []
all_V = []

for loop_iter in range(3):
    print('--- Loop iteration {} ---'.format(loop_iter+1))
    
    # Phase 1: Lorenz with feedback perturbation
    sigma, rho, beta = 10.0, 28.0, 8/3.0
    dt = 0.01
    N = 5000
    xs = np.zeros(N); ys = np.zeros(N); zs = np.zeros(N)
    x = 0.1 + lorenz_perturbation[0]
    y = 0.0 + lorenz_perturbation[1]
    z = 0.0 + lorenz_perturbation[2]
    for i in range(N):
        dx = sigma*(y-x); dy = x*(rho-z)-y; dz = x*y - beta*z
        x += dx*dt; y += dy*dt; z += dz*dt
        xs[i], ys[i], zs[i] = x, y, z
    
    idx = np.linspace(1000, N-1, 6).astype(int)
    lorenz_pts = list(zip(xs[idx], ys[idx], zs[idx]))
    all_lorenz.append((xs, ys, zs, idx))
    print('  Lorenz: perturbation={}'.format(np.round(lorenz_perturbation, 4)))
    
    # Phase 2: Mandelbrot with Lorenz-modulated power
    re = np.linspace(-2.0, 0.5, W)
    im = np.linspace(-1.25, 1.25, Hh)
    RE, IM = np.meshgrid(re, im)
    C = RE + 1j*IM
    escape = np.zeros((Hh, W))
    
    for py in range(Hh):
        lidx = int((py / Hh) * len(lorenz_pts))
        lidx = min(lidx, len(lorenz_pts)-1)
        lx = lorenz_pts[lidx][0]
        power = 2.0 + (lx / 30.0)
        Z = np.zeros(W, dtype=complex)
        c_row = C[py]
        for it in range(max_iter):
            Z = np.where(np.abs(Z) > 2, Z, Z**power + c_row)
            escaped = np.abs(Z) > 2
            not_yet = escape[py] == 0
            newly = escaped & not_yet
            escape[py, newly] = it
    
    escape_norm = np.clip(escape / max_iter, 0, 1)
    all_escape.append(escape_norm.copy())
    print('  Mandelbrot: mean escape={:.4f}'.format(escape_norm.mean()))

    # Phase 3: Gray-Scott
    F_base = 0.025 + 0.005 * escape_norm.mean()
    k_base = 0.060 + 0.005 * (1 - escape_norm.mean())
    F_field = F_base + 0.01 * escape_norm
    k_field = k_base + 0.01 * (1 - escape_norm)

    U = np.ones((Hh, W))
    V = np.zeros((Hh, W))
    seed_mask = (escape_norm > 0.15) & (escape_norm < 0.6)
    V[seed_mask] = 0.5
    U[seed_mask] = 0.5
    V += np.random.rand(Hh, W) * 0.05 * seed_mask
    U = np.clip(U, 0, 1)
    V = np.clip(V, 0, 1)

    for step in range(gs_steps):
        lap_U = (np.roll(U,1,0)+np.roll(U,-1,0)+np.roll(U,1,1)+np.roll(U,-1,1)-4*U)
        lap_V = (np.roll(V,1,0)+np.roll(V,-1,0)+np.roll(V,1,1)+np.roll(V,-1,1)-4*V)
        uv2 = U*V*V
        U += Du*lap_U - uv2 + F_field*(1-U)
        V += Dv*lap_V + uv2 - k_field*V
        U = np.clip(U, 0, 1)
        V = np.clip(V, 0, 1)

    all_V.append(V.copy())
    print('  Gray-Scott: V mean={:.4f}, V std={:.4f}'.format(V.mean(), V.std()))

    # Phase 4: Feedback - GS stats -> Lorenz perturbation
    v_mean = V.mean()
    v_std = V.std()
    v_max = V.max()
    lorenz_perturbation = np.array([
        (v_mean - 0.25) * 2.0,
        (v_std - 0.1) * 3.0,
        (v_max - 0.5) * 1.0
    ])
    lorenz_perturbation = np.clip(lorenz_perturbation, -2.0, 2.0)
    print('  Feedback -> next perturbation: {}'.format(np.round(lorenz_perturbation, 4)))

print()
print('=== Visualization ===')
fig, axes = plt.subplots(3, 4, figsize=(24, 18))

for i in range(3):
    xs, ys, zs, idx = all_lorenz[i]
    axes[i,0].plot(xs, ys, lw=0.3, alpha=0.7, color='cyan')
    axes[i,0].scatter(xs[idx], ys[idx], c='red', s=15, zorder=5)
    axes[i,0].set_title('Loop {}: Lorenz'.format(i+1), fontsize=12)
    axes[i,0].set_facecolor('#0a0a1a')
    axes[i,1].imshow(all_escape[i], extent=[-2,0.5,-1.25,1.25], origin='lower', cmap='inferno', aspect='auto')
    axes[i,1].set_title('Loop {}: Mandelbrot'.format(i+1), fontsize=12)
    axes[i,2].imshow(all_V[i], cmap='magma', origin='lower', aspect='auto')
    axes[i,2].set_title('Loop {}: Gray-Scott'.format(i+1), fontsize=12)
    comp = all_escape[i] * 0.4 + all_V[i] * 0.6
    axes[i,3].imshow(comp, cmap='twilight_shifted', origin='lower', aspect='auto')
    axes[i,3].set_title('Loop {}: Composite'.format(i+1), fontsize=12)

plt.suptitle('R10: Closed-Loop Resonance: Lorenz -> Mandelbrot -> Gray-Scott -> feedback', fontsize=16, y=0.98)
plt.tight_layout()
fig.savefig('../../shared_space/resonance_closed_loop_3iterations.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('Saved: resonance_closed_loop_3iterations.png')
print('=== R10 COMPLETE ===')
