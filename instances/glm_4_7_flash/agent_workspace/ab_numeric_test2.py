"""Split-step Fourier test of the exact AB formula + corrected peak law.
Equation (rotating frame): i psi_t + psi_xx + 2(|psi|^2-1) psi = 0
Split: linear L: psi -> exp(i k^2 dt) psi (FFT); nonlinear N: psi -> exp(2i(|psi|^2-1) dt) psi.
Strang splitting. Both subflows are exact => global error O(dt^2).
"""
import matplotlib
matplotlib.use('Agg')
import numpy as np, json
import matplotlib.pyplot as plt

K = 1.0
b = np.sqrt(1.0 - K*K/4.0)
W = 2*K*b

def ab_psi(x, t, K):
    b = np.sqrt(1.0 - K*K/4.0); W = 2*K*b; r = b
    c = np.cosh(W*t); s = np.sinh(W*t); C = np.cos(K*x)
    return 1.0 + (-(K*K/2.0)*c - 1j*(W/2.0)*s)/(c - r*C)

L = 2*np.pi
N = 256
dx = L/N
x = np.arange(N)*dx
kk = 2*np.pi*np.fft.fftfreq(N, d=dx)
k2 = kk*kk

def step(psi, dt):
    # half nonlinear
    psi = psi*np.exp(2j*(np.abs(psi)**2 - 1.0)*dt/2)
    # full linear
    psi = np.real(np.fft.ifft(np.exp(1j*k2*dt)*np.fft.fft(psi))) + 1j*np.imag(np.fft.ifft(np.exp(1j*k2*dt)*np.fft.fft(psi)))
    # half nonlinear
    psi = psi*np.exp(2j*(np.abs(psi)**2 - 1.0)*dt/2)
    return psi

T = 3.0; nsteps = 6000; dt = T/nsteps
psi = ab_psi(x, 0.0, K).astype(complex)
snap_times = [0.0, 0.5, 1.0, 2.0, 3.0]
snaps = {}
errs = []
t = 0.0
snapset = set(np.round(snap_times,6))
for n in range(nsteps+1):
    if np.any(np.abs(np.array(snap_times)-t) < dt/2):
        ex = ab_psi(x, t, K)
        e = np.max(np.abs(psi-ex))
        errs.append((t, e))
        snaps[round(t,3)] = psi.copy()
    if n < nsteps:
        psi = step(psi, dt); t += dt

for tt, e in errs:
    print(f"t={tt:5.2f}  max|numeric-exact| = {e:.3e}")

# convergence order check: error ~ dt^2
def run(dt):
    psi = ab_psi(x,0.0,K).astype(complex); n = int(round(T/dt))
    for _ in range(n): psi = step(psi, dt)
    return np.max(np.abs(psi - ab_psi(x,T,K)))
dts = [0.02, 0.01, 0.005, 0.0025]
es = [run(d) for d in dts]
print("dt:", dts); print("err:", [f"{e:.2e}" for e in es])
orders = [np.log(es[i]/es[i+1])/np.log(dts[i]/dts[i+1]) for i in range(len(dts)-1)]
print("observed split-step orders:", [f"{o:.2f}" for o in orders])

# spectral residual of exact formula (much cleaner than FD)
def spectral_residual(K, t0):
    ps = ab_psi(x, t0, K)
    h = 1e-5
    pt = (ab_psi(x,t0+h,K)-ab_psi(x,t0-h,K))/(2*h)
    pxx = np.fft.ifft(-k2*np.fft.fft(ps))
    R = 1j*pt + pxx + 2*(np.abs(ps)**2-1)*ps
    return np.max(np.abs(R))
R0 = spectral_residual(K, 0.3); R1 = spectral_residual(1.3, 0.7)
print("spectral residual t=0.3:", f"{R0:.2e}", " t=0.7:", f"{R1:.2e}")

# corrected peak law
Ks = np.linspace(0.05, 1.995, 100)
peaks = []
for k in Ks:
    xs = np.linspace(0, 2*np.pi/k, 2000)
    peaks.append(np.max(np.abs(ab_psi(xs, 0.0, k))))
peaks = np.array(peaks); pred = 1.0 + 2.0*np.sqrt(1.0 - Ks**2/4.0)
dev = np.max(np.abs(peaks-pred))
print("PEAK LAW  max|1+2sqrt(1-K^2/4) - measured| =", f"{dev:.2e}")

fig, ax = plt.subplots(figsize=(7,5))
ax.plot(Ks, peaks, 'b-', lw=2, label='measured peak |psi_AB|')
ax.plot(Ks, pred, 'r--', lw=1.5, label='1 + 2 sqrt(1-K^2/4)')
ax.set_xlabel('K'); ax.set_ylabel('peak |psi|'); ax.legend(); ax.grid(alpha=0.3)
ax.set_title('Akhmediev breather peak-amplitude law')
plt.tight_layout(); plt.savefig('ab_peak_law.png', dpi=110)

# heatmap
Kv = 1.0; Wv = 2*Kv*np.sqrt(1-Kv*Kv/4)
ts = np.linspace(-3.5/Wv, 3.5/Wv, 500)
xs = np.linspace(0, 2*np.pi/Kv, 500)
TT, XX = np.meshgrid(ts, xs, indexing='ij')
M = np.abs(ab_psi(XX, TT, Kv))
fig2, axes = plt.subplots(1, 2, figsize=(13,5))
im = axes[0].pcolormesh(XX, Wv*TT, M, shading='auto', cmap='inferno')
axes[0].set_xlabel('x'); axes[0].set_ylabel('W t'); axes[0].set_title('|psi_AB| exact, K=1 (peak 1+2b≈2.73)')
fig2.colorbar(im, ax=axes[0])
axes[1].plot(ts, M[:, np.argmin(np.abs(xs-0))], 'k-', lw=2)
axes[1].set_xlabel('t'); axes[1].set_ylabel('|psi| at x=0'); axes[1].grid(alpha=0.3)
axes[1].set_title('breathing at x=0')
plt.tight_layout(); plt.savefig('ab_heatmap.png', dpi=110)
print("saved ab_peak_law.png, ab_heatmap.png")

json.dump({"errors_at_snaps": errs,
           "convergence_orders": orders,
           "spectral_residuals": [float(R0), float(R1)],
           "peak_law_max_dev": float(dev)},
          open('ab_metrics.json','w'), indent=2)
print("saved ab_metrics.json")
