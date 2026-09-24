"""
Kuramoto-Sivashinsky equation using ETDRK4 (Kassam & Trefethen 2005).
u_t = -u_xx - u_xxxx - (u * u_x)
Linear part: L = k^2 - k^4 (in Fourier space)
Nonlinear part: N(u) = -0.5 * i*k * FFT(u^2)
ETDRK4 exactly integrates the stiff linear part.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import json

L = 128.0
N = 1024
dt = 0.25
T_total = 2000.0

def setup(L, N, dt):
    dx = L / N
    x = np.arange(N) * dx
    k = 2.0 * np.pi * np.fft.fftfreq(N, d=dx)
    L_hat = k**2 - k**4
    
    # ETD coefficients (Kassam-Trefethen)
    E = np.exp(L_hat * dt)
    E2 = np.exp(L_hat * dt / 2.0)
    
    # phi_n(z) = (exp(z) - sum_{j=0}^{n-1} z^j/j!) / z^n
    # phi_1(z) = (exp(z) - 1) / z
    # phi_2(z) = (exp(z) - 1 - z) / z^2
    # phi_3(z) = (exp(z) - 1 - z - z^2/2) / z^3
    
    # Handle z=0: phi_1(0)=1, phi_2(0)=1/2, phi_3(0)=1/6
    z = L_hat * dt
    phi1 = np.where(np.abs(z) < 1e-10, 1.0, (np.exp(z) - 1) / z)
    phi2 = np.where(np.abs(z) < 1e-10, 0.5, (np.exp(z) - 1 - z) / z**2)
    phi3 = np.where(np.abs(z) < 1e-10, 1.0/6.0, (np.exp(z) - 1 - z - z**2/2) / z**3)
    
    a = E2 * phi1
    b = E2 * phi2
    c = phi3
    
    return x, k, L_hat, E, E2, a, b, c

def ks_solver(L, N, dt, T_total, seed=42):
    np.random.seed(seed)
    x, k, L_hat, E, E2, a_coef, b_coef, c_coef = setup(L, N, dt)
    
    u = 0.1 * (np.random.rand(N) - 0.5)
    u_hat = np.fft.fft(u)
    
    def Nl(uh):
        ur = np.fft.ifft(uh).real
        return -0.5 * 1j * k * np.fft.fft(ur**2)
    
    n_steps = int(T_total / dt)
    n_save = max(1, n_steps // 400)
    
    u_frames = []
    t_frames = []
    energy_frames = []
    
    for step in range(n_steps):
        N_u = Nl(u_hat)
        N_a = Nl(a_coef * u_hat + b_coef * dt * N_u)
        N_b = Nl(a_coef * u_hat + b_coef * dt * N_a)
        N_c = Nl(E2 * u_hat + a_coef * dt * (2*N_b - N_u))
        
        u_hat = E * u_hat + dt * (
            N_u * phi1_2(L_hat, dt) +
            2 * (N_a + N_b) * phi2_2(L_hat, dt) +
            N_c * phi3_2(L_hat, dt)
        )
        u_hat[0] = 0.0  # zero mean
        
        if step % n_save == 0:
            u_real = np.fft.ifft(u_hat).real
            u_frames.append(u_real.copy())
            t_frames.append(step * dt)
            energy_frames.append(np.sum(u_real**2) * (L/N))
    
    return x, np.array(u_frames), np.array(t_frames), np.array(energy_frames)

def phi1_2(L_hat, dt):
    z = L_hat * dt
    return np.where(np.abs(z) < 1e-10, 1.0, (np.exp(z) - 1) / z)

def phi2_2(L_hat, dt):
    z = L_hat * dt
    return np.where(np.abs(z) < 1e-10, 0.5, (np.exp(z) - 1 - z) / z**2)

def phi3_2(L_hat, dt):
    z = L_hat * dt
    return np.where(np.abs(z) < 1e-10, 1.0/6.0, (np.exp(z) - 1 - z - z**2/2) / z**3)

print(f"KS: L={L}, N={N}, dt={dt}, T={T_total}")
print("Simulating...")
x, u_frames, t_frames, energy_frames = ks_solver(L, N, dt, T_total)
print(f"Done. {len(u_frames)} frames. Max|u|={np.max(np.abs(u_frames)):.4f}")
print(f"Energy range: [{np.min(energy_frames):.4f}, {np.max(energy_frames):.4f}]")
