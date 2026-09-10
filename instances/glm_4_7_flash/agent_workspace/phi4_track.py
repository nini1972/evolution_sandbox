import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

L = 400.0; N = 512; dx = L/N
x = np.linspace(0, L, N, endpoint=False)
k = np.fft.fftfreq(N, d=dx) * 2*np.pi
k2fac = -k**2

def uxx(u):
    return np.fft.ifft(k2fac * np.fft.fft(u)).real

def run_track(v, t_max=600, dt=0.25):
    s2 = np.sqrt(2.0); g = 1.0/np.sqrt(1-v**2)
    x1, x2 = 150.0, 250.0
    u = np.tanh(g*(x-x1)/s2) - np.tanh(g*(x-x2)/s2) - 1.0
    sech1 = 1.0/np.cosh(g*(x-x1)/s2)
    sech2 = 1.0/np.cosh(g*(x-x2)/s2)
    w = -g*v/s2 * sech1**2 - g*v/s2 * sech2**2
    ns = int(t_max/dt)
    ux = uxx(u)
    
    t_arr = []
    u_center = []
    u_max = []
    u_min = []
    
    for i in range(ns):
        w += 0.5*dt*(ux - (u**3 - u))
        u += dt*w
        ux = uxx(u)
        w += 0.5*dt*(ux - (u**3 - u))
        if i % 4 == 0:
            t_arr.append(i*dt)
            u_center.append(u[N//2])
            u_max.append(np.max(u))
            u_min.append(np.min(u))
        if not np.isfinite(u).all() or np.max(np.abs(u))>10:
            break
    
    return np.array(t_arr), np.array(u_center), np.array(u_max), np.array(u_min)

# Check what happens at various velocities
fig, axes = plt.subplots(5, 1, figsize=(16, 20))
for idx, v in enumerate([0.1, 0.2, 0.3, 0.4, 0.5]):
    t, uc, umax, umin = run_track(v, t_max=600)
    axes[idx].plot(t, uc, 'b-', label='u(center)', alpha=0.8)
    axes[idx].plot(t, umax, 'r-', label='u_max', alpha=0.5)
    axes[idx].plot(t, umin, 'g-', label='u_min', alpha=0.5)
    axes[idx].set_title(f'v={v}')
    axes[idx].set_ylabel('phi')
    axes[idx].legend()
    axes[idx].set_ylim(-3, 3)
axes[-1].set_xlabel('time')
plt.tight_layout()
plt.savefig('phi4_field_track.png', dpi=150)
plt.close()
print('Saved phi4_field_track.png')

# Print some data
for v in [0.1, 0.3, 0.5]:
    t, uc, umax, umin = run_track(v, t_max=600)
    # Find collision time (when u_center first deviates significantly from 1)
    dev_idx = np.where(np.abs(uc - 1.0) > 0.1)[0]
    if len(dev_idx) > 0:
        t_collision = t[dev_idx[0]]
        print(f'v={v}: collision at t={t_collision:.1f}, final u_center={uc[-1]:.3f}, final u_max={umax[-1]:.3f}, final u_min={umin[-1]:.3f}')
    else:
        print(f'v={v}: no collision detected, final u_center={uc[-1]:.3f}')