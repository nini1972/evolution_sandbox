"""Split-step Fourier test, corrected linear sign. K=1 (commensurate with grid).
Equation: i psi_t + psi_xx + 2(|psi|^2-1) psi = 0
Linear substep: psi_hat *= exp(-i k^2 dt).  Nonlinear: psi *= exp(2i(|psi|^2-1) dt).
"""
import matplotlib
matplotlib.use('Agg')
import numpy as np, json
import matplotlib.pyplot as plt

def ab_psi(x, t, K):
    b = np.sqrt(1.0 - K*K/4.0); W = 2*K*b
    c = np.cosh(W*t); s = np.sinh(W*t); C = np.cos(K*x)
    return 1.0 + (-(K*K/2.0)*c - 1j*(W/2.0)*s)/(c - b*C)

L = 2*np.pi
N = 256
dx = L/N
x = np.arange(N)*dx
kk = 2*np.pi*np.fft.fftfreq(N, d=dx)
k2 = kk*kk
LF = np.exp(-1j*k2)   # per unit time

def step(psi, dt):
    psi = psi*np.exp(2j*(np.abs(psi)**2 - 1.0)*dt/2)
    ph = np.fft.fft(psi)
    psi = np.fft.ifft(np.exp(-1j*k2*dt)*ph)
    psi = psi*np.exp(2j*(np.abs(psi)**2 - 1.0)*dt/2)
    return psi

K = 1.0
T = 3.0
def run(dt, T=3.0, K=1.0):
    psi = ab_psi(x, 0.0, K).astype(complex)
    n = int(round(T/dt))
    for _ in range(n):
        psi = step(psi, dt)
    return psi

for dt in [0.01, 0.005, 0.0025, 0.00125]:
    psi = run(dt)
    err = np.max(np.abs(psi - ab_psi(x, T, K)))
    print(f"dt={dt:8.5f}  max|numeric-exact| at T={T}: {err:.3e}")

# convergence orders
dts = [0.01, 0.005, 0.0025, 0.00125]
es = [np.max(np.abs(run(d)-ab_psi(x,T,K))) for d in dts]
orders = [np.log(es[i]/es[i+1])/np.log(dts[i]/dts[i+1]) for i in range(len(dts)-1)]
print("split-step observed orders:", [f"{o:.2f}" for o in orders])

# also test at negative times (breather coming in from |t| large)
Tm = -2.0
psi = run(0.0025, T=Tm)
errm = np.max(np.abs(psi - ab_psi(x, Tm, K)))
print(f"backward to T=-2: max|numeric-exact| = {errm:.3e}")

# conservation checks along the way (Hamiltonian flow invariants)
def invariants(psi):
    n = np.sum(np.abs(psi)**2)/N
    h = np.sum(-np.abs(np.gradient(np.real(psi))+1j*np.gradient(np.imag(psi)))**2 + (np.abs(psi)**2-1)**2)/N
    return n, h
psi = ab_psi(x,0,K).astype(complex)
n0, h0 = invariants(psi)
psi2 = run(0.0025, T=1.5)
n1, h1 = invariants(psi2)
print(f"norm: {n0:.6f} -> {n1:.6f}   H: {h0:.6f} -> {h1:.6f}")

json.dump({"dts": dts, "errors_T3": es, "orders": orders,
           "backward_err": float(errm),
           "norm0": float(n0), "norm1": float(n1), "H0": float(h0), "H1": float(h1)},
          open('ab_metrics2.json','w'), indent=2)
print("saved ab_metrics2.json")
