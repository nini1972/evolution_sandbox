#!/usr/bin/env python3
"""
Forensic repro: Entry #001 'Lempel-Ziv Flatline Phenomenon'.

Original code path (resonance_archaeology_1.py lines 147-154):

    for i in range(N):
        binary_seq = phase_to_binary(phases_steady[i:i+1].T)
        if len(binary_seq) > 0 and len(binary_seq[0]) > 10:
            lz = lempel_ziv_complexity(binary_seq[0])
            all_lz.append(lz)
    mean_lz = np.mean(all_lz) if all_lz else 0

phases_steady has shape (N, time) after phases = sol.T.
phases_steady[i:i+1] -> (1, time); .T -> (time, 1);
phase_to_binary np.diff(axis=0) -> (time-1, 1).
So binary_seq[0] is a ROW of length 1  =>  1 > 10 is False  =>  all_lz
stays empty => mean_lz = 0 for EVERY K, by the `else 0` fallback.

The reported 'LZ = 0 across all coupling strengths' is the literal
default of the ternary, not a property of Kuramoto dynamics.
"""
import numpy as np

# --- Exact original instrument -------------------------------------------
def lempel_ziv_complexity(sequence, normalize=True):
    s = ''.join(map(str, sequence))
    n = len(s)
    if n == 0:
        return 0
    i, l, k, c = 0, 1, 1, 0
    while l + k <= n:
        if s[i + k - 1] == s[l + k - 1]:
            k += 1
        else:
            c += 1
            i += 1
            if i == l:
                l, i, k = l + k, 0, 1
            else:
                k = 1
    c += 1
    return c / (n / np.log2(n)) if normalize and n > 1 else c

def phase_to_binary(phases, threshold=0):
    dpdt = np.diff(phases, axis=0)
    return (dpdt > threshold).astype(int)

# Simulate one K of the original size: N=50, T=100, dt=0.1
N, T, dt = 50, 100, 0.1
t = np.arange(0, T, dt)
# Stand in for odeint output: shape (time, N) -> .T -> (N, time)
phases = np.random.default_rng(42).normal(size=(len(t), N)).T * 0.1
phases_steady = phases[:, len(t) // 3:]          # (50, 667)

all_lz, shapes = [], []
for i in range(N):
    binary_seq = phase_to_binary(phases_steady[i:i + 1].T)
    shapes.append(binary_seq.shape)
    if len(binary_seq) > 0 and len(binary_seq[0]) > 10:
        all_lz.append(lempel_ziv_complexity(binary_seq[0]))

mean_lz = np.mean(all_lz) if all_lz else 0
print('binary_seq shapes:', set(shapes))
print('len(binary_seq[0]) =', len(binary_seq[0]), '-> guard 1 > 10 =',
      len(binary_seq[0]) > 10)
print('all_lz entries:', len(all_lz))
print('reported mean_lz =', mean_lz, '(the `else 0` fallback)')

# --- What the instrument WOULD have measured ------------------------------
per_osc = []
for i in range(N):
    per_osc.append(lempel_ziv_complexity(
        phase_to_binary(phases_steady[i:i + 1]).ravel()))
print('correct indexing, same data: per-oscillator LZ = %.4f .. %.4f'
      % (min(per_osc), max(per_osc)))

# --- The second defect: lab-frame sign(dphi/dt) ---------------------------
# Absolute phases drift monotonically once coupled => constant '1' string.
K, omega = 1.0, np.random.default_rng(0).normal(0, 0.1, N)
phi = phases_steady[:, -1].copy()
seq = []
for _ in range(600):
    z = np.mean(np.exp(1j * phi)); psi = np.angle(z); R = np.abs(z)
    phi += (omega + K * R * np.sin(psi - phi)) * 0.1
    seq.append((phi - psi))  # increments unchanged by frame for dphi
sign_seq = (np.diff(seq, axis=0) > 0).ravel()
print('lab-frame sign(dphi/dt): fraction of 1s = %.3f, LZ = %.4f'
      % (sign_seq.mean(), lempel_ziv_complexity(sign_seq)))
