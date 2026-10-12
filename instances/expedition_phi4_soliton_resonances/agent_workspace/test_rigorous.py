"""Rigorous isolation with EXACT grid-periodic modes + initial-energy decomposition."""
import numpy as np
import phi4_resonance_vectorized as P

def grad_energy_only(phi):
    ph = np.fft.fft(phi)
    return 0.5*np.sum(P.KX**2*np.abs(ph)**2)*P.DX/P.N

def free_energy(phi, pi):           # 1/2 pi^2 + 1/2 phi_x^2  (what kinetic_step conserves)
    return np.sum(0.5*pi**2)*P.DX + grad_energy_only(phi)

print("="*70)
print("TEST 1: kinetic_step on an EXACT grid mode (integer m)")
m = 64
k = P.KX[m]
phi = np.cos(k*P.X)
pi  = np.zeros_like(P.X)
print(f"  grid mode k={k:.5f} (period {2*np.pi/k:.2f} vs L={P.L})")
E0 = free_energy(phi, pi)
print(f"  free_energy(0)={E0:.8f}")
mode0 = np.abs(np.fft.fft(phi))[m]
ok = True
for i in range(1, 401):
    phi, pi = P.kinetic_step(phi, pi, 0.01)
    if i % 100 == 0:
        E = free_energy(phi, pi)
        spec = np.abs(np.fft.fft(phi)); spec[m+1:]=0; spec[:m]=0; spec[m-1]=0
        leak = np.sum(spec)            # power outside the single mode m
        print(f"  step {i:3d} freeE={E:.8f} dE={abs(E-E0)/E0:+.2e} "
              f"offmode_power={leak/mode0:.2e} |phi|max={np.max(np.abs(phi)):.5f}")

print("="*70)
print("TEST 2: spectral derivative accuracy on exact grid mode")
phi = np.cos(k*P.X)
dphi = np.fft.ifft(1j*P.KX*np.fft.fft(phi)).real
exact = -k*np.sin(k*P.X)
print(f"  RMS residual of spectral d/dx vs analytic: {np.sqrt(np.mean((dphi-exact)**2)):.3e}")

print("="*70)
print("TEST 3: initial two-kink energy decomposition vs analytic 2*gamma*M")
v = 0.22
g = 1.0/np.sqrt(1.0-v*v); s = g/np.sqrt(2.0)
phi = np.tanh(s*(P.X+P.X0)) - np.tanh(s*(P.X-P.X0)) - 1.0
sech2_k  = (1.0/np.cosh(s*(P.X+P.X0)))**2
sech2_ak = (1.0/np.cosh(s*(P.X-P.X0)))**2
pi = -v*s*(sech2_k + sech2_ak)
E_tot = P.total_energy(phi, pi)
E_kin = np.sum(0.5*pi**2)*P.DX
E_grad= grad_energy_only(phi)
E_pot = np.sum(0.25*(phi**2-1)**2)*P.DX
M = P.M_KINK
print(f"  v={v}  gamma={g:.5f}  analytic 2*gamma*M = {2*g*M:.6f}")
print(f"  code total_energy = {E_tot:.6f}")
print(f"  breakdown:  E_kin={E_kin:.6f}  E_grad={E_grad:.6f}  E_pot={E_pot:.6f}")
print(f"  E_kin+E_grad+E_pot = {E_kin+E_grad+E_pot:.6f}  (== total? {abs(E_kin+E_grad+E_pot-E_tot)<1e-9})")
print(f"  analytic split per kink: M_kin=M_grad=M_pot=M/3={M/3:.5f}; total/2 = {E_tot/2:.6f}")

print("="*70)
print("TEST 4: full Strang, track total_energy THROUGH collision for v=0.22")
phi, pi = np.tanh(s*(P.X+P.X0)) - np.tanh(s*(P.X-P.X0)) - 1.0, pi
E0 = P.total_energy(phi, pi)
for step in range(1, 16001):
    phi, pi = P.strang_step(phi, pi, 0.01)
    if step in (1000,2000,4000,6000,8000,10000,12000,14000,15999):
        E = P.total_energy(phi, pi)
        print(f"  t={step*0.01:7.2f}  E={E:.6f}  dE={abs(E-E0)/E0:+.4e}  |phi|max={np.max(np.abs(phi)):.4f}")
