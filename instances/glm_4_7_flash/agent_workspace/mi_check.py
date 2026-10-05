"""Exact Akhmediev Breather: verify PDE residual and measure b(K).

Standard form (Akhmediev 1987) for i psi_t + psi_xx + 2|psi|^2 psi = 0:
  psi = 1 + (G cosh(b t) + i F sinh(b t)) / (sqrt(2) phi - cos(K x)) * ... 
We use the widely cited form:
  psi_AB = 1 + [b^2/(2) ... ] -- instead use the parameterization via phi in (0, pi/2):
  K = 2 sin(phi), b = 2 sin(phi) cos(phi)  (temporal growth rate)
  psi = 1 + 4 b [cosh(b t + i phi) ... ]

Let me just use the clean complex form:
  psi = 1 + [P cosh(b t) + i Q sinh(b t)] / [R cosh(b t) - cos(K x)]
with the literature constraints. The known exact one (e.g., Wikipedia "Akhmediev breather"):
  psi = 1 + [ (2*(1-2a) cosh(b t) + i sqrt(8a)*cosh... ]

STOP guessing. Derive numerically: take the known solution in the form used in most papers
(matveev & various):
  psi = [cosh(b t) - sqrt(1-?) ... ]

Empirical approach instead: HIGH-PRECISION TIME INTEGRATION from exact initial data.
Take K in (0,2), a = 1 - K^2/4 (MI parameter), then
  b = K * sqrt(1 - K^2/4)      (growth rate, = 2 sin(phi) cos(phi) with K = 2 sin phi)
  psi(x, 0) = 1 + A cos(K x),  psi_t(x,0) = -i [psi_xx + 2|psi|^2 psi]  (from PDE: psi_t = i(psi_xx+2|psi|^2 psi))

Wait, that only works if the initial condition matches the exact solution at t=0.
The exact AB at t=0 is: psi(x,0) = 1 + [G]/[R - cos(Kx)] (cosh(0)=1) -- i.e., NOT of form 1+A cos(Kx)
unless r=0... 

CORRECT EMPIRICAL APPROACH: numerical evolution of the MI eigenmode.
Initialize psi = 1 + eps*cos(Kx), eps small (e.g., 1e-4). Linear theory: |psi| grows like
cosh(b t) with b = K sqrt(1 - K^2/4) for i psi_t + psi_xx + 2|psi|^2 psi? Let's derive:
linearize around psi=1: psi = 1 + w. Then i w_t + w_xx + 2(w + w*) + ... = 0.
Fourier: w = a e^{i(K x - w_t t)} + conj... standard result: growth rate b = K sqrt(1 - K^2/4).
Check K=1: b = sqrt(3)/2 = 0.8660. The known MI band for unit background, focusing NLS with
coefficient 2: unstable for 0 < K < 2. Max growth at K = sqrt(2).

So: integrate NLS spectrally from psi = 1 + eps cos(Kx), fit |a(t)| ~ (eps/2) exp(b t) + c exp(-b t),
extract b(K) numerically, compare to b_theory = K sqrt(1 - K^2/4).
This is a genuine empirical test of the MI dispersion relation, independent of AB formulas.
"""
import numpy as np
matplotlib = __import__('matplotlib'); matplotlib.use('Agg')
import matplotlib.pyplot as plt

N = 512
L = 40.0                       # domain length
x = np.arange(N) * L / N - L/2
dx = L / N
Ks = np.linspace(0.2, 1.95, 12)
eps = 1e-4
dt = 0.002
Tmax = 8.0
nsteps = int(Tmax / dt)

kx = 2*np.pi*np.fft.fftfreq(N, d=dx)
k2 = kx**2

def nls_step(psi, dt):
    # split-step: half linear, full nonlinear, half linear
    # linear: i psi_t + psi_xx = 0 => psi_t = i psi_xx => psi~ = exp(-i k^2 dt) psi~
    psi = np.fft.ifft(np.exp(-1j*k2*dt/2) * np.fft.fft(psi))
    # nonlinear: i psi_t + 2|psi|^2 psi = 0 => psi~ = exp(2i|psi|^2 dt)
    psi = psi * np.exp(2j*np.abs(psi)**2 * dt)
    psi = np.fft.ifft(np.exp(-1j*k2*dt/2) * np.fft.fft(psi))
    return psi

results = []
for K in Ks:
    psi = 1.0 + eps*np.cos(K*x)
    log_amps = []
    times = []
    t = 0.0
    # track amplitude of mode K via Fourier coefficient at frequency K
    # nearest index
    idx = np.argmin(np.abs(kx - K))
    for n in range(nsteps):
        psi = nls_step(psi, dt)
        t += dt
        if n % 5 == 0:
            fh = np.fft.fft(psi - 1.0)
            amp = np.abs(fh[idx]) / N * 2  # cos coefficient => amp/2 in fft; fh[idx]/N ~ eps/2
            log_amps.append(np.log(max(amp, 1e-300)))
            times.append(t)
    times = np.array(times); la = np.array(log_amps)
    # fit exponential growth on early window where amp in [1e-3, 1] roughly linear in log
    mask = (la > np.log(eps*0.5+1e-12)) & (la < np.log(0.05)) & (times > 0.5)
    if mask.sum() < 5:
        mask = (times > 0.5) & (times < 3.0)
    A = np.polyfit(times[mask], la[mask], 1)
    b_num = A[0]
    b_theory = K*np.sqrt(max(1 - K**2/4, 0))
    results.append((K, b_num, b_theory))
    print(f"K={K:.3f}  b_num={b_num:.5f}  b_theory={b_theory:.5f}  ratio={b_num/b_theory:.4f}")

Ks_, bn, bt = np.array(results).T
fig, ax = plt.subplots(figsize=(7,5))
ax.plot(Ks_, bt, 'k-', lw=2, label=r'theory $b=K\sqrt{1-K^2/4}$')
ax.plot(Ks_, bn, 'ro', ms=7, label='spectral NLS (measured)')
ax.set_xlabel('perturbation wavenumber K'); ax.set_ylabel('growth rate b')
ax.set_title('Modulational instability dispersion, focusing NLS (unit background)')
ax.legend(); fig.tight_layout()
fig.savefig('mi_dispersion.png', dpi=130)
print("saved mi_dispersion.png")
