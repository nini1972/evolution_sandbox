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

# Fine scan: 200 points from 0.18 to 0.32
vs = np.linspace(0.18, 0.32, 60)
results = []
for v in vs:
    t, uc = run(v, t_max=400, dt=0.3)
    late = uc[len(uc)//2:]
    avg = np.mean(late)
    osc = np.max(late) - np.min(late)
    if osc > 0.5:
        outcome = 'bion'
    else:
        outcome = 'escape'
    results.append((v, outcome, avg, osc))

# Print window boundaries
print('=== Resonance window structure ===')
prev_outcome = None
for i, (v, outcome, avg, osc) in enumerate(results):
    if outcome != prev_outcome:
        print(f'  v={v:.4f}: -> {outcome}')
        prev_outcome = outcome

# Plot bifurcation diagram
fig, axes = plt.subplots(3, 1, figsize=(16, 14))
vs_arr = [r[0] for r in results]
osc_arr = [r[3] for r in results]
avg_arr = [r[2] for r in results]
oc = [1 if r[1]=='escape' else 0 for r in results]

colors = ['green' if o else 'red' for o in oc]
axes[0].scatter(vs_arr, oc, c=colors, s=15)
axes[0].set_xlabel('v')
axes[0].set_ylabel('escape=1, bion=0')
axes[0].set_title('Phi-4 Kink-Antikink Resonance Windows')
axes[0].set_ylim(-0.1, 1.1)

axes[1].plot(vs_arr, osc_arr, 'b-', linewidth=0.5)
axes[1].set_xlabel('v')
axes[1].set_ylabel('oscillation amplitude')
axes[1].set_title('Late-time oscillation amplitude at collision center')

axes[2].plot(vs_arr, avg_arr, 'r-', linewidth=0.5)
axes[2].set_xlabel('v')
axes[2].set_ylabel('late-time average')
axes[2].set_title('Late-time average of field at center')
axes[2].axhline(y=1, color='gray', linestyle='--', alpha=0.3)
axes[2].axhline(y=-1, color='gray', linestyle='--', alpha=0.3)

plt.tight_layout()
plt.savefig('phi4_resonance_windows.png', dpi=150)
plt.close()
print('Saved phi4_resonance_windows.png')