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

def run_full(v, t_max=None, dt=0.25):
    if t_max is None:
        t_max = max(300.0, 80.0/v)  # ensure kinks have time to collide and separate
    s2 = np.sqrt(2.0); g = 1.0/np.sqrt(1-v**2)
    x1, x2 = 150.0, 250.0
    u = np.tanh(g*(x-x1)/s2) - np.tanh(g*(x-x2)/s2) - 1.0
    sech1 = 1.0/np.cosh(g*(x-x1)/s2)
    sech2 = 1.0/np.cosh(g*(x-x2)/s2)
    w = -g*v/s2 * sech1**2 - g*v/s2 * sech2**2
    ns = int(t_max/dt)
    ux = uxx(u)
    
    center_pos = []
    t_record = []
    for i in range(ns):
        w += 0.5*dt*(ux - (u**3 - u))
        u += dt*w
        ux = uxx(u)
        w += 0.5*dt*(ux - (u**3 - u))
        if i % 8 == 0:
            dev = 0.25*(u**2-1)**2
            tot = np.sum(dev)*dx
            c = np.sum(x*dev)*dx/tot if tot > 1e-10 else 200.0
            center_pos.append(c)
            t_record.append(i*dt)
        if not np.isfinite(u).all() or np.max(np.abs(u))>10:
            return 'diverged', center_pos, t_record
    
    dev_final = 0.25*(u**2-1)**2
    peaks = []
    for j in range(2, N-2):
        if dev_final[j] > 0.002 and dev_final[j] >= dev_final[j-1] and dev_final[j] >= dev_final[j+1]:
            peaks.append(x[j])
    
    if len(peaks) >= 2 and abs(peaks[-1] - peaks[0]) > 30:
        outcome = 'escape'
    else:
        outcome = 'bion'
    
    return outcome, center_pos, t_record

# Test with longer times
print('=== Test ===')
for v in [0.10, 0.15, 0.18, 0.20, 0.22, 0.25, 0.30, 0.35]:
    out, cp, tr = run_full(v)
    print(f'v={v:.3f}: {out}, len(cp)={len(cp)}')
