"""M23: Test Hénon, Ikeda, and Tinkerbell maps against Adler ceiling."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def band_frac(arr, lo_frac=0.3, hi_frac=0.7):
    lo = arr.min() + lo_frac * (arr.max() - arr.min())
    hi = arr.min() + hi_frac * (arr.max() - arr.min())
    return ((arr >= lo) & (arr <= hi)).mean()

# Hénon map: x_{n+1} = 1 - a*x_n^2 + y_n, y_{n+1} = b*x_n
# Chaotic at a=1.4, b=0.3
def henon(n_steps, a=1.4, b=0.3, x0=0.1, y0=0.1):
    xs = np.zeros(n_steps)
    ys = np.zeros(n_steps)
    x, y = x0, y0
    for i in range(n_steps):
        x_new = 1 - a * x * x + y
        y_new = b * x
        x, y = x_new, y_new
        xs[i] = x
        ys[i] = y
    return xs, ys

# Ikeda map: from laser physics
# z_{n+1} = 1 + u*(z_n*exp(...) - 6*...)
def ikeda(n_steps, u=0.9, x0=0.1, y0=0.1):
    xs = np.zeros(n_steps)
    ys = np.zeros(n_steps)
    x, y = x0, y0
    for i in range(n_steps):
        r2 = x*x + y*y
        # Ikeda with standard parameters
        # t = 0.4 - 6/(1+r2)
        t = 0.4 - 6.0 / (1.0 + r2)
        x_new = 1 + u * (x * np.cos(t) - y * np.sin(t))
        y_new = u * (x * np.sin(t) + y * np.cos(t))
        x, y = x_new, y_new
        xs[i] = x
        ys[i] = y
    return xs, ys

# Tinkerbell map: 2D discrete with chaotic attractor
# x_{n+1} = x^2 - y^2 + a*x + b*y
# y_{n+1} = 2*x*y + c*x + d*y
def tinkerbell(n_steps, a=0.9, b=-0.6013, c=2.0, d=0.5, x0=0.1, y0=0.1):
    xs = np.zeros(n_steps)
    ys = np.zeros(n_steps)
    x, y = x0, y0
    for i in range(n_steps):
        x_new = x*x - y*y + a*x + b*y
        y_new = 2*x*y + c*x + d*y
        x, y = x_new, y_new
        xs[i] = x
        ys[i] = y
    return xs, ys

# Test all three
print('=== Hénon Map (a=1.4, b=0.3) ===')
xs, ys = henon(n_steps=20000)
xs = xs[2000:]; ys = ys[2000:]
bf_x = band_frac(xs)
bf_y = band_frac(ys)
print(f'  x: bf = {bf_x:.4f}')
print(f'  y: bf = {bf_y:.4f}')
print(f'  mean: bf = {(bf_x+bf_y)/2:.4f}')
print(f'  R = {((bf_x+bf_y)/2)/0.4142:.3f}')

# Sweep Hénon a
print('\nHénon a sweep (b=0.3):')
for a in [0.5, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]:
    xs, ys = henon(n_steps=15000, a=a)
    xs = xs[1500:]; ys = ys[1500:]
    bf_x = band_frac(xs)
    bf_y = band_frac(ys)
    print(f'  a={a}: x={bf_x:.4f}, y={bf_y:.4f}, mean={(bf_x+bf_y)/2:.4f}')

print('\n=== Ikeda Map (u=0.9) ===')
xs, ys = ikeda(n_steps=20000)
xs = xs[2000:]; ys = ys[2000:]
bf_x = band_frac(xs)
bf_y = band_frac(ys)
print(f'  x: bf = {bf_x:.4f}')
print(f'  y: bf = {bf_y:.4f}')
print(f'  mean: bf = {(bf_x+bf_y)/2:.4f}')
print(f'  R = {((bf_x+bf_y)/2)/0.4142:.3f}')

print('\n=== Tinkerbell Map ===')
xs, ys = tinkerbell(n_steps=20000)
xs = xs[2000:]; ys = ys[2000:]
bf_x = band_frac(xs)
bf_y = band_frac(ys)
print(f'  x: bf = {bf_x:.4f}')
print(f'  y: bf = {bf_y:.4f}')
print(f'  mean: bf = {(bf_x+bf_y)/2:.4f}')
print(f'  R = {((bf_x+bf_y)/2)/0.4142:.3f}')

# Combined plot: phase portraits
fig, axes = plt.subplots(2, 3, figsize=(15, 10))

# Hénon phase portrait
ax = axes[0, 0]
xs, ys = henon(n_steps=20000)
xs = xs[2000:]; ys = ys[2000:]
ax.scatter(xs[::5], ys[::5], s=0.5, alpha=0.4, c='C0')
ax.set_xlabel('x')
ax.set_ylabel('y')
bf_x = band_frac(xs); bf_y = band_frac(ys)
ax.set_title(f'Hénon (a=1.4)\nbf_x={bf_x:.3f}, bf_y={bf_y:.3f}')

# Hénon bf vs a
ax = axes[0, 1]
a_vals = []
mean_bfs = []
for a in np.linspace(0.3, 1.5, 25):
    xs, ys = henon(n_steps=8000, a=a)
    xs = xs[800:]; ys = ys[800:]
    bf_x = band_frac(xs)
    bf_y = band_frac(ys)
    mean_bf = (bf_x + bf_y) / 2
    a_vals.append(a)
    mean_bfs.append(mean_bf)
ax.plot(a_vals, mean_bfs, 'o-', linewidth=2)
ax.axhline(0.414, color='red', linestyle='--', label='Adler ceiling')
ax.axhline(0.4, color='gray', linestyle=':', label='uniform (0.4)')
ax.set_xlabel('a (Hénon parameter)')
ax.set_ylabel('mean bf')
ax.set_title('Hénon bf vs a')
ax.legend()
ax.grid(True, alpha=0.3)

# Ikeda phase portrait
ax = axes[0, 2]
xs, ys = ikeda(n_steps=20000)
xs = xs[2000:]; ys = ys[2000:]
ax.scatter(xs[::5], ys[::5], s=0.5, alpha=0.4, c='C1')
ax.set_xlabel('x')
ax.set_ylabel('y')
bf_x = band_frac(xs); bf_y = band_frac(ys)
ax.set_title(f'Ikeda (u=0.9)\nbf_x={bf_x:.3f}, bf_y={bf_y:.3f}')

# Tinkerbell phase portrait
ax = axes[1, 0]
xs, ys = tinkerbell(n_steps=20000)
xs = xs[2000:]; ys = ys[2000:]
ax.scatter(xs[::5], ys[::5], s=0.5, alpha=0.4, c='C2')
ax.set_xlabel('x')
ax.set_ylabel('y')
bf_x = band_frac(xs); bf_y = band_frac(ys)
ax.set_title(f'Tinkerbell\nbf_x={bf_x:.3f}, bf_y={bf_y:.3f}')

# Comparison bar chart
ax = axes[1, 1]
systems = ['Hénon\n(a=1.4)', 'Ikeda\n(u=0.9)', 'Tinkerbell', 'Rössler\n(c=5.7)', 'Lorenz\n(ρ=28)']
# Compute fresh values
xs, ys = henon(n_steps=20000); xs = xs[2000:]; ys = ys[2000:]
bfs = [(band_frac(xs) + band_frac(ys))/2]
xs, ys = ikeda(n_steps=20000); xs = xs[2000:]; ys = ys[2000:]
bfs.append((band_frac(xs) + band_frac(ys))/2)
xs, ys = tinkerbell(n_steps=20000); xs = xs[2000:]; ys = ys[2000:]
bfs.append((band_frac(xs) + band_frac(ys))/2)
bfs.append(0.37)  # Rössler c=5.7
bfs.append(0.68)  # Lorenz ρ=28

x_pos = np.arange(len(systems))
colors = ['C0', 'C1', 'C2', 'C3', 'red']
bars = ax.bar(x_pos, bfs, color=colors, alpha=0.7)
ax.axhline(0.414, color='red', linestyle='--', label='Adler ceiling (0.414)')
ax.axhline(0.4, color='gray', linestyle=':', label='uniform (0.4)')
ax.set_xticks(x_pos)
ax.set_xticklabels(systems, rotation=0, fontsize=9)
ax.set_ylabel('mean band fraction')
ax.set_title('M23: Multiple Chaotic Systems vs Adler Ceiling')
ax.legend()
ax.grid(True, alpha=0.3)

# Add R values
for i, bf in enumerate(bfs):
    r = bf / 0.4142
    ax.text(i, bf + 0.01, f'R={r:.2f}', ha='center', fontsize=9)

# Summary
ax = axes[1, 2]
ax.axis('off')
summary = """M23 Summary:

Hénon (2D, discrete, two-wing):     0.40-0.45 (at ceiling)
Ikeda (2D, discrete, spiral):       ?
Tinkerbell (2D, discrete):          ?
Rössler (3D, continuous, coherent): 0.40 (at ceiling)
Lorenz (3D, continuous, two-wing):  0.68 (ABOVE ceiling)

Emerging pattern:
  - 2D discrete maps: usually at ceiling
  - Phase-coherent 3D: at ceiling
  - Two-wing 3D (Lorenz): ABOVE ceiling

Key test: is the "two-wing" topology the determining factor?
"""
ax.text(0.0, 1.0, summary, fontsize=10, family='monospace', va='top')

plt.suptitle('M23: Multiple Chaotic Systems — Testing the Topology Hypothesis',
             fontsize=14, y=1.00)
plt.tight_layout()
plt.savefig('_artifacts/m23_multi_chaos.png', dpi=110, bbox_inches='tight')
print('\nSaved m23_multi_chaos.png')