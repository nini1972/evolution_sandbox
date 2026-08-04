import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = '../../shared_space/complexity_atlas_phase_space.png'

# Common parameter grids for comparison
x = np.linspace(-2.0, 1.0, 360)
y = np.linspace(-1.25, 1.25, 360)
X, Y = np.meshgrid(x, y)

# 1. Mandelbrot escape-time landscape
Z = X + 1j * Y
C = Z.copy()
escape = np.zeros(Z.shape, dtype=int)
mask = np.ones(Z.shape, dtype=bool)
for n in range(1, 50):
    Z[mask] = Z[mask] * Z[mask] + C[mask]
    escaped = np.abs(Z) > 2.0
    newly = escaped & mask
    escape[newly] = n
    mask &= ~escaped
mandel = np.where(escape == 0, 0, 1.0 / np.log1p(escape))

# 2. Julia set for c = -0.7269 + 0.1889i
c = -0.7269 + 0.1889j
Z = X + 1j * Y
escape = np.zeros(Z.shape, dtype=int)
mask = np.ones(Z.shape, dtype=bool)
for n in range(1, 50):
    Z[mask] = Z[mask] * Z[mask] + c
    escaped = np.abs(Z) > 2.0
    newly = escaped & mask
    escape[newly] = n
    mask &= ~escaped
julia = np.where(escape == 0, 0, 1.0 / np.log1p(escape))

# 3. Logistic map bifurcation proxy: entropy-like diversity over r values
r = np.linspace(2.5, 4.0, 360)
entropy = np.zeros_like(r)
for i, rr in enumerate(r):
    z = 0.5
    orbit = []
    for _ in range(500):
        z = rr * z * (1 - z)
    samples = np.array([z := rr * z * (1 - z) for _ in range(1000)])
    hist, _ = np.histogram(samples, bins=80, range=(0, 1), density=True)
    hist = hist / (hist.sum() + 1e-12)
    entropy[i] = -np.sum(hist * np.log(hist + 1e-12))

# 4. Rule 30 entropy proxy over initial seed density
width = 180
steps = 180
densities = np.linspace(0.0, 1.0, 360)
rule30_entropy = []
for rho in densities:
    rng = np.random.default_rng(int(round(rho * 10000)))
    row = (rng.random(width) < rho).astype(np.uint8)
    entropies = []
    for _ in range(steps):
        # left/right shifted with null boundary
        left = np.r_[0, row[:-1]]
        right = np.r_[row[1:], 0]
        row = left ^ (row | right)
        p = row.mean()
        if p > 0 and p < 1:
            entropies.append(-p*np.log(p) - (1-p)*np.log(1-p))
    rule30_entropy.append(np.mean(entropies) if entropies else 0)
rule30_entropy = np.array(rule30_entropy)

# 5. Kuramoto order parameter proxy over coupling K
N = 60
rng = np.random.default_rng(42)
omega = rng.normal(0, 1, N)
theta0 = rng.random(N) * 2*np.pi
Ks = np.linspace(0.0, 4.0, 360)
R = []
for K in Ks:
    theta = theta0.copy()
    dt = 0.02
    for _ in range(300):
        mean_phase = np.angle(np.mean(np.exp(1j*theta)))
        theta = (theta + dt * (omega + K * np.sin(mean_phase - theta))) % (2*np.pi)
    order = np.abs(np.mean(np.exp(1j*theta)))
    R.append(order)
R = np.array(R)

# Compose figure
fig = plt.figure(figsize=(18, 10), facecolor='#0b1020')
fig.suptitle('Complexity Atlas: Escape, Entropy, and Synchronization Landscapes',
             color='white', fontsize=18, y=0.98)

# Mandelbrot
ax = fig.add_subplot(2, 3, 1)
im = ax.imshow(mandel, extent=[x.min(), x.max(), y.min(), y.max()], origin='lower',
               cmap='magma', aspect='auto')
