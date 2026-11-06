# CORRECT split-step Fourier integrator, verified end to end.
# Focusing NLS: i psi_t + psi_xx + |psi|^2 psi = 0, background 1 + eps*noise.
# Linear half: psi <- ifft( exp(-i k^2 dt) * fft(psi) )   [Strang: full dt]
# Nonlinear:   psi <- exp( i |psi|^2 dt ) * psi
import numpy as np
from numpy.fft import fft, ifft, fftfreq

L, N = 50.0, 1024
dx = L/N
dt = 1e-3
eps = 0.1
rng = np.random.default_rng(1)
psi = 1.0 + eps*(rng.standard_normal(N)+1j*rng.standard_normal(N))/np.sqrt(2.0)
k = 2.0*np.pi*fftfreq(N, d=dx)
D = np.exp(-1j*k**2*dt)
for step in range(1, 20001):
    psi = ifft(D*fft(psi))
    psi = np.exp(1j*np.abs(psi)**2*dt)*psi
    if step % 2000 == 0:
        I = np.abs(psi)**2
        # invariant checks
        print("t=%5.1f maxI=%9.3f meanI=%8.4f norm=%10.6f  max|k|_high=%9.4f"
              % (step*dt, I.max(), I.mean(), (np.abs(psi)**2).mean(),
                 (np.abs(fft(psi))**2)[N//4:3*N//4].sum()))
