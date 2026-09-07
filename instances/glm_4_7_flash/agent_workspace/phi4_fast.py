"""
Phi^4 Resonance Window Scanner - Optimized
============================================
Fast FFT-based phi^4 kink-antikink collision simulation.
Scans velocities to map fractal resonance window structure.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

# Compact domain
L = 200.0
N = 512
dx = L / N
x = np.linspace(0, L, N, endpoint=False)
k = np.fft.fftfreq(N, d=dx) * 2 * np.pi
ik = 1j * k
k2 = k**2

def rhs(u, w):
    u_hat = np.fft.fft(u)
    u_xx = np.fft.ifft(-k2 * u_hat).real
    return w, u_xx - (u**3 - u)

def rk4_step(u, w, dt):
    k1u, k1w = rhs(u, w)
    k2u, k2w = rhs(u + 0.5*dt*k1u, w + 0.5*dt*k1w)
    k3u, k3w = rhs(u + 0.5*dt*k2u, w + 0.5*dt*k2w)
    k4u, k4w = rhs(u + dt*k3u, w + dt*k3w)
    u_new = u + (dt/6.0)*(k1u + 2*k2u + 2*k3u + k4u)
    w_new = w + (dt/6.0)*(k1w + 2*k2w + 2*k3w + k4w)
    return u_new, w_new

def kink_antikink_init(v, x1=80.0, x2=120.0):
    sqrt2 = np.sqrt(2.0)
    gamma = 1.0 / np.sqrt(1 - v**2)
    u0 = np.tanh(gamma * (x - x1) / sqrt2) - np.tanh(gamma * (x - x2) / sqrt2) - 1.0
    sech1 = 1.0 / np.cosh(gamma * (x - x1) / sqrt2)
    sech2 = 1.0 / np.cosh(gamma * (x - x2) / sqrt2)
    w0 = -gamma * v / sqrt2 * sech1**2 + gamma * v / sqrt2 * sech2**2
    return u0, w0

def run_collision(v, t_max=150.0, dt=0.05):
    """Run collision, classify outcome."""
    u, w = kink_antikink_init(v)
    ns = int(t_max / dt)
    
    # Track energy center at several time points
    centers = []
    for i in range(ns):
        if i % 10 == 0:
            dev = 0.25 * (u**2 - 1)**2
            total = np.sum(dev) * dx
            if total > 1e-10:
                center = np.sum(x * dev) * dx / total
            else:
                center = 100.0
            centers.append(center)
        
        u, w = rk4_step(u, w, dt)
        if not np.isfinite(u).all() or np.max(np.abs(u)) > 10:
            return {'v': v, 'outcome': 'diverged', 'max_dev': 0, 'std_dev': 0}
    
    centers = np.array(centers)
    
    # Late-time behavior
    late = centers[len(centers)*2//3:]
    max_dev = np.max(np.abs(late - 100))
    std_dev = np.std(late)
    
    # Classify: escape if center moves far and keeps moving
    # Bion: center oscillates near 100
    if max_dev > 25 and std_dev > 5:
        outcome = 'escape'
    else:
        outcome = 'bion'
    
    return {'v': v, 'outcome': outcome, 'max_dev': max_dev, 'std_dev': std_dev}

# Test a few velocities
print("=== Test velocities ===")
for v in [0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]:
    r = run_collision(v)
    print(f"v={v:.3f}: {r['outcome']}, max_dev={r['max_dev']:.1f}, std={r['std_dev']:.1f}")

# Main scan
print("\n=== Main scan ===")
velocities = np.linspace(0.15, 0.55, 300)
results = []
for i, v in enumerate(velocities):
    r = run_collision(v)
    results.append(r)
    if (i+1) % 50 == 0:
        n_esc = sum(1 for r in results if r['outcome'] == 'escape')
        print(f"  {i+1}/300, escapes so far: {n_esc}")

# Save
with open('phi4_scan.json', 'w') as f:
    json.dump(results, f)

# Plot
fig, axes = plt.subplots(2, 1, figsize=(16, 10))

vs = [r['v'] for r in results]
outcomes = [1 if r['outcome'] == 'escape' else 0 for r in results]
colors = ['green' if o else 'red' for o in outcomes]

ax = axes[0]
ax.scatter(vs, outcomes, c=colors, s=10, alpha=0.7)
ax.set_xlabel('Initial velocity v')
ax.set_ylabel('Outcome (1=escape, 0=bion)')
ax.set_title('Phi^4 Kink-Antikink: Resonance Window Structure', fontsize=14, fontweight='bold')
ax.set_ylim(-0.1, 1.1)

ax = axes[1]
max_devs = [r['max_dev'] for r in results]
ax.scatter(vs, max_devs, c=colors, s=10, alpha=0.7)
ax.set_xlabel('Initial velocity v')
ax.set_ylabel('Max energy center deviation')
ax.set_title('Energy Center Displacement', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('phi4_resonance_windows.png', dpi=150)
plt.close()
print("Saved phi4_resonance_windows.png")

escape_vs = [r['v'] for r in results if r['outcome'] == 'escape']
print(f"\nEscape: {len(escape_vs)}, Bion: {len(results)-len(escape_vs)}")
if escape_vs:
    print(f"Escape range: [{min(escape_vs):.4f}, {max(escape_vs):.4f}]")

print("Done!")
