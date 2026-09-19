"""
Detailed trajectory analysis of phi4 kink-antikink collisions
Focus on kink separation vs time for different outcomes
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

L = 200.0; N = 512; dx = L/N
x = np.linspace(0, L, N, endpoint=False)
k = np.fft.fftfreq(N, d=dx) * 2*np.pi
k2fac = -k**2

def uxx(u):
    return np.fft.ifft(k2fac * np.fft.fft(u)).real

def run_phi4_track(v, dt=0.04, x1=60.0, x2=140.0, t_post=400.0):
    s2 = np.sqrt(2.0); g = 1.0/np.sqrt(1-v**2)
    sep0 = x2 - x1
    u = np.tanh(g*(x-x1)/s2) - np.tanh(g*(x-x2)/s2) - 1.0
    s1c = 1.0/np.cosh(g*(x-x1)/s2)
    s2c = 1.0/np.cosh(g*(x-x2)/s2)
    w = -g*v/s2*s1c**2 - g*v/s2*s2c**2

    t_col = sep0 / (2*v)
    t_max = t_col + t_post
    ns = int(t_max/dt)
    
    track = {'t': [], 'xk1': [], 'xk2': [], 'sep': [], 'max_field': [], 'E': []}
    ux = uxx(u)

    for i in range(ns):
        w += 0.5*dt*(ux - (u**3 - u))
        u += dt*w
        ux = uxx(u)
        w += 0.5*dt*(ux - (u**3 - u))

        t = i * dt
        if i % 4 == 0:  # every 0.16 time units
            # Find kink positions by looking at |du/dx| peaks
            dux = np.abs(np.gradient(u, dx))
            peaks = []
            for j in range(2, len(dux)-2):
                if dux[j] > 0.15 and dux[j] >= dux[j-1] and dux[j] >= dux[j+1]:
                    if not peaks or (j - peaks[-1]) > 20:
                        peaks.append(j)
                    elif dux[j] > dux[peaks[-1]]:
                        peaks[-1] = j
            
            if len(peaks) >= 2:
                pos = sorted([x[peaks[0]], x[peaks[1]]])
                sep = pos[1] - pos[0]
            else:
                pos = [0, 0]
                sep = 0
            
            track['t'].append(t)
            track['xk1'].append(pos[0])
            track['xk2'].append(pos[1])
            track['sep'].append(sep)
            track['max_field'].append(np.max(np.abs(u)))
    
    return track

# Select representative velocities
velocities = {
    'BION (v=0.15)': 0.15,           # Deep bion
    'BION (v=0.18)': 0.18,           # Near-edge bion  
    '2-bounce ESC (v=0.195)': 0.195,  # First escape window
    'BION window (v=0.21)': 0.21,    # Resonance window
    '3-bounce ESC (v=0.24)': 0.24,   # Between windows
    'BION window (v=0.25)': 0.25,    # Last resonance window
    'ESC (v=0.28)': 0.28,            # Above critical
    'ESC (v=0.40)': 0.40,            # High energy escape
}

fig, axes = plt.subplots(4, 2, figsize=(18, 20))
axes = axes.flatten()

for idx, (label, v) in enumerate(velocities.items()):
    ax = axes[idx]
    track = run_phi4_track(v, t_post=400)
    ts = np.array(track['t'])
    seps = np.array(track['sep'])
    
    ax.plot(ts, seps, 'b-', linewidth=0.8)
    ax.set_title(label, fontsize=12, fontweight='bold')
    ax.set_xlabel('Time t')
    ax.set_ylabel('Kink separation')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-5, 200)
    
    # Mark collision time
    t_col = 80 / (2*v)
    ax.axvline(x=t_col, color='red', linestyle='--', alpha=0.5, label=f'Collision t={t_col:.0f}')
    ax.legend(fontsize=8)

plt.suptitle(r'$\phi^4$ Kink-Antikink: Separation vs Time for Different Outcomes', 
             fontsize=16, fontweight='bold', y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('phi4_trajectories_detail.png', dpi=150)
plt.close()

print("Saved phi4_trajectories_detail.png")

# Also create a space-time density plot for 3 key cases
fig2, axes2 = plt.subplots(3, 1, figsize=(18, 12))

key_vels = [0.15, 0.21, 0.28]
labels = ['BION (v=0.15)', 'Resonance window BION (v=0.21)', 'ESC above v_c (v=0.28)']

for idx, (v, label) in enumerate(zip(key_vels, labels)):
    s2 = np.sqrt(2.0); g = 1.0/np.sqrt(1-v**2)
    x1, x2 = 60.0, 140.0
    u = np.tanh(g*(x-x1)/s2) - np.tanh(g*(x-x2)/s2) - 1.0
    s1c = 1.0/np.cosh(g*(x-x1)/s2)
    s2c = 1.0/np.cosh(g*(x-x2)/s2)
    w = -g*v/s2*s1c**2 - g*v/s2*s2c**2
    
    dt = 0.04
    t_max = 80/(2*v) + 300
    ns = int(t_max/dt)
    ux = uxx(u)
    
    field_history = []
    save_every = 2
    for i in range(ns):
        w += 0.5*dt*(ux - (u**3 - u))
        u += dt*w
        ux = uxx(u)
        w += 0.5*dt*(ux - (u**3 - u))
        if i % save_every == 0:
            field_history.append(u.copy())
    
    field_arr = np.array(field_history)
    times = np.arange(0, ns, save_every) * dt
    
    ax = axes2[idx]
    im = ax.pcolormesh(times, x, field_arr.T, cmap='RdBu_r', vmin=-1.5, vmax=1.5, shading='auto')
    ax.set_title(label, fontsize=12, fontweight='bold')
    ax.set_ylabel('Position x')
    ax.set_ylim(30, 170)
    if idx == 2:
        ax.set_xlabel('Time t')
    plt.colorbar(im, ax=ax, label='Field φ')

plt.suptitle(r'$\phi^4$ Kink-Antikink: Space-Time Field Evolution', fontsize=16, fontweight='bold', y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('phi4_spacetime.png', dpi=150)
plt.close()

print("Saved phi4_spacetime.png")
print("Done!")