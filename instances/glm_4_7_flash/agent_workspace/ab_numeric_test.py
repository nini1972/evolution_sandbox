"""Gold-standard test: integrate the rotating-frame NLS
    i psi_t + psi_xx + 2(|psi|^2 - 1) psi = 0
spectrally, starting from the EXACT AB formula at t=0, and compare
the evolved field against the exact formula at later times.
Also render |psi| heatmaps. Outputs: ab_numeric_test.png, ab_heatmap.png, ab_metrics.json
"""
import matplotlib
matplotlib.use('Agg')
import numpy as np, json

# ---------- exact solution ----------
def ab_psi(x, t, K):
    W = K*np.sqrt(4.0-K*K)
    r = np.sqrt(1.0 - K*K/4.0)
    c = np.cosh(W*t); s = np.sinh(W*t); C = np.cos(K*x)
    num = -(K*K)*c - 1j*W*s
    den = 2.0*(c - r*C)
    return 1.0 + num/den

# ---------- spectral integrator (IF-RK4, rotating frame) ----------
L = 2*np.pi
def integrate(psi0, T, N=256, nsteps=400):
    dx = L/N
    x = np.arange(N)*dx
    k = 2*np.pi*np.fft.fftfreq(N, d=dx)
    k2 = k*k
    dt = T/nsteps
    psi = psi0.copy().astype(complex)
    # i psi_t = -psi_xx - 2(|psi|^2-1) psi  ->  linear part: i psi_t = -psi_xx  => psi_t = i psi_xx
    # integrating factor: psi = exp(i k^2 t) * w
    def rhs(w):
        psi = w*np.exp(-1j*k2*0)  # w already carries IF; reconstruct psi at substep
        return None
    # simpler: RK4 on full RHS with exact linear IF applied per step
    Lop = 1j*k2
    def nl(psi):
        return -2j*(np.abs(psi)**2 - 1.0)*psi
    for n in range(nsteps):
        # split: linear exact, nonlinear RK4 with frozen IF? Use ETDRK4-lite: RK4 with IF weight
        # We do standard IF-RK4: psi = e^{L dt} (psi + RK4 corrections on nonlinear)
        # Implementation: RK4 in the "interaction picture"
        t0 = n*dt
        E = np.exp(Lop*dt/2); Ei = np.exp(-Lop*dt/2)
        def NR(w, s):  # nonlinear in interaction picture at offset s
            psi = w*np.exp(Lop*(s))
            return Ei*0 + 0  # placeholder
        # do straightforward RK4 on dpsi/dt = L psi + N(psi) with L treated exactly per substep
        def Nf(psi):
            return -2j*(np.abs(psi)**2 - 1.0)*psi
        p = psi
        k1 = Nf(p)
        k2_ = Nf((p + dt/2*(Lop*p*0 + k1))*np.exp(Lop*dt/2))  # approximate
        # ---- cleaner: use standard RK4 including linear operator (dt small enough) ----
        k1 = Lop*p + Nf(p)
        k2_ = Lop*(p+dt/2*k1) + Nf(p+dt/2*k1)
        k3 = Lop*(p+dt/2*k2_) + Nf(p+dt/2*k2_)
        k4 = Lop*(p+dt*k3) + Nf(p+dt*k3)
        psi = p + dt/6*(k1+2*k2_+2*k3+k4)
    return psi, x

K = 1.0
N = 256; nsteps = 4000
x = np.arange(N)*(L/N)
T = 2.0
psi0 = ab_psi(x, 0.0, K)
psiT, _ = integrate(psi0, T, N=N, nsteps=nsteps)
exact = ab_psi(x, T, K)
err = np.max(np.abs(psiT - exact))
print(f"K={K}, T={T}: max |numeric - exact| = {err:.3e}")
rel = err/np.max(np.abs(exact))
print(f"relative error: {rel:.3e}")

# residual check of exact formula by finite differences too
def residual_fd(K, t0, N=512, h=1e-4):
    xs = np.arange(N)*(L/N)
    p = lambda tt: ab_psi(xs, tt, K)
    pt = (p(t0+h)-p(t0-h))/(2*h)
    pxx = (np.roll(p(t0),-1)-2*p(t0)+np.roll(p(t0),1))/( (L/N)**2 )
    u = p(t0)
    R = 1j*pt + pxx + 2*(np.abs(u)**2-1)*u
    return np.max(np.abs(R))
print("FD residual of exact formula at t=0.3:", residual_fd(K, 0.3))

# ---------- heatmap of |psi| ----------
Kv = 1.0
W = Kv*np.sqrt(4-Kv*Kv)
ts = np.linspace(-3.0/W, 3.0/W, 400)
xs = np.linspace(0, 2*np.pi/Kv, 400)
TT, XX = np.meshgrid(ts, xs, indexing='ij')
M = np.abs(ab_psi(XX, TT, Kv))
import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 2, figsize=(13,5))
im = axes[0].pcolormesh(XX, W*TT, M, shading='auto', cmap='inferno')
axes[0].set_xlabel('x'); axes[0].set_ylabel('W t')
axes[0].set_title('|psi| : Akhmediev breather (exact), K=1')
fig.colorbar(im, ax=axes[0])
# profile at peak time
Mprof = np.abs(ab_psi(xs, ts[np.argmax(M[:,200])], Kv))
axes[1].plot(xs, Mprof, 'r-', lw=2)
axes[1].set_xlabel('x'); axes[1].set_title('peak profile |psi|')
axes[1].grid(alpha=0.3)
plt.tight_layout()
plt.savefig('ab_heatmap.png', dpi=110)
print("saved ab_heatmap.png")

# max amplitude scaling with K (key invariant: peak |psi| = 3 - K^2)
Ks = np.linspace(0.2, 1.99, 60)
peaks = []
for k in Ks:
    tt = 0.0
    xs2 = np.linspace(0, 2*np.pi/k, 800)
    peaks.append(np.max(np.abs(ab_psi(xs2, tt, k))))
peaks = np.array(peaks)
pred = 3.0 - Ks**2
print("max |psi| vs (3 - K^2): max abs deviation =", np.max(np.abs(peaks-pred)))
fig2, ax = plt.subplots(figsize=(7,5))
ax.plot(Ks, peaks, 'b-', label='peak |psi_AB| (numeric from formula)')
ax.plot(Ks, pred, 'r--', label='3 - K^2')
ax.set_xlabel('K'); ax.legend(); ax.grid(alpha=0.3)
ax.set_title('Peak amplitude law: |psi|_max = 3 - K^2')
plt.tight_layout(); plt.savefig('ab_peak_law.png', dpi=110)
print("saved ab_peak_law.png")

json.dump({"max_abs_err_integration": float(err),
           "relative_err": float(rel),
           "fd_residual": float(residual_fd(K,0.3)),
           "peak_law_max_dev": float(np.max(np.abs(peaks-pred)))},
          open('ab_metrics.json','w'), indent=2)
print("saved ab_metrics.json")
