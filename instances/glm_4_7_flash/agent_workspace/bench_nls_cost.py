"""Benchmark: serial cost of ONE NLS realization at production settings."""
import numpy as np, time

def intensity(psi):
    return psi.real*psi.real + psi.imag*psi.imag

def one(seed, N, L, dt, T, eps=0.05, kymo=False):
    dx = L/N
    k = 2.0*np.pi*np.fft.fftfreq(N, d=dx)
    K2 = k*k
    lin_half = np.exp(-0.5j*K2*dt)
    nsteps = int(round(T/dt))
    rng = np.random.default_rng(seed)
    psi = np.ones(N, dtype=complex)
    psi += eps*(rng.standard_normal(N) + 1j*rng.standard_normal(N))/np.sqrt(2)
    t0 = time.time()
    for n in range(1, nsteps+1):
        psi = np.fft.ifft(lin_half*np.fft.fft(psi))
        psi *= np.exp(2j*dt*intensity(psi))
        psi = np.fft.ifft(lin_half*np.fft.fft(psi))
    return time.time()-t0

for (N, L, dt, T) in [(1024, 128, 0.0025, 10.0),   # benchmark scale
                      (1024, 128, 0.0025, 10.0),
                      (2048, 200, 0.0025, 10.0),
                      (2048, 200, 0.0025, 10.0)]:
    el = one(1, N, L, dt, T)
    print(f"N={N:5d} dt={dt} T={T:5.1f}: {el:6.2f}s  -> extrapolated T=100: {el*10:7.1f}s/realization")
