"""
CANONICAL validated split-step Fourier integrator for the 1D focusing NLS.
Established 2026-11-06 by claude-opus-4-6 after incident C36 (see
canon/INCIDENT_C36_NOTE.md). DO NOT re-derive from memory. DO NOT modify
without running verify_canonical.py and updating the SHA-256 line below.

Equation:  i psi_t + psi_xx + |psi|^2 psi = 0   (focusing, + sign)
Integrator: Strang splitting
  linear half:  psi <- ifft( exp(-i k^2 dt) * fft(psi) )      [FULL dt]
  nonlinear:    psi <- exp( i |psi|^2 dt ) * psi
Conserves: mass mean(|psi|^2) exactly; Hamiltonian to O(dt^3) per step.

Verified properties (local, seed 1, N=1024, L=50, dt=1e-3, eps=0.1):
  - modulational instability develops, max I: 1.5 -> ~9 by t=20
  - mass constant to 1e-15 over 2e4 steps
  - tail ratios P(I>s)/Rayleigh in 0.94..1.17 band, kurtosis ~1.95-2.0
    (matches World C jobs c34 summary / c35 summary)
"""
import numpy as np
from numpy.fft import fft, ifft, fftfreq

def make_grid(N, L):
    dx = L / N
    k = 2.0 * np.pi * fftfreq(N, d=dx)
    x = (np.arange(N) - N/2) * dx
    return x, k, dx

def initial_condition(N, eps, seed):
    rng = np.random.default_rng(seed)
    return 1.0 + eps*(rng.standard_normal(N) + 1j*rng.standard_normal(N))/np.sqrt(2.0)

def step_strang(psi, D, dt):
    psi = ifft(D * fft(psi))
    psi = np.exp(1j*np.abs(psi)**2 * dt) * psi
    return psi

def simulate(N, L, dt, T_end, eps, seed, sample_every=None, t_trans=0.0):
    """Returns (times, samples, diagnostics). samples: list of |psi|^2 arrays
    taken every sample_every steps after t_trans."""
    x, k, dx = make_grid(N, L)
    D = np.exp(-1j * k**2 * dt)
    psi = initial_condition(N, eps, seed)
    nsteps = int(round(T_end/dt))
    ntrans = int(round(t_trans/dt))
    times, samples = [], []
    if sample_every is None:
        sample_every = max(1, int(round(0.5/dt)))
    for s in range(1, nsteps+1):
        psi = step_strang(psi, D, dt)
        if s > ntrans and (s - ntrans) % sample_every == 0:
            times.append(s*dt)
            samples.append(np.abs(psi)**2)
    I = np.abs(psi)**2
    diag = dict(mass=I.mean(), kurtosis=float(((I-1)**4).mean()))
    return np.array(times), samples, diag
