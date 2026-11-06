# Sign diagnostic: which dispersion sign gives MI growth (filaments)?
# Focusing NLS: i psi_t + psi_xx + |psi|^2 psi = 0
#   -> linear: exp(-i k^2 dt), nonlinear: exp(+i |psi|^2 dt)
# Defocusing:   i psi_t + psi_xx - |psi|^2 psi = 0
#   -> linear: exp(-i k^2 dt), nonlinear: exp(-i |psi|^2 dt)
import numpy as np
from numpy.fft import fftfreq

L, N = 50.0, 1024
dx = L/N
dt = 1e-3
eps = 0.1
rng = np.random.default_rng(1)
psi0 = 1.0 + eps*(rng.standard_normal(N)+1j*rng.standard_normal(N))/np.sqrt(2.0)
k = 2.0*np.pi*fftfreq(N, d=dx)

for tag, sgn in (("focusing(+nl)", +1.0), ("defocusing(-nl)", -1.0)):
    psi = psi0.copy()
    D = np.exp(-1j*k**2*dt)
    for step in range(1, 5001):
        psi = D*(np.exp(sgn*1j*np.abs(psi)**2*dt)*psi)
        if step % 500 == 0:
            print("%s step %d t=%.1f maxI=%.4f meanI=%.4f" %
                  (tag, step, step*dt, (np.abs(psi)**2).max(), (np.abs(psi)**2).mean()))
    print()
