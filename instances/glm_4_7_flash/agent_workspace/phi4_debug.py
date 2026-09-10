import numpy as np

L = 400.0; N = 512; dx = L/N
x = np.linspace(0, L, N, endpoint=False)
k = np.fft.fftfreq(N, d=dx) * 2*np.pi
k2fac = -k**2

def uxx(u):
    return np.fft.ifft(k2fac * np.fft.fft(u)).real

def run_debug(v, t_max=None, dt=0.25):
    if t_max is None:
        t_max = max(300.0, 80.0/v)
    s2 = np.sqrt(2.0); g = 1.0/np.sqrt(1-v**2)
    x1, x2 = 150.0, 250.0
    u = np.tanh(g*(x-x1)/s2) - np.tanh(g*(x-x2)/s2) - 1.0
    sech1 = 1.0/np.cosh(g*(x-x1)/s2)
    sech2 = 1.0/np.cosh(g*(x-x2)/s2)
    w = -g*v/s2 * sech1**2 - g*v/s2 * sech2**2
    ns = int(t_max/dt)
    ux = uxx(u)
    
    for i in range(ns):
        w += 0.5*dt*(ux - (u**3 - u))
        u += dt*w
        ux = uxx(u)
        w += 0.5*dt*(ux - (u**3 - u))
        
        if i % 40 == 0:
            dev = 0.25*(u**2-1)**2
            # Find peaks in dev
            peaks = []
            for j in range(2, N-2):
                if dev[j] > 0.002 and dev[j] >= dev[j-1] and dev[j] >= dev[j+1]:
                    peaks.append((x[j], dev[j]))
            # Field value at center (x=200)
            u_center = u[N//2]
            print(f't={i*dt:6.1f}  u(200)={u_center:+.4f}  npeaks={len(peaks)}  peaks={[(f"{p[0]:.0f}", f"{p[1]:.4f}") for p in peaks[:4]]}')
        
        if not np.isfinite(u).all() or np.max(np.abs(u))>10:
            print('DIVERGED')
            break

print('=== v=0.18 ===')
run_debug(0.18)
print()
print('=== v=0.25 ===')
run_debug(0.25)
