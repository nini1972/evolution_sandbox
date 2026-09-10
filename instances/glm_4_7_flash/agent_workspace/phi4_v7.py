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

def run(v, t_max=None, dt=0.25, record_every=8):
    if t_max is None:
        t_max = max(300.0, 80.0/v)
    s2 = np.sqrt(2.0); g = 1.0/np.sqrt(1-v**2)
    x1, x2 = 150.0, 250.0
    # Kink at x1 (moving right), Antikink at x2 (moving left)
    u = np.tanh(g*(x-x1)/s2) - np.tanh(g*(x-x2)/s2) - 1.0
    sech1 = 1.0/np.cosh(g*(x-x1)/s2)
    sech2 = 1.0/np.cosh(g*(x-x2)/s2)
    # Kink at x1 moving right: du/dt = -v/sqrt(2) * sech^2 (x1 increases)
    # Antikink at x2 moving left: du/dt = +v/sqrt(2) * sech^2 (x2 decreases)
    w = -g*v/s2 * sech1**2 + g*v/s2 * sech2**2
    ns = int(t_max/dt)
    ux = uxx(u)
    
    center_pos = []
    t_record = []
    for i in range(ns):
        w += 0.5*dt*(ux - (u**3 - u))
        u += dt*w
        ux = uxx(u)
        w += 0.5*dt*(ux - (u**3 - u))
        if i % record_every == 0:
            dev = 0.25*(u**2-1)**2
            tot = np.sum(dev)*dx
            c = np.sum(x*dev)*dx/tot if tot > 1e-10 else 200.0
            center_pos.append(c)
            t_record.append(i*dt)
        if not np.isfinite(u).all() or np.max(np.abs(u))>10:
            return 'diverged', center_pos, t_record
    
    # Better detection: measure energy spread (second moment)
    dev = 0.25*(u**2-1)**2
    # Also look at kinetic energy
    kin = 0.5 * w**2
    total_energy = dev + kin
    center = np.sum(x * total_energy) * dx / (np.sum(total_energy)*dx)
    spread = np.sqrt(np.sum((x-center)**2 * total_energy) * dx / (np.sum(total_energy)*dx))
    
    # If spread is large, kinks have escaped. If small, bion.
    if spread > 80:
        outcome = 'escape'
    else:
        outcome = 'bion'
    
    return outcome, center_pos, t_record

# Test
print('=== Test with corrected velocities ===')
for v in [0.10, 0.15, 0.18, 0.20, 0.22, 0.25, 0.28, 0.30, 0.35]:
    out, cp, tr = run(v)
    t = np.array(tr)
    cp_arr = np.array(cp)
    # Report trajectory behavior
    if len(cp) > 10:
        # Check if center oscillates (bion) or moves (escape)
        late_cp = cp_arr[len(cp)//2:]
        amplitude = np.max(late_cp) - np.min(late_cp)
        print(f'v={v:.3f}: {out}, center_range_late={amplitude:.1f}, final_center={cp[-1]:.1f}')
    else:
        print(f'v={v:.3f}: {out}, len={len(cp)}')