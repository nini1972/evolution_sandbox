"""
Phi^4 - Numerical diagnostics: print field values at specific points
to verify the collision dynamics
"""
import numpy as np

L = 200.0; N = 512; dx = L/N
x = np.linspace(0, L, N, endpoint=False)
k = np.fft.fftfreq(N, d=dx) * 2*np.pi
k2fac = -k**2

def uxx(u):
    return np.fft.ifft(k2fac * np.fft.fft(u)).real

def run_phi4_diag(v, t_max=100.0, dt=0.02):
    s2 = np.sqrt(2.0); g = 1.0/np.sqrt(1-v**2)
    x1, x2 = 70.0, 130.0

    u = np.tanh(g*(x-x1)/s2) - np.tanh(g*(x-x2)/s2) - 1.0
    s1 = 1.0/np.cosh(g*(x-x1)/s2)
    s2v = 1.0/np.cosh(g*(x-x2)/s2)
    w = -g*v/s2*s1**2 - g*v/s2*s2v**2

    ns = int(t_max/dt)
    ux = uxx(u)

    print(f"\nv={v}, initial: u[100]={u[100]:.4f}, u[256]={u[256]:.4f}, u[400]={u[400]:.4f}")
    print(f"  max(u)={np.max(u):.4f}, min(u)={np.min(u):.4f}")
    
    center_idx = N//2  # x=100, the midpoint

    for i in range(ns):
        w += 0.5*dt*(ux - (u**3 - u))
        u += dt*w
        ux = uxx(u)
        w += 0.5*dt*(ux - (u**3 - u))

        t = i * dt
        if i % 250 == 0:  # every 5 time units
            print(f"  t={t:6.1f}: u[center]={u[center_idx]:+.4f}, max={np.max(u):+.4f}, "
                  f"energy={0.5*np.sum(w**2 + 0.5*ux**2 + 0.5*u**4 - 0.5*u**2)*dx:.4f}")

# Test several velocities
for v in [0.10, 0.20, 0.25, 0.30, 0.35, 0.40]:
    run_phi4_diag(v, t_max=80, dt=0.02)