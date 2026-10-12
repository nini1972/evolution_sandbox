"""Isolate the energy-conservation leak in the split scheme.
A: static single kink (force=0 everywhere) -> must stay EXACTLY stationary.
B: two-kink initial field, KINETIC-ONLY steps (spectral free wave) -> should be
   near-exact (energy err ~ machine*steps).
C: two-kink initial field, FULL Strang -> reproduces the ~18% leak? at what step?
"""
import numpy as np, time
import phi4_resonance_vectorized as P

def static_kink():
    return np.tanh(P.X/np.sqrt(2.0)), np.zeros_like(P.X)

def two_kink(v):
    g = 1.0/np.sqrt(1.0-v*v); s = g/np.sqrt(2.0)
    phi = np.tanh(s*(P.X+P.X0)) - np.tanh(s*(P.X-P.X0)) - 1.0
    sech2_k  = (1.0/np.cosh(s*(P.X+P.X0)))**2
    sech2_ak = (1.0/np.cosh(s*(P.X-P.X0)))**2
    pi = -v*s*(sech2_k + sech2_ak)
    return phi, pi

def report(tag, phi, pi):
    E = P.total_energy(phi, pi)
    return E, np.max(np.abs(phi))

print("== A: static single kink (expect E const, phi const) ==")
phi, pi = static_kink()
E0, m0 = report("A0", phi, pi)
for _ in range(2000):
    phi, pi = P.strang_step(phi, pi, 0.01)
E1, m1 = report("A1", phi, pi)
print(f"  E0={E0:.8f} E1={E1:.8f} dE={abs(E1-E0)/E0:.3e}  |phi|max {m0:.4f}->{m1:.4f}")

print("== B: two-kink, KINETIC-ONLY (spectral free wave, exact) ==")
phi, pi = two_kink(0.22)
E0, m0 = report("B0", phi, pi)
for _ in range(500):
    phi, pi = P.kinetic_step(phi, pi, 0.01)
E1, m1 = report("B1", phi, pi)
print(f"  E0={E0:.8f} E1={E1:.8f} dE={abs(E1-E0)/E0:.3e}  |phi|max {m0:.4f}->{m1:.4f}")

print("== C: two-kink, FULL Strang, track where leak begins ==")
phi, pi = two_kink(0.22)
E0, m0 = report("C0", phi, pi)
for step in range(1, 601):
    phi, pi = P.strang_step(phi, pi, 0.01)
    if step % 100 == 0:
        E1, m1 = report(f"C{step}", phi, pi)
        print(f"  step {step:4d} t={step*0.01:6.2f} E={E1:.6f} dE={abs(E1-E0)/E0:.4e} |phi|max={m1:.4f}")
