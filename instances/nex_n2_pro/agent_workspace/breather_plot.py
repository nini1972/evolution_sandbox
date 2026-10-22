import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

N = 32
def step(x, r, eps):
    fx = r * x * (1.0 - x)
    return (1.0 - eps) * fx + 0.5 * eps * (np.roll(fx, 1) + np.roll(fx, -1))

np.random.seed(42)
x = np.random.rand(N)
r, eps = 3.88, 0.14   # float-P4 & shadow-P2 breather
for _ in range(400):
    x = step(x, r, eps)

T = 64
traj = np.zeros((T, N))
traj[0] = x
for t in range(1, T):
    x = step(x, r, eps)
    traj[t] = x

even = traj[:, 0::2].mean(1)
odd  = traj[:, 1::2].mean(1)
gap  = np.abs(even - odd)

# single-site orbits of a few representative sites
fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
ax = axes[0]
for s in [0, 1, 2, 3, 5, 8, 13, 17]:
    ax.plot(np.arange(T), traj[:, s], lw=1.0, label=f'site {s}')
ax.set_title('CML logistic lattice N=32, r=3.88, eps=0.14 — site orbits (float-P4 breather)')
ax.set_ylabel('x_i'); ax.legend(ncol=4, fontsize=8); ax.grid(alpha=0.3)

ax = axes[1]
ax.plot(even, label='even-site mean', lw=1.5)
ax.plot(odd, label='odd-site mean', lw=1.5)
ax.set_ylabel('mean value')
ax.set_xlabel('time')
ax.set_title('Antiphase breathing: even vs odd sublattice means (symbolic shadow folds to P2)')
ax.legend(); ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('breather_antiphase.png', dpi=120)
print('saved breather_antiphase.png')

# amplitude decomposition: how much of the P4 motion is antiphase (2-mode) vs genuine 4-mode?
sig = traj - traj.mean(0, keepdims=True)
F = np.fft.rfft(sig, axis=0)
powf = np.abs(F)**2
# Fourier in time: mode 0 (dc), mode 1, mode 2, mode 4
amodes = [0, 1, 2, 3, 4]
fr = powf[amodes, :].sum(1)
print('time-Fourier power (mode 0..4):', dict(zip(amodes, [round(float(fr[i]),1) for i in range(len(amodes))])))
total = fr.sum()
print(f'fraction of oscillatory power in antiphase mode-2: {fr[2]/(fr[1]+fr[2]+fr[3]+fr[4]):.2f}')
np.save('breather_traj.npy', traj)
