"""
Phi^4 Resonance Windows - Strang Splitting
===========================================
Use Strang splitting for speed: half-step potential, full-step linear, half-step potential.
This avoids 4 FFTs per RK4 step (only needs 2 FFTs per full step).
u_tt = u_xx - (u^3 - u)

Write as first-order: u_t = w, w_t = u_xx - V'(u)
Split into:
  H1: u_t = w (potential part, w_t = -V'(u))  -> but this doesn't split cleanly
  
Better: Use symplectic Euler or leapfrog.
u_t = w, w_t = u_xx - (u^3 - u)

Leapfrog: 
  w_{n+1/2} = w_n + 0.5*dt * (u_xx^n - (u_n^3 - u_n))
  u_{n+1} = u_n + dt * w_{n+1/2}  
  w_{n+1} = w_{n+1/2} + 0.5*dt * (u_xx^{n+1} - (u_{n+1}^3 - u_{n+1}))
This needs 2 FFTs per step (for u_xx at two time levels).
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

L = 120.0
N = 256
dx = L / N
x = np.linspace(0, L, N, endpoint=False)
k = np.fft.fftfreq(N, d=dx) * 2 * np.pi
k2 = k**2
u_xx_hat_factor = -k2  # multiply fft(u) by this to get fft(u_xx)

def u_xx(u):
    return np.fft.ifft(u_xx_hat_factor * np.fft.fft(u)).real

def run_collision(v, t_max=100.0, dt=0.1):
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
    
    # First u_xx
    uxx = u_xx(u)
    
    for i in range(ns):
        # Leapfrog (kick-drift-kick)
        w += 0.5 * dt * (uxx - (u**3 - u))
        u += dt * w
        uxx = u_xx(u)  # Only 1 FFT per step!
        w += 0.5 * dt * (uxx - (u**3 - u))
        
        if i % 10 == 0 and i > ns * 2 // 3:
            dev = 0.25 * (u**2 - 1)**2
            total = np.sum(dev) * dx
            center = np.sum(x * dev) * dx / total if total > 1e-10 else center0
            late_centers.append(center)
        
        if not np.isfinite(u).all() or np.max(np.abs(u)) > 10:
            return {'v': v, 'outcome': 'diverged', 'max_dev': 0, 'n_peaks': 0}
    
    late_centers = np.array(late_centers)
    if len(late_centers) == 0:
        return {'v': v, 'outcome': 'bion', 'max_dev': 0, 'n_peaks': 0}
    
    max_dev = np.max(np.abs(late_centers - center0))
    
    # Count peaks in final energy density
    final_dev = 0.25 * (u**2 - 1)**2
    from scipy.signal import find_peaks
    peaks, _ = find_peaks(final_dev, height=0.005, distance=5)
    n_peaks = len(peaks)
    
    if max_dev > 15 or n_peaks >= 2:
        outcome = 'escape'
    else:
        outcome = 'bion'
    
    return {'v': v, 'outcome': outcome, 'max_dev': float(max_dev), 'n_peaks': n_peaks}

# Quick test
print("=== Quick test ===")
for v in [0.1, 0.2, 0.25, 0.3, 0.4]:
    r = run_collision(v)
    print(f"v={v:.3f}: {r['outcome']}, max_dev={r['max_dev']:.1f}, n_peaks={r['n_peaks']}")

# Main scan
print("\n=== Main scan ===")
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
ax.set_ylim(-0.1, 1.1)

ax = axes[1]
ax.scatter(vs, [r['max_dev'] for r in results], c=colors, s=12, alpha=0.8)
ax.set_xlabel('v')
ax.set_ylabel('Max energy center deviation')
ax.set_title('Energy Center Displacement', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('phi4_resonance_windows.png', dpi=150)
plt.close()

escape_vs = [r['v'] for r in results if r['outcome'] == 'escape']
print(f"\nEscape: {len(escape_vs)}, Bion: {len(results)-len(escape_vs)}")
if escape_vs:
    print(f"Escape range: [{min(escape_vs):.4f}, {max(escape_vs):.4f}]")
print("Done!")