ax.set_title('Mandelbrot escape-time complexity', color='white')
ax.set_xlabel('Re(c)'); ax.set_ylabel('Im(c)')
ax.tick_params(colors='white'); ax.xaxis.label.set_color('white'); ax.yaxis.label.set_color('white')
fig.colorbar(im, ax=ax, label='escape contrast', shrink=0.75)

# Julia
ax = fig.add_subplot(2, 3, 2)
im = ax.imshow(julia, extent=[x.min(), x.max(), y.min(), y.max()], origin='lower',
               cmap='inferno', aspect='auto')
ax.set_title('Julia set: c = -0.7269 + 0.1889i', color='white')
ax.set_xlabel('Re(z)'); ax.set_ylabel('Im(z)')
ax.tick_params(colors='white'); ax.xaxis.label.set_color('white'); ax.yaxis.label.set_color('white')
fig.colorbar(im, ax=ax, label='escape contrast', shrink=0.75)

# Logistic entropy
ax = fig.add_subplot(2, 3, 3)
ax.plot(r, entropy, color='#00d1ff', lw=2)
ax.fill_between(r, entropy, alpha=0.2, color='#00d1ff')
ax.set_title('Logistic map entropy over r', color='white')
ax.set_xlabel('growth rate r'); ax.set_ylabel('Shannon entropy')
ax.set_xlim(2.5, 4.0); ax.set_ylim(0, entropy.max()*1.05)
ax.grid(alpha=0.3); ax.tick_params(colors='white'); ax.xaxis.label.set_color('white'); ax.yaxis.label.set_color('white')

# Rule 30 entropy
ax = fig.add_subplot(2, 3, 4)
ax.plot(densities, rule30_entropy, color='#a855f7', lw=2)
ax.fill_between(densities, rule30_entropy, alpha=0.2, color='#a855f7')
ax.set_title('Rule 30 density-to-entropy response', color='white')
ax.set_xlabel('initial density'); ax.set_ylabel('mean binary entropy')
ax.grid(alpha=0.3); ax.tick_params(colors='white'); ax.xaxis.label.set_color('white'); ax.yaxis.label.set_color('white')

# Kuramoto order
ax = fig.add_subplot(2, 3, 5)
ax.plot(Ks, R, color='#22c55e', lw=2)
ax.fill_between(Ks, R, alpha=0.2, color='#22c55e')
ax.set_title('Kuramoto synchronization order parameter', color='white')
ax.set_xlabel('coupling K'); ax.set_ylabel('|order parameter|')
ax.set_ylim(-0.02, 1.02); ax.grid(alpha=0.3)
ax.tick_params(colors='white'); ax.xaxis.label.set_color('white'); ax.yaxis.label.set_color('white')

# Composite summary: normalized signatures
ax = fig.add_subplot(2, 3, 6)
def norm(a):
    a = np.asarray(a, dtype=float)
    mn, mx = a.min(), a.max()
    if mx == mn:
        return np.zeros_like(a)
    return (a - mn) / (mx - mn)
ax.plot(r, norm(entropy), color='#00d1ff', lw=1.8, label='logistic entropy')
ax.plot(densities, norm(rule30_entropy), color='#a855f7', lw=1.8, label='rule30 entropy')
ax.plot(Ks, norm(R), color='#22c55e', lw=1.8, label='Kuramoto order')
ax.set_title('Normalized signatures of complexity transitions', color='white')
ax.set_xlabel('parameter sweep')
ax.set_ylabel('normalized response')
ax.grid(alpha=0.3); ax.legend(facecolor='#111827', edgecolor='#334155', labelcolor='white')
ax.tick_params(colors='white'); ax.xaxis.label.set_color('white'); ax.yaxis.label.set_color('white')

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig(OUT, dpi=180, facecolor=fig.get_facecolor())
plt.close(fig)

print(OUT)
