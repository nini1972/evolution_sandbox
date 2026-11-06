import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Parameters
L = 96.0
N = 2048
dx = L / N
X = np.fft.fftfreq(N, d=dx) * (2*np.pi)  # physical k
K = np.fft.fftfreq(N, d=dx) * 2*np.pi
# Actually fftfreq gives cycles per unit length. k = 2pi * fftfreq.
# For derivative: d/dx in Fourier multiplies by i*k where k = 2*pi*fftfreq(N, dx).
K = 2*np.pi*np.fft.fftfreq(N, dx)
K[0] = 0.0
# second derivative operator
K2 = K**2
# massive dispersion
OM = np.sqrt(K2 + 1.0)   # mass^2 = 1 (linear term)
OM[0] = 0.0  # careful at k=0

def grad_spec(phi):
    return np.fft.ifft(1j*K*np.fft.fft(phi)).real

def energy(phi, pi, dx):
    T = 0.5*np.sum(pi**2)*dx
    G = 0.5*np.sum(grad_spec(phi)**2)*dx
    V = 0.25*np.sum((phi**2-1)**2)*dx
    return T+G+V, T, G, V

def initial_state(v, sep=14.0):
    # kink-antikink: phi0 = tanh((x+sep)/sqrt2) - tanh((x-sep)/sqrt2) - 1 ??? 
    # Actually kink (from -1 to +1): tanh(x/sqrt2). antikink (+1 to -1): -tanh(x/sqrt2).
    # pair: antikink at -sep, kink at +sep, so phi = -tanh((x+sep)/sqrt2) + tanh((x-sep)/sqrt2)
    # moving: pi = -v * dphi/dx * gamma
    ...
