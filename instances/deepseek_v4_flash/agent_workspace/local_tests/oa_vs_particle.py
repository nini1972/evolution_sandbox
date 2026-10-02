"""Cross-check: OA reduced ODE vs particle integrators (Euler small/large dt, RK4).
Question: is the a=1, K0=3 locking at R~0.55 real physics or integrator artifact?
"""
import numpy as np

def oa_reduced(K0, a, gamma=1.0, T=300.0, dt=0.001, r0=0.03):
    """Integrate OA: rdot = -gamma r + (K0/2) r^{a+1} (1-r^2)"""
    r = r0; steps = int(T/dt); rs = np.empty(steps)
    for i in range(steps):
        r += dt * (-gamma * r + (K0/2) * r**(a+1) * (1-r*r))
        rs[i] = r
    return rs[-1]

def particle(N, K0, a, T=300.0, dt=0.02, method='euler', seed=3, gamma=1.0):
    rng = np.random.default_rng(seed)
    u = rng.random(N); om = gamma*np.tan(np.pi*(u-0.5))
    th = rng.uniform(0, 2*np.pi, N)
    steps = int(T/dt)
    for i in range(steps):
        z = np.exp(1j*th).mean(); R = abs(z); psi = np.angle(z)
        K = K0*(R**a)
        if method == 'euler':
            th = (th + om*dt + K*np.sin(psi-th)*dt) % (2*np.pi)
        elif method == 'rk4':
            # relative phase to psi: phi = theta - psi; psi rotates slowly
            phi = th - psi
            k1 = om + K*np.sin(-phi)          # d phi/dt ~ om + K sin(0 - phi)
            k2 = om + K*np.sin(-(phi+0.5*dt*k1))
            k3 = om + K*np.sin(-(phi+0.5*dt*k2))
            k4 = om + K*np.sin(-(phi+dt*k3))
            phi = (phi + dt/6*(k1+2*k2+2*k3+k4)) % (2*np.pi)
            th = (psi + phi) % (2*np.pi)
    # avg last 20
    Rs = []
    for _ in range(20):
        z = np.exp(1j*th).mean(); R = abs(z); psi = np.angle(z)
        K = K0*(R**a)
        if method == 'euler':
            th = (th + om*dt + K*np.sin(psi-th)*dt) % (2*np.pi)
        else:
            phi = th - psi
            k1 = om + K*np.sin(-phi)
            k2 = om + K*np.sin(-(phi+0.5*dt*k1))
            k3 = om + K*np.sin(-(phi+0.5*dt*k2))
            k4 = om + K*np.sin(-(phi+dt*k3))
            phi = (phi + dt/6*(k1+2*k2+2*k3+k4)) % (2*np.pi)
            th = (psi + phi) % (2*np.pi)
        Rs.append(R)
    return float(np.mean(Rs))

print('=== OA reduced ODE (ground truth for N->inf) ===')
for a, K0 in [(0,3.0),(1,3.0),(1,7.0),(2,20.0)]:
    print(f'a={a} K0={K0}: r_end={oa_reduced(K0,a):.5f}', flush=True)

print()
print('=== particle cross-check a=1 K0=3, N=2000 ===')
for method, dt in [('euler',0.02),('euler',0.002),('rk4',0.02)]:
    R = particle(2000, 3.0, 1, T=200.0, dt=dt, method=method, seed=5)
    print(f'method={method:5s} dt={dt:.3f}: R={R:.4f}', flush=True)

print()
print('=== particle cross-check a=0 K0=3 (classic, theory 0.577) ===')
for method, dt in [('euler',0.02),('rk4',0.02)]:
    R = particle(2000, 3.0, 0, T=400.0, dt=dt, method=method, seed=5)
    print(f'method={method:5s} dt={dt:.3f}: R={R:.4f}', flush=True)

print()
print('=== particle cross-check a=2 K0=20 ===')
for method, dt in [('euler',0.02),('rk4',0.02)]:
    R = particle(2000, 20.0, 2, T=200.0, dt=dt, method=method, seed=5)
    print(f'method={method:5s} dt={dt:.3f}: R={R:.4f}', flush=True)