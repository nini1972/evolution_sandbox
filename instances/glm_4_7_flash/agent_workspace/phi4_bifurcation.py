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

def run(v, t_max=1200, dt=0.25):
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
    energy_arr = []
    
    for i in range(ns):
        w += 0.5*dt*(ux - (u**3 - u))
        u += dt*w
        ux = uxx(u)
        w += 0.5*dt*(ux - (u**3 - u))
        
        if i % 4 == 0:
            t_arr.append(i*dt)
            u_center_arr.append(u[N//2])
            # Total energy
            dev = 0.25*(u**2-1)**2
            kin = 0.5 * w**2
            energy_arr.append(np.sum(dev + kin)*dx)
        
        if not np.isfinite(u).all() or np.max(np.abs(u))>10:
            break
    
    return np.array(t_arr), np.array(u_center_arr), np.array(energy_arr)

# Fine scan around the transition
vs = np.linspace(0.18, 0.35, 30)
print('Fine scan around transition:')
results = []
for v in vs:
    t, uc, E = run(v, t_max=1200)
    late = uc[len(uc)//2:]
    avg = np.mean(late)
    osc = np.max(late) - np.min(late)
    # Bion: oscillating (osc > 0.5 and avg < 0.5)
    # Escape: settled near +1 (osc < 0.2 and avg > 0.9)
    if osc > 0.5:
        outcome = 'bion'
    else:
        outcome = 'escape'
    results.append((v, outcome, avg, osc))
    print(f'v={v:.4f}: {outcome}, avg={avg:.3f}, osc={osc:.3f}')

# Plot
fig, axes = plt.subplots(2, 1, figsize=(14, 10))
vs_arr = [r[0] for r in results]
osc_arr = [r[3] for r in results]
avg_arr = [r[2] for r in results]
oc = [1 if r[1]=='escape' else 0 for r in results]

axes[0].scatter(vs_arr, oc, c=['green' if o else 'red' for o in oc], s=60)
axes[0].set_xlabel('v')
axes[0].set_ylabel('escape=1, bion=0')
axes[0].set_title('Phi4 Kink-Antikink Collision: Bifurcation Diagram')
axes[0].set_ylim(-0.1, 1.1)

axes[1].plot(vs_arr, osc_arr, 'b-o', markersize=5, label='oscillation amplitude')
axes[1].plot(vs_arr, avg_arr, 'r-s', markersize=5, label='late-time average')
axes[1].set_xlabel('v')
axes[1].set_ylabel('value')
axes[1].legend()
axes[1].set_title('Bifurcation metrics')

plt.tight_layout()
plt.savefig('phi4_bifurcation.png', dpi=150)
plt.close()
print('Saved phi4_bifurcation.png')