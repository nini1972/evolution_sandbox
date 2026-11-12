"""
C39: SEED EXTENSION to kill far-tail starvation (s=12,13,14) ...
targets: expected events at s=13 ≈ 100 per arm → n_total = e^13/N ... seeds table.
Bit-compatible integrator (verbatim canon), seeds 1..n_total per arm.
StageTracker('c39_seed_extension'), per-seed incremental checkpoint within arm,
per-arm key 'L50'..'L800', final 'final'. C37 consistency check on seeds 1-12.
"""
import os, json, math, time
import numpy as np
from numpy.fft import fft, ifft, fftfreq

# CANONICAL INTEGRATOR — verbatim from canon/nls_splitstep_canonical.py
def make_grid(N, L):
    dx = L / N
    k = 2.0 * np.pi * fftfreq(N, d=dx)
    x = (np.arange(N) - N/2) * dx
    return x, k, dx

def initial_condition(N, eps, seed):
    rng = np.random.default_rng(seed)
    return 1.0 + eps*(rng.standard_normal(N) + 1j*rng.standard_normal(N))/sqrt2

def step_strang(psi, D, dt):
    psi = ifft(D * fft(psi))
    psi = np.exp(1j*np.abs(psi)**2 * dt) * psi
    return psi
