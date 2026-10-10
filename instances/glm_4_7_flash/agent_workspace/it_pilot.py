"""
DISCOVERY 029 PILOT: Integrable turbulence in the focusing NLS.
Seeding: plane wave + small random noise -> MI cascade -> turbulent field.
Question: statistics of max |psi|^2. Do events exceed the Peregrine bound 9?
Pilot: 1 realization, moderate grid, verify pipeline + timing.
"""
import numpy as np
import json, time

matplotlib_ok = True
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
except Exception:
    matplotlib_ok = False

# ---------------- parameters ----------------
N  = 512
L  = 100.0            # domain [0, L)
dx = L / N
dt = 1e-3
T  = 60.0
nsteps = int(T / dt)
eps = 0.1             # noise amplitude on top of unit background

x  = np.arange(N) * dx
k  = 2.0 * np.pi * np.fft.fftfreq(N, d=dx)
K2 = k * k

def split_step(psi, dt):
    """2nd-order symmetric split-step for i psi_t + psi_xx + 2|psi|^2 psi = 0."""
    # half linear: exp(-i k^2 dt/2)  (since i psi_t = -psi_xx => psi ~ exp(i k^2 t) in linear part? careful)
    # Linear: i psi_t + psi_xx = 0 => psi_t = i psi_xx => psi(k,t) = psi(k,0) e^{-i k^2 t}
    psi = np.fft.ifft(np.exp(-1j * K2 * dt / 2) * np.fft.fft(psi))
    # full nonlinear: i psi_t + 2|psi|^2 psi = 0 => psi_t = 2i |psi|^2 psi => psi = psi exp(i 2|psi|^2 dt)
    a2 = np.abs(psi)**2
    psi = psi * np.exp(1j * 2.0 * a2 * dt)
    # half linear
    psi = np.fft.ifft(np.exp(-1j * K2 * dt / 2) * np.fft.fft(psi))
    return psi

rng = np.random.default_rng(42)
psi = np.ones(N, dtype=complex)
psi += eps * (rng.standard_normal(N) + 1j * rng.standard_normal(N)) / np.sqrt(2)

t0 = time.time()
maxI_track = []
kurt_track  = []
sample_every = 100
kymo = np.zeros((nsteps // 200 + 1, N))
ki = 0
for n in range(1, nsteps + 1):
    psi = split_step(psi, dt)
    if n % sample_every == 0:
        I = np.abs(psi)**2
        maxI_track.append(I.max())
        m2 = np.mean(I**2); m1 = np.mean(I)
        kurt_track.append(m2 / (m1**2))   # kurtosis of intensity (Gaussian field -> 2)
    if n % 200 == 0:
        kymo[ki] = np.abs(psi)**2; ki += 1

elapsed = time.time() - t0
print(f"pilot done: {nsteps} steps in {elapsed:.1f}s ({nsteps/elapsed:.0f} steps/s)")
maxI = np.array(maxI_track)
print(f"max |psi|^2 overall (t<{T}): {maxI.max():.3f}")
print(f"events > 9 (Peregrine bound): {(maxI > 9).sum()} of {len(maxI)} samples")
print(f"kurtosis: start {kurt_track[0]:.2f} -> max {max(kurt_track):.2f} -> end {kurt_track[-1]:.2f}")

if matplotlib_ok:
    tt = np.arange(len(maxI_track)) * sample_every * dt
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    ax = axes[0,0]
    ax.plot(tt, maxI, lw=0.8)
    ax.axhline(9, color='r', ls='--', label='Peregrine bound (9)')
    ax.axhline(4, color='gray', ls=':', label='Kuznetsov-Ma typical (~4)')
    ax.set_xlabel('t'); ax.set_ylabel(r'max$_x\,|\psi|^2$'); ax.legend()
    ax.set_title('Pilot: peak intensity vs time (1 realization)')
    ax = axes[0,1]
    ax.plot(tt, kurt_track, lw=0.8)
    ax.axhline(2, color='k', ls='--', label='Gaussian value 2')
    ax.set_xlabel('t'); ax.set_ylabel('kurtosis of |psi|^2')
    ax.set_title('Intermittency: kurtosis evolution'); ax.legend()
    ax = axes[1,0]
    ax.imshow(kymo[:ki], aspect='auto', origin='lower', cmap='inferno',
              extent=[0, L, 0, T])
    ax.set_xlabel('x'); ax.set_ylabel('t'); ax.set_title('|psi|^2 kymograph')
    ax = axes[1,1]
    ax.hist(np.log10(maxI[tt > 30]), bins=40, color='steelblue')
    ax.set_xlabel(r'log$_{10}$ max$|\psi|^2$ (post-saturation)'); ax.set_ylabel('count')
    ax.set_title('Peak intensity distribution (post-saturation samples)')
    plt.tight_layout(); plt.savefig('it_pilot.png', dpi=110)
    print("saved it_pilot.png")
json.dump({'maxI': maxI.tolist(), 'kurt': kurt_track, 'elapsed_s': elapsed},
          open('it_pilot.json','w'))
