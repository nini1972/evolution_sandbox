"""
Phi^4 Resonance Windows - Ultra Fast
=====================================
Minimal grid, minimal time, but enough to see fractal structure.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

L = 120.0
N = 256
dx = L / N
x = np.linspace(0, L, N, endpoint=False)
k = np.fft.fftfreq(N, d=dx) * 2 * np.pi
k2 = k**2

def rk4_step(u, w, dt):
    u_hat = np.fft.fft(u)
    u_xx = np.fft.ifft(-k2 * u_hat).real
    k1u, k1w = w, u_xx - (u**3 - u)
    u2 = u + 0.5*dt*k1u; w2 = w + 0.5*dt*k1w
    u_xx2 = np.fft.ifft(-k2 * np.fft.fft(u2)).real
    k2u, k2w = w2, u_xx2 - (u2**3 - u2)
    u3 = u + 0.5*dt*k2u; w3 = w + 0.5*dt*k2w
    u_xx3 = np.fft.ifft(-k2 * np.fft.fft(u3)).real
    k3u, k3w = w3, u_xx3 - (u3**3 - u3)
    u4 = u + dt*k3u; w4 = w + dt*k3w
    u_xx4 = np.fft.ifft(-k2 * np.fft.fft(u4)).real
    k4u, k4w = w4, u_xx4 - (u4**3 - u4)
    u_new = u + (dt/6.0)*(k1u + 2*k2u + 2*k3u + k4u)
    w_new = w + (dt/6.0)*(k1w + 2*k2w + 2*k3w + k4w)
    return u_new, w_new

def run_collision(v, t_max=80.0, dt=0.1):
    sqrt2 = np.sqrt(2.0)
    gamma = 1.0 / np.sqrt(1 - v**2)
    x1, x2 = 48.0, 72.0
    u = np.tanh(gamma * (x - x1) / sqrt2) - np.tanh(gamma * (x - x2) / sqrt2) - 1.0
    sech1 = 1.0 / np.cosh(gamma * (x - x1) / sqrt2)
    sech2 = 1.0 / np.cosh(gamma * (x - x2) / sqrt2)
    w = -gamma * v / sqrt2 * sech1**2 + gamma * v / sqrt2 * sech2**2
    
    ns = int(t_max / dt)
    center0 = 60.0
    late_centers = []
    all_centers = []
    
    for i in range(ns):
        if i % 5 == 0:
            dev = 0.25 * (u**2 - 1)**2
            total = np.sum(dev) * dx
            center = np.sum(x * dev) * dx / total if total > 1e-10 else center0
            all_centers.append(center)
            if i > ns * 2 // 3:
                late_centers.append(center)
        
        u, w = rk4_step(u, w, dt)
        if not np.isfinite(u).all() or np.max(np.abs(u)) > 10:
            return {'v': v, 'outcome': 'diverged', 'max_dev': 0, 'final_center': 0}
    
    late_centers = np.array(late_centers)
    all_centers = np.array(all_centers)
    
    if len(late_centers) == 0:
        return {'v': v, 'outcome': 'bion', 'max_dev': 0, 'final_center': center0}
    
    max_dev = np.max(np.abs(late_centers - center0))
    
    # Also check final field: is it oscillating near center or has it separated?
    final_dev = 0.25 * (u**2 - 1)**2
    # Count peaks
    from scipy.signal import find_peaks
    peaks, _ = find_peaks(final_dev, height=0.005, distance=5)
    n_peaks = len(peaks)
    
    if max_dev > 15 or n_peaks >= 2:
        outcome = 'escape'
    else:
        outcome = 'bion'
    
    final_center = all_centers[-1] if len(all_centers) > 0 else center0
    
    return {'v': v, 'outcome': outcome, 'max_dev': float(max_dev), 
            'final_center': float(final_center), 'n_peaks': n_peaks}

# Quick test
print("=== Quick test ===")
for v in [0.1, 0.2, 0.25, 0.3, 0.4]:
    r = run_collision(v)
    print(f"v={v:.3f}: {r['outcome']}, max_dev={r['max_dev']:.1f}, n_peaks={r['n_peaks']}")

# Main scan
print("\n=== Main scan (200 velocities) ===")
velocities = np.linspace(0.15, 0.55, 200)
results = []
for i, v in enumerate(velocities):
    r = run_collision(v)
    results.append(r)

# Plot
fig, axes = plt.subplots(2, 1, figsize=(16, 10))

vs = [r['v'] for r in results]
outcomes = [1 if r['outcome'] == 'escape' else 0 for r in results]
colors = ['green' if o else 'red' for o in outcomes]

ax = axes[0]
ax.scatter(vs, outcomes, c=colors, s=12, alpha=0.8)
ax.set_xlabel('v')
ax.set_ylabel('escape=1, bion=0')
ax.set_title('Phi^4 Kink-Antikink Resonance Windows', fontsize=14, fontweight='bold')

ax = axes[1]
ax.scatter(vs, [r['max_dev'] for r in results], c=colors, s=12, alpha=0.8)
ax.set_xlabel('v')
ax.set_ylabel('Max energy center deviation')
ax.set_title('Energy Center Displacement (green=escape, red=bion)', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('phi4_resonance_windows.png', dpi=150)
plt.close()

escape_vs = [r['v'] for r in results if r['outcome'] == 'escape']
print(f"\nEscape: {len(escape_vs)}, Bion: {len(results)-len(escape_vs)}")
if escape_vs:
    print(f"Escape range: [{min(escape_vs):.4f}, {max(escape_vs):.4f}]")
print("Done!")
