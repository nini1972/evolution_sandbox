import numpy as np, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

L, N, dt, T_total = 128.0, 1024, 0.25, 2000.0

def ks_solver(L, N, dt, T_total, seed=42):
    np.random.seed(seed)
    dx = L / N
    x = np.arange(N) * dx
    k = 2.0 * np.pi * np.fft.fftfreq(N, d=dx)
    Lhat = k**2 - k**4
    E = np.exp(Lhat * dt)
    # dealias mask
    nd = N // 3
    dea = np.zeros(N); dea[:nd] = 1.0; dea[-nd:] = 1.0
    
    def nl_rhs(u):
        ux = np.fft.ifft(1j * k * np.fft.fft(u) * dea).real
        return -u * ux
    
    def nl_step(u, h):
        k1 = nl_rhs(u)
        k2 = nl_rhs(u + 0.5*h*k1)
        k3 = nl_rhs(u + 0.5*h*k2)
        k4 = nl_rhs(u + h*k3)
        return u + h/6.0*(k1 + 2*k2 + 2*k3 + k4)
    
    u = 0.1 * (np.random.rand(N) - 0.5)
    uh = np.fft.fft(u) * dea
    uh[0] = 0
    
    ns = int(T_total / dt)
    nsave = max(1, ns // 400)
    uf, tf, ef = [], [], []
    
    for s in range(ns):
        # Strang splitting: NL(dt/2) -> Lin(dt) -> NL(dt/2)
        ur = np.fft.ifft(uh).real
        ur = nl_step(ur, dt/2.0)
        uh = np.fft.fft(ur) * dea
        uh = E * uh
        uh[0] = 0
        ur = np.fft.ifft(uh).real
        ur = nl_step(ur, dt/2.0)
        uh = np.fft.fft(ur) * dea
        uh[0] = 0
        
        if s % nsave == 0:
            uf.append(ur.copy())
            tf.append(s * dt)
            ef.append(np.sum(ur**2) * dx)
    
    return x, k, np.array(uf), np.array(tf), np.array(ef)

print(f"KS: L={L}, N={N}, dt={dt}, T={T_total}")
print("Simulating...")
x, k, uf, tf, ef = ks_solver(L, N, dt, T_total)
print(f"Done. {len(uf)} frames. Max|u|={np.max(np.abs(uf)):.4f}")
print(f"Energy range: [{np.min(ef):.4f}, {np.max(ef):.4f}]")
