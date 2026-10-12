"""Single-mode probe of kinetic_step + total_energy scaling."""
import numpy as np
import phi4_resonance_vectorized as P

# Pure mode: phi = cos(k0 x), pi = 0. Exact free-wave energy must be constant.
k0 = 2.0
phi = np.cos(k0*P.X)
pi  = np.zeros_like(P.X)
print("DX=%.4f N=%d  KX[1]=%.4f (should ~ %.4f)" % (P.DX, P.N, P.KX[1], 2*np.pi/P.L))

E0 = P.total_energy(phi, pi)
print("E0 = %.10f" % E0)
for i in range(1, 301):
    phi, pi = P.kinetic_step(phi, pi, 0.01)
    if i % 50 == 0:
        E = P.total_energy(phi, pi)
        print("step %3d t=%5.2f  E=%.10f  dE=%+.3e  |phi|max=%.5f"
              % (i, i*0.01, E, (E-E0)/E0, np.max(np.abs(phi))))

# Also check: is the FFT derivative self-consistent? d/dx cos(k0 x) = -k0 sin(k0 x)
# compute spectral derivative manually and compare RMS residual.
ph = np.fft.fft(phi)
dph = np.fft.ifft(1j*P.KX*ph).real
exact = -k0*np.sin(k0*P.X)
print("spectral-d/dphi RMS residual vs exact: %.3e" % np.sqrt(np.mean((dph-exact)**2)))
