"""Final verification battery:
1. forward + BACKWARD split-step integration vs exact AB (K=1)
2. Hamiltonian H = <|psi_x|^2 - (|psi|^2-1)^2> conservation
3. Peregrine limit: K->0 with rescaled coords -> psi_P = 1 - 4(1+4it)/(1+4x^2+16t^2)
4. K=0.5 commensurate-grid independent check (K=1/(2pi/L)...)
"""
import matplotlib
matplotlib.use('Agg')
import numpy as np, json

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

def step(psi, dt):
    psi = psi*np.exp(2j*(np.abs(psi)**2 - 1.0)*dt/2)
    psi = np.fft.ifft(np.exp(-1j*k2*dt)*np.fft.fft(psi))
    psi = psi*np.exp(2j*(np.abs(psi)**2 - 1.0)*dt/2)
    return psi

K = 1.0
# ---- backward run: t: 0 -> -2 (dt>0, step with -dt) ----
dt = 0.0025
psi = ab_psi(x, 0.0, K).astype(complex)
n = int(round(2.0/dt))
for _ in range(n):
    psi = step(psi, -dt)
err_back = np.max(np.abs(psi - ab_psi(x, -2.0, K)))
print(f"BACKWARD to t=-2: max|numeric-exact| = {err_back:.3e}")

# ---- Hamiltonian conservation (correct sign) ----
def H(psi):
    px = (np.roll(psi,-1)-np.roll(psi,1))/(2*dx)
    return np.mean(np.abs(px)**2 - (np.abs(psi)**2-1)**2)
h0 = H(ab_psi(x,0,K))
psi = ab_psi(x,0,K).astype(complex)
for _ in range(int(round(1.0/dt))):
    psi = step(psi, dt)
h1 = H(psi)
print(f"H: t=0: {h0:.6f}   t=1: {h1:.6f}   drift {abs(h1-h0):.2e}")

# ---- K = 1/2 check on doubled domain (commensurate) ----
L2 = 4*np.pi
x2 = np.arange(N)*(L2/N)
kk2 = 2*np.pi*np.fft.fftfreq(N, d=L2/N)
k2_2 = kk2*kk2
def step2(psi, dt):
    psi = psi*np.exp(2j*(np.abs(psi)**2 - 1.0)*dt/2)
    psi = np.fft.ifft(np.exp(-1j*k2_2*dt)*np.fft.fft(psi))
    psi = psi*np.exp(2j*(np.abs(psi)**2 - 1.0)*dt/2)
    return psi
K2 = 0.5
psi = ab_psi(x2, 0.0, K2).astype(complex)
for _ in range(int(round(1.5/dt))):
    psi = step2(psi, dt)
err_half = np.max(np.abs(psi - ab_psi(x2, 1.5, K2)))
print(f"K=0.5, T=1.5: max|numeric-exact| = {err_half:.3e}")

# ---- Peregrine limit ----
# psi_AB(x,t;K) with K->0: set X=Kx/2... claim: lim = 1 - 4(1+4i T)/(1+4 X^2+16 T^2)
# with X = K x/2 ... check: substitute x -> X, t -> T directly:
# ab_psi ~ 1 - (1+4iT)/(X^2... ) we derived psi ~ 1 - (1+4it)/(x^2+4t^2+1/4)
def peregrine(x, t):
    return 1.0 - 4.0*(1.0+4j*t)/(1.0+4*x*x+16*t*t)
Ks = [1e-1, 1e-2, 1e-3]
for k in Ks:
    # rescale: physical coords X,T fixed; lattice coords x_phys = 2X/K, t_phys = T/K (since W~2K... careful)
    # from derivation: psi_AB(x,t;K) = 1-(1+4it)/(x^2+4t^2+1/4) + O(K) where x,t are the SAME coordinates.
    xg = np.linspace(-2, 2, 400)
    tg = 0.3
    ab = ab_psi(xg, tg, k)
    pg = peregrine(xg, tg)
    # need small x,t window of size O(1/K): use xg ~ O(1), tg~O(1) region where O(K) corrections small?
    print(f"K={k}: max|AB - Peregrine| on |x|<2, t=0.3 = {np.max(np.abs(ab-pg)):.3e}")
# finer: the O(K) correction vanishes as K->0; test convergence
for k in [0.2, 0.1, 0.05]:
    xg = np.linspace(-1.5,1.5,300); tg=0.25
    d = np.max(np.abs(ab_psi(xg,tg,k)-peregrine(xg,tg)))
    print(f"  K={k}: dev={d:.3e}")

json.dump({"backward_err_T-2": float(err_back),
           "H0": float(h0), "H1": float(h1),
           "K_half_err": float(err_half)},
          open('ab_metrics3.json','w'), indent=2)
print("saved ab_metrics3.json")
