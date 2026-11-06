import numpy as np, time, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ---------- grid ----------
N  = 2048
L  = 96.0
dx = L/N
x  = (np.arange(N) - N/2)*dx
K  = 2*np.pi*np.fft.fftfreq(N, dx)
K2 = K**2

S2 = np.sqrt(2.0)
def kink(u):
    return np.tanh(u/S2)
def kinkp(u):
    t = np.tanh(u/S2)
    return (1.0 - t*t)/S2

# ---------- ICs (verified algebra) ----------
def make_ka(v, d=15.0):
    g  = 1.0/np.sqrt(1.0 - v*v)
    u1 = g*(x + d);  u2 = g*(x - d)
    s1, s2 = np.cosh(u1), np.cosh(u2)
    phi = kink(u1) - kink(u2) - 1.0
    pi  = -(g*v/S2)*(1.0/s1**2 + 1.0/s2**2)
    return phi, pi

def make_single_kink(v, x0=-L/4):
    g = 1.0/np.sqrt(1.0 - v*v)
    u = g*(x - x0)
    phi = kink(u)
    pi  = -(g*v/S2)/np.cosh(u)**2
    return phi, pi

# ---------- diagnostics ----------
def gradient(phi):   return np.fft.ifft(1j*K*np.fft.fft(phi)).real
def energy(phi, pi):
    E1 = 0.5*np.sum(pi**2)*dx
    E2 = 0.5*np.sum(gradient(phi)**2)*dx
    E3 = 0.25*np.sum((phi*phi - 1.0)**2)*dx
    return E1 + E2 + E3, (E1, E2, E3)

# ---------- CORRECT spectral Strang splits ----------
# H1 (wave): phi_tt = phi_xx - m^2 phi   ;  H2 (kick): V(phi) = (phi^2-1)^2/4
#   massive:  m^2 = 1   ->  omega^2 = K^2 + 1,  kick force = -phi^3 + 2 phi
#   massless: m^2 = 0   ->  omega^2 = K^2,       kick force = -phi^3 + phi
def strang_split(phi, pi, dt, nsteps, massive=True):
    if massive:
        w2 = K2 + 1.0
    else:
        w2 = K2.copy(); w2[0] = (2*np.pi/L/dx*0 + 1e-12)**2  # avoid /0 at k=0
    w  = np.sqrt(w2)
    cw = np.cos(w*dt)
    sw = np.sinc(w*dt/np.pi)*dt          # = sin(w dt)/w
    kickcoef = 2.0 if massive else 1.0
    for _ in range(nsteps):
        # half kick (pi update)
        pih = pi + 0.5*dt*(-(phi**3) + kickcoef*phi)
        # full wave step on (phi, pih)
        ph = phi
        phk = np.fft.fft(ph); pik = np.fft.fft(pih)
        phk = cw*phk + sw*pik
        pik = cw*pik - w2*sw*phk
        ph  = np.fft.ifft(phk).real
        pih = np.fft.ifft(pik).real
        # half kick (phi and pi update)
        phi = ph + 0.5*dt*pih
        pi  = pih + 0.5*dt*(-(phi**3) + kickcoef*phi)
    return phi, pi

# ---------- tests ----------
def run(integrator, v, dt=0.01, T=40.0, d=15.0, kind='ka', massive=True):
    n = int(round(T/dt))
    if kind == 'ka':   phi, pi = make_ka(v, d)
    else:              phi, pi = make_single_kink(v)
    E0, _ = energy(phi, pi)
    phi, pi = integrator(phi, pi, dt, n, massive=massive)
    E1, _ = energy(phi, pi)
    return (E1 - E0)/E0

t0 = time.time()
print("=== sanity: IC momentum & energy ===")
for v in (0.0, 0.02, 0.10, 0.26):
    phi, pi = make_ka(v)
    P = np.sum(pi*gradient(phi))*dx
    E0, (E1,E2,E3) = energy(phi, pi)
    print(f"v={v:.2f}: P={P:+.3e}  E0={E0:.6f} (pi2={E1:.4f} grad2={E2:.4f} pot={E3:.4f}) max|phi|={np.max(np.abs(phi)):.4f}")
print(f"t={time.time()-t0:.1f}s")

print("\n=== A: v-scan, MASSIVE split, dt=0.01, T=40 ===")
vs = [0.0, 0.02, 0.05, 0.10, 0.18, 0.22, 0.26]
resA = []
for v in vs:
    r = run(strang_split, v, massive=True)
    resA.append((v, r)); print(f"v={v:.2f}: dE/E = {r:+.4e}")
print(f"t={time.time()-t0:.1f}s")

print("\n=== B: single kink vs pair, MASSIVE split ===")
for kind in ('ka','kink'):
    for v in (0.02, 0.26):
        print(f"{kind:4s} v={v:.2f}: dE/E = {run(strang_split, v, kind=kind, massive=True):+.4e}")
print(f"t={time.time()-t0:.1f}s")

print("\n=== C: dt-scan v=0.26, T=10 (secular -> dE/E ~ dt^2) ===")
for dt in (0.01, 0.005, 0.0025):
    r = run(strang_split, 0.26, dt=dt, T=10.0, massive=True)
    print(f"dt={dt:.4f}: dE/E(T=10) = {r:+.4e}   *(dt_ref/dt)^2 = {r*(0.01/dt)**2:+.4e}")
print(f"t={time.time()-t0:.1f}s")

print("\n=== D: MASSLESS split v-scan, dt=0.01, T=10 ===")
for v in (0.02, 0.10, 0.26):
    print(f"v={v:.2f}: dE/E = {run(strang_split, v, T=10.0, massive=False):+.4e}")
print(f"t={time.time()-t0:.1f}s")

# ---------- figure ----------
fig, ax = plt.subplots(figsize=(7,5))
v_, r_ = zip(*resA)
ax.plot(v_, np.abs(r_), 'o-', label='massive split |dE/E|, dt=0.01, T=40')
ax.set_xlabel('v'); ax.set_ylabel('|dE/E|'); ax.set_yscale('log')
ax.axhline(1e-6, ls=':', color='gray', label='1e-6 (target)')
ax.legend(); ax.set_title('phi4 energy drift vs impact velocity (fixed spectral split)')
fig.tight_layout(); fig.savefig('phi4_diag_vscan.png', dpi=150)
print("saved phi4_diag_vscan.png")
np.save('resA.npy', np.array(resA))
