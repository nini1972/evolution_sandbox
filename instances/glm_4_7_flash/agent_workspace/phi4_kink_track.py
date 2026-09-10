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
    # Track kink positions by finding zero crossings
    # Kink: phi goes from -1 to +1 (crosses 0 going up)
    # Antikink: phi goes from +1 to -1 (crosses 0 going down)
    kink_pos = []
    antikink_pos = []
    u_center_arr = []
    
    for i in range(ns):
        w += 0.5*dt*(ux - (u**3 - u))
        u += dt*w
        ux = uxx(u)
        w += 0.5*dt*(ux - (u**3 - u))
        
        if i % 4 == 0:
            t_arr.append(i*dt)
            u_center_arr.append(u[N//2])
            # Find zero crossings
            crossings = []
            for j in range(N-1):
                if u[j] * u[j+1] < 0:  # sign change
                    # Linear interpolation
                    xc = x[j] + dx * (-u[j]) / (u[j+1] - u[j])
                    crossings.append((xc, u[j+1] - u[j]))  # position, slope sign
            
            kp = []
            akp = []
            for xc, slope in crossings:
                if slope > 0:  # crossing upward = kink
                    kp.append(xc)
                else:  # crossing downward = antikink
                    akp.append(xc)
            
            kink_pos.append(kp)
            antikink_pos.append(akp)
        
        if not np.isfinite(u).all() or np.max(np.abs(u))>10:
            break
    
    return np.array(t_arr), kink_pos, antikink_pos, np.array(u_center_arr)

# Run for a few velocities and plot
fig, axes = plt.subplots(6, 1, figsize=(16, 24))
for idx, v in enumerate([0.1, 0.2, 0.25, 0.3, 0.4, 0.5]):
    t, kp, akp, uc = run(v, t_max=800)
    # Plot kink positions
    for ti in range(len(t)):
        for kk in kp[ti]:
            axes[idx].plot(t[ti], kk, 'b.', markersize=1)
        for aa in akp[ti]:
            axes[idx].plot(t[ti], aa, 'r.', markersize=1)
    axes[idx].plot(t, uc, 'g-', alpha=0.3, label='u(center)')
    axes[idx].set_title(f'v={v} (blue=kink, red=antikink, green=u_center)')
    axes[idx].set_ylabel('position')
    axes[idx].set_ylim(0, 400)
    axes[idx].legend()

axes[-1].set_xlabel('time')
plt.tight_layout()
plt.savefig('phi4_kink_track.png', dpi=150)
plt.close()
print('Saved phi4_kink_track.png')

# Print summary
for v in [0.1, 0.2, 0.3, 0.4, 0.5]:
    t, kp, akp, uc = run(v, t_max=800)
    # Check last 1/4 of simulation
    n = len(t)
    late_kinks = []
    late_antis = []
    for ti in range(3*n//4, n):
        late_kinks.extend(kp[ti])
        late_antis.extend(akp[ti])
    
    n_kink = len(late_kinks)
    n_anti = len(late_antis)
    late_uc = uc[3*n//4:]
    
    print(f'v={v}: late kinks={n_kink}, late antis={n_anti}, u_center_range=[{np.min(late_uc):.2f}, {np.max(late_uc):.2f}]')