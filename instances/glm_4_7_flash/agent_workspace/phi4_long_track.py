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

def run(v, t_max=800, dt=0.25):
    s2 = np.sqrt(2.0); g = 1.0/np.sqrt(1-v**2)
    x1, x2 = 150.0, 250.0
    u = np.tanh(g*(x-x1)/s2) - np.tanh(g*(x-x2)/s2) - 1.0
    sech1 = 1.0/np.cosh(g*(x-x1)/s2)
    sech2 = 1.0/np.cosh(g*(x-x2)/s2)
    w = -g*v/s2 * sech1**2 - g*v/s2 * sech2**2
    ns = int(t_max/dt)
    ux = uxx(u)
    
    t_arr = []
    u_center_arr = []
    
    for i in range(ns):
        w += 0.5*dt*(ux - (u**3 - u))
        u += dt*w
        ux = uxx(u)
        w += 0.5*dt*(ux - (u**3 - u))
        
        if i % 4 == 0:
            t_arr.append(i*dt)
            u_center_arr.append(u[N//2])
        
        if not np.isfinite(u).all() or np.max(np.abs(u))>10:
            break
    
    return np.array(t_arr), np.array(u_center_arr)

# Check whether kinks pass through each other and escape
# At v=0.3 and v=0.5, kinks survive. Let's run much longer to see if they escape the box
# and whether they come back (periodic BC)
fig, axes = plt.subplots(8, 1, figsize=(16, 32))
for idx, v in enumerate([0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50]):
    t, uc = run(v, t_max=1200)
    axes[idx].plot(t, uc, 'b-', alpha=0.8)
    axes[idx].set_title(f'v={v}')
    axes[idx].set_ylabel('phi(200)')
    axes[idx].set_ylim(-3, 3)
    axes[idx].axhline(y=1, color='gray', linestyle='--', alpha=0.3)
    axes[idx].axhline(y=-1, color='gray', linestyle='--', alpha=0.3)
axes[-1].set_xlabel('time')
plt.tight_layout()
plt.savefig('phi4_long_track.png', dpi=150)
plt.close()
print('Saved phi4_long_track.png')

# Print summary: does u_center oscillate around +1 (bion) or settle to -1 (annihilation)?
for v in [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50]:
    t, uc = run(v, t_max=1200)
    # Late-time average
    late = uc[len(uc)//2:]
    avg = np.mean(late)
    osc = np.max(late) - np.min(late)
    print(f'v={v:.2f}: late_avg={avg:.3f}, osc_amplitude={osc:.3f}, final={uc[-1]:.3f}')