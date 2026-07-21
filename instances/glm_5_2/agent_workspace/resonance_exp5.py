import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
N = 300
max_iter = 80
dt_l = 0.005
steps_l = 5000
x, y, z = 1.0, 1.0, 1.0
sigma, rho, beta = 10.0, 28.0, 8.0/3.0
traj = []
for _ in range(steps_l):
    dx = sigma * (y - x)
    dy = x * (rho - z) - y
    dz = x * y - beta * z
    x += dt_l * dx
    y += dt_l * dy
    z += dt_l * dz
    traj.append((x, y, z))
traj = np.array(traj)
cx = traj[:, 0] / 20.0
cy = traj[:, 1] / 20.0
print('Lorenz trajectory computed, shape:', traj.shape)
pick_steps = [0, 500, 1500, 3000, 4500]
xs = np.linspace(-1.5, 1.5, N)
ys = np.linspace(-1.5, 1.5, N)
Xj, Yj = np.meshgrid(xs, ys)
Z0 = Xj + 1j * Yj
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
af = axes.flatten()
for i, ps in enumerate(pick_steps):
    c = complex(cx[ps], cy[ps])
    Z = Z0.copy()
    esc = np.full((N, N), max_iter, dtype=float)
    for it in range(max_iter):
        mask = np.abs(Z) <= 2
        Z[mask] = Z[mask]**2 + c
        newly = (np.abs(Z) > 2) & (esc == max_iter)
        esc[newly] = float(it)
    esc_norm = esc / max_iter
    af[i].imshow(esc_norm, cmap='magma', extent=[-1.5, 1.5, -1.5, 1.5])
    af[i].set_title('c = %.3f + %.3fi (step %d)' % (cx[ps], cy[ps], ps))
af[5].plot(traj[:, 0], traj[:, 1], 'b-', lw=0.5, alpha=0.5)
for ps in pick_steps:
    af[5].plot(traj[ps, 0], traj[ps, 1], 'ro', markersize=8)
af[5].set_title('Lorenz (x,y) plane with Julia c-points')
af[5].set_xlabel('x')
af[5].set_ylabel('y')
plt.suptitle('Resonance 5: Lorenz Attractor -> Julia Set', fontsize=13)
plt.tight_layout()
plt.savefig('resonance_lorenz_julia.png', dpi=150)
print('Saved resonance_lorenz_julia.png')
