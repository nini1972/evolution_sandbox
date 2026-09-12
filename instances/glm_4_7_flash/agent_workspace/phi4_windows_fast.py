import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Smaller domain, shorter time, for speed
L = 200.0; N = 256; dx = L/N
x = np.linspace(0, L, N, endpoint=False)
k = np.fft.fftfreq(N, d=dx) * 2*np.pi
k2fac = -k**2

def uxx(u):
    return np.fft.ifft(k2fac * np.fft.fft(u)).real

def run(v, t_max=300, dt=0.4):
    s2 = np.sqrt(2.0); g = 1.0/np.sqrt(1-v**2)
    x1, x2 = 80.0, 120.0
    u = np.tanh(g*(x-x1)/s2) - np.tanh(g*(x-x2)/s2) - 1.0
    sech1 = 1.0/np.cosh(g*(x-x1)/s2)
    sech2 = 1.0/np.cosh(g*(x-x2)/s2)
    w = -g*v/s2 * sech1**2 - g*v/s2 * sech2**2
    ns = int(t_max/dt)
    ux = uxx(u)
    
    uc_list = []
    
    for i in range(ns):
        w += 0.5*dt*(ux - (u**3 - u))
        u += dt*w
        ux = uxx(u)
        w += 0.5*dt*(ux - (u**3 - u))
        
        if i % 2 == 0:
            uc_list.append(u[N//2])
        
        if not np.isfinite(u).all() or np.max(np.abs(u))>10:
            break
    
    uc = np.array(uc_list)
    late = uc[len(uc)//2:]
    if len(late) == 0:
        return 'bion', 0, 0
    avg = np.mean(late)
    osc = np.max(late) - np.min(late)
    if osc > 0.5:
        return 'bion', avg, osc
    else:
        return 'escape', avg, osc

# Fine scan: 300 points from 0.18 to 0.32
npts = 300
vs = np.linspace(0.18, 0.32, npts)
results = []
for v in vs:
    outcome, avg, osc = run(v)
    results.append((v, outcome, avg, osc))

# Print window boundaries
print('=== Resonance window structure ===')
prev = None
for v, outcome, avg, osc in results:
    if outcome != prev:
        print(f'  v={v:.5f}: -> {outcome}')
        prev = outcome

# Plot
fig, axes = plt.subplots(2, 1, figsize=(16, 10))
vs_arr = np.array([r[0] for r in results])
oc = np.array([1 if r[1]=='escape' else 0 for r in results])
osc_arr = np.array([r[3] for r in results])
avg_arr = np.array([r[2] for r in results])

axes[0].scatter(vs_arr, oc, c=['green' if o else 'red' for o in oc], s=8)
axes[0].set_xlabel('v (initial velocity)')
axes[0].set_ylabel('escape=1, bion=0')
axes[0].set_title(r'$\phi^4$ Kink-Antikink Resonance Windows')
axes[0].set_ylim(-0.1, 1.1)

axes[1].plot(vs_arr, osc_arr, 'b-', linewidth=0.5)
axes[1].set_xlabel('v')
axes[1].set_ylabel('oscillation amplitude')
axes[1].set_title('Late-time oscillation amplitude at collision center')

plt.tight_layout()
plt.savefig('phi4_resonance_windows.png', dpi=150)
plt.close()
print('Saved phi4_resonance_windows.png')
