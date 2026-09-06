"""
Phi^4 Kink-Antikink Collision Resonance Windows
================================================
The phi^4 model: u_tt - u_xx + u^3 - u = 0  (i.e. V(u) = (1/2)(u^2-1)^2)
Kink solution: u_K = tanh((x-x0)/sqrt(2))

Unlike the integrable Sine-Gordon, phi^4 is NOT integrable.
Kink-antikink collisions exhibit resonance windows:
- At certain velocities, kinks separate permanently (escape windows)
- At other velocities, they recapture and form a bound oscillating state (bion)
- The escape windows form a fractal (Cantor-like) set

We measure the fractal dimension of the escape velocity set.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

L = 400.0
N = 1024
dx = L / N
x = np.linspace(0, L, N, endpoint=False)
k = np.fft.fftfreq(N, d=dx) * 2 * np.pi
ik = 1j * k
k2 = k**2

def rhs(u, w):
    u_hat = np.fft.fft(u)
    u_xx = np.fft.ifft(-k2 * u_hat).real
    du_dt = w
    dw_dt = u_xx - (u**3 - u)  # V'(u) = u^3 - u
    return du_dt, dw_dt

def rk4_step(u, w, dt):
    k1u, k1w = rhs(u, w)
    k2u, k2w = rhs(u + 0.5*dt*k1u, w + 0.5*dt*k1w)
    k3u, k3w = rhs(u + 0.5*dt*k2u, w + 0.5*dt*k2w)
    k4u, k4w = rhs(u + dt*k3u, w + dt*k4w)
    u_new = u + (dt/6.0)*(k1u + 2*k2u + 2*k3u + k4u)
    w_new = w + (dt/6.0)*(k1w + 2*k2w + 2*k3w + k4w)
    return u_new, w_new

def phi4_energy(u, w):
    u_x = np.fft.ifft(ik * np.fft.fft(u)).real
    return np.sum(0.5*w**2 + 0.5*u_x**2 + 0.5*(u**2 - 1)**2) * dx

def kink_antikink_init(v, x1=150.0, x2=250.0):
    """Initialize kink at x1 moving right, antikink at x2 moving left."""
    sqrt2 = np.sqrt(2.0)
    # Lorentz factor
    gamma = 1.0 / np.sqrt(1 - v**2)
    # Kink: tanh(gamma*(x-x1)/sqrt(2)), moving right with velocity v
    # Antikink: -tanh(gamma*(x-x2)/sqrt(2)), moving left with velocity v
    u0 = np.tanh(gamma * (x - x1) / sqrt2) - np.tanh(gamma * (x - x2) / sqrt2) - 1.0
    # Actually: kink at x1 is tanh(...), antikink at x2 is -tanh(...)
    # u0 = tanh(g*(x-x1)/s2) + (-tanh(g*(x-x2)/s2)) = tanh(g*(x-x1)/s2) - tanh(g*(x-x2)/s2)
    # But we want vacuum u=-1 at far left, u=+1 between, u=-1 at far right
    # Kink goes from -1 to +1: tanh((x-x1)/s2)
    # Antikink goes from +1 to -1: -tanh((x-x2)/s2)  
    # Superposition: tanh(g*(x-x1)/s2) - tanh(g*(x-x2)/s2) - 1
    # At x << x1: tanh=-1, -tanh(g*(x-x2)/s2)≈+1, so u ≈ -1+1-1 = -1 ✓
    # At x1 < x < x2: tanh≈1, -tanh≈1, u ≈ 1+1-1 = 1 ✓  
    # At x >> x2: tanh≈1, -tanh≈-1, u ≈ 1-1-1 = -1 ✓
    
    # Time derivative: w = du/dt
    # Kink moving right: u_K = tanh(g*(x - x1 - v*t)/s2), du/dt = -g*v/s2 * sech^2(...)
    # Antikink moving left: u_AK = -tanh(g*(x - x2 + v*t)/s2), du/dt = -g*v/s2 * sech^2(...)
    # Wait: antikink moving left means x2 -> x2 - v*t, so argument is g*(x - x2 + v*t)/s2
    # du_AK/dt = -g*v/s2 * sech^2(g*(x-x2+v*t)/s2)
    
    sech1 = 1.0 / np.cosh(gamma * (x - x1) / sqrt2)
    sech2 = 1.0 / np.cosh(gamma * (x - x2) / sqrt2)
    w0 = -gamma * v / sqrt2 * sech1**2 - gamma * v / sqrt2 * sech2**2
    # Actually: kink du/dt = -g*v/s2 * sech^2(g*(x-x1)/s2) (moving right, x1 increases)
    # antikink du/dt = +g*v/s2 * sech^2(g*(x-x2)/s2) (moving left, x2 decreases)
    # Wait, let me be more careful.
    # Kink: u_K(x,t) = tanh(g*(x - x1 - v*t)/s2)
    #   du_K/dt = -g*v/s2 * sech^2(g*(x-x1-v*t)/s2)  [negative since kink moves right]
    # Antikink: u_AK(x,t) = -tanh(g*(x - x2 + v*t)/s2) 
    #   du_AK/dt = -g*v/s2 * sech^2(g*(x-x2+v*t)/s2)  [also negative]
    # Hmm, that doesn't seem right. Let me reconsider.
    # Antikink moving left: center at x2 - v*t, so u_AK = -tanh(g*(x - (x2-v*t))/s2) = -tanh(g*(x - x2 + v*t)/s2)
    # du_AK/dt = -(-g*v/s2) * sech^2(...) = ... 
    # d/dt[-tanh(g*(x-x2+v*t)/s2)] = -g*v/s2 * sech^2(g*(x-x2+v*t)/s2) * (-1) = g*v/s2 * sech^2(...)
    # No: d/dt[tanh(g*(x-x2+v*t)/s2)] = g*v/s2 * sech^2(...)
    # d/dt[-tanh(...)] = -g*v/s2 * sech^2(...)
    # Hmm, that gives both negative. But physically, antikink moving left means the 
    # transition region moves left, so at a fixed point, u first increases then decreases...
    
    # Let me just use: w0 for kink = -g*v/s2 * sech1^2
    # w0 for antikink (moving left) = +g*v/s2 * sech2^2
    w0 = -gamma * v / sqrt2 * sech1**2 + gamma * v / sqrt2 * sech2**2
    
    return u0, w0

# Test: single kink energy
sqrt2 = np.sqrt(2.0)
u_test = np.tanh((x - 200.0) / sqrt2)
w_test = np.zeros_like(x)
e_kink = phi4_energy(u_test, w_test)
print('Single kink energy: %.6f (expected 2*sqrt(2)/3 = %.6f)' % (e_kink, 2*np.sqrt(2)/3))

# Test kink-antikink initial condition
v_test = 0.3
u0, w0 = kink_antikink_init(v_test)
e0 = phi4_energy(u0, w0)
e_expected = 2 * (2*np.sqrt(2)/3) * (1.0/np.sqrt(1 - v_test**2))  # 2 kinks with Lorentz boost
print('Kink-antikink init: E=%.6f, expected=%.6f, ratio=%.4f' % (e0, e_expected, e0/e_expected))
print('u range: [%.4f, %.4f]' % (np.min(u0), np.max(u0)))

dt = 0.02

# Run a single collision to verify behavior
print('\n=== Test collision: v=0.3 ===')
u, w = u0.copy(), w0.copy()
t_max = 200.0
ns = int(t_max / dt)
nsave = max(1, ns // 300)
times, us = [], []
for i in range(ns):
    if i % nsave == 0:
        times.append(i * dt)
        us.append(u.copy())
    u, w = rk4_step(u, w, dt)
    if not np.isfinite(u).all() or np.max(np.abs(u)) > 10:
        print('Diverged at step %d' % i)
        break

times = np.array(times)
us = np.array(us)
print('Frames: %d, final u range: [%.4f, %.4f]' % (len(us), np.min(us[-1]), np.max(us[-1])))

# Track kink positions: find where u crosses zero
def find_kink_positions(u_arr, x_arr):
    """Find approximate kink positions by looking for sign changes."""
    # Kink: u goes from -1 to +1 (zero crossing going up)
    # Antikink: u goes from +1 to -1 (zero crossing going down)
    crossings = []
    for i in range(len(u_arr) - 1):
        if u_arr[i] * u_arr[i+1] < 0:
            # Linear interpolation for zero crossing
            xc = x_arr[i] + (0 - u_arr[i]) / (u_arr[i+1] - u_arr[i]) * (x_arr[i+1] - x_arr[i])
            crossings.append((xc, 1 if u_arr[i+1] > u_arr[i] else -1))
    return crossings

# Track center of mass of |u| deviation from -1
def track_energy_center(u_arr, x_arr, dx_val):
    """Track the energy-weighted center position."""
    dev = 0.5 * (u_arr**2 - 1)**2  # potential energy density
    total = np.sum(dev) * dx_val
    if total > 0:
        center = np.sum(x_arr * dev) * dx_val / total
    else:
        center = 200.0
    return center

# Track separation over time for the test case
centers = []
u_track, w_track = u0.copy(), w0.copy()
for i in range(ns):
    if i % 50 == 0:
        c = track_energy_center(u_track, x, dx)
        centers.append((i * dt, c))
    u_track, w_track = rk4_step(u_track, w_track, dt)
    if not np.isfinite(u_track).all() or np.max(np.abs(u_track)) > 10:
        break

centers = np.array(centers)
print('Energy center trajectory: start=%.1f, end=%.1f' % (centers[0, 1], centers[-1, 1]))

# Plot test collision
fig, ax = plt.subplots(figsize=(16, 8))
im = ax.imshow(us, aspect='auto', cmap='RdBu_r',
               extent=[0, L, times[-1], 0], interpolation='bilinear',
               vmin=-1.5, vmax=1.5)
ax.set_xlabel('x')
ax.set_ylabel('Time')
ax.set_title('Phi^4 Kink-Antikink Collision (v=%.2f)' % v_test, fontsize=14, fontweight='bold')
plt.colorbar(im, ax=ax, label='u(x,t)')
plt.tight_layout()
plt.savefig('phi4_test_collision.png', dpi=150)
plt.close()
print('Saved phi4_test_collision.png')

# Plot energy center trajectory
fig2, ax2 = plt.subplots(figsize=(12, 5))
ax2.plot(centers[:, 0], centers[:, 1], 'darkblue', linewidth=1.5)
ax2.set_xlabel('Time')
ax2.set_ylabel('Energy-weighted center')
ax2.set_title('Energy Center Position (v=%.2f)' % v_test, fontsize=14, fontweight='bold')
ax2.axhline(y=200.0, color='red', linestyle='--', alpha=0.5, label='Symmetry center')
ax2.legend()
plt.tight_layout()
plt.savefig('phi4_energy_center.png', dpi=150)
plt.close()
print('Saved phi4_energy_center.png')

print('\nDone with test phase.')
